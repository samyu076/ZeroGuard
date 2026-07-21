"""
ZeroGuard Graph Engine
Implements deterministic Spatio-Temporal Weighted Propagation graph engine using
Personalized PageRank (Random Walk with Restart) with spatial coupling weights:
W_ij = SpatialProximity(i,j) * HazardSeverity(i) * AnomalyZScore(j)
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from app.engine.schema import Node, Edge, NodeCategory, RiskLevel


class GraphEngine:
    def __init__(self, restart_probability: float = 0.15):
        self.restart_probability = restart_probability
        self.nodes: Dict[str, Node] = {}
        self.node_id_to_index: Dict[str, int] = {}
        self.index_to_node_id: Dict[int, str] = {}
        self.sensor_permit_distances: Dict[tuple, float] = {}
        self.adjacency_matrix: Optional[np.ndarray] = None
        self.edge_weights: Dict[tuple, float] = {}

    def set_nodes(self, nodes: List[Node]) -> None:
        self.nodes = {node.id: node for node in nodes}
        self.node_id_to_index = {node.id: i for i, node in enumerate(nodes)}
        self.index_to_node_id = {i: node.id for i, node in enumerate(nodes)}
        self.adjacency_matrix = None
        self.edge_weights = {}

    def set_sensor_permit_distances(self, distances: Dict[tuple, float]) -> None:
        self.sensor_permit_distances = distances

    def calculate_spatial_proximity(self, node_i_id: str, node_j_id: str) -> Tuple[float, bool]:
        distance = self.sensor_permit_distances.get((node_i_id, node_j_id))
        if distance is None:
            distance = self.sensor_permit_distances.get((node_j_id, node_i_id))

        if distance is not None:
            max_distance = 35.0
            proximity = max(0.0, 1.0 - (distance / max_distance))
            return proximity, True

        node_i = self.nodes.get(node_i_id)
        node_j = self.nodes.get(node_j_id)
        if node_i and node_j:
            pos_i = (node_i.attributes.get("x"), node_i.attributes.get("y"))
            pos_j = (node_j.attributes.get("x"), node_j.attributes.get("y"))
            if all(v is not None for v in pos_i + pos_j):
                dist = float(np.sqrt((pos_i[0] - pos_j[0])**2 + (pos_i[1] - pos_j[1])**2))
                max_dist = 35.0
                return max(0.0, 1.0 - (dist / max_dist)), True

        return 0.5, False

    def calculate_edge_weight(self, node_i_id: str, node_j_id: str, anomaly_z_score_j: Optional[float] = None) -> Tuple[float, bool]:
        spatial_proximity, is_valid = self.calculate_spatial_proximity(node_i_id, node_j_id)
        node_i = self.nodes.get(node_i_id)
        if not node_i:
            return 0.0, False

        hazard_severity = float(node_i.attributes.get("hazard_severity", 1.0))
        node_j = self.nodes.get(node_j_id)
        if node_j and node_j.category == NodeCategory.SENSOR:
            anomaly_score = abs(anomaly_z_score_j) if anomaly_z_score_j is not None else abs(node_j.z_score or 0)
        else:
            anomaly_score = 1.0

        weight = spatial_proximity * hazard_severity * anomaly_score
        weight = max(0.0, min(weight, 1.0))
        return weight, True

    def build_adjacency_matrix(self, current_anomalies: Dict[str, float]) -> Tuple[np.ndarray, float]:
        n = len(self.nodes)
        if n == 0:
            return np.array([]), 1.0

        self.adjacency_matrix = np.zeros((n, n))
        self.edge_weights = {}

        node_ids = list(self.nodes.keys())
        valid_edges = 0
        total_edges = 0

        for i, node_id_i in enumerate(node_ids):
            for j, node_id_j in enumerate(node_ids):
                if i == j:
                    continue
                total_edges += 1
                anomaly_score_j = current_anomalies.get(node_id_j, 0.0)
                weight, is_valid = self.calculate_edge_weight(node_id_i, node_id_j, anomaly_score_j)
                self.adjacency_matrix[i, j] = weight
                self.edge_weights[(node_id_i, node_id_j)] = weight
                if is_valid:
                    valid_edges += 1

        confidence_score = valid_edges / total_edges if total_edges > 0 else 1.0

        row_sums = self.adjacency_matrix.sum(axis=1)
        nonzero_rows = row_sums > 0
        self.adjacency_matrix[nonzero_rows] = self.adjacency_matrix[nonzero_rows] / row_sums[nonzero_rows, np.newaxis]

        return self.adjacency_matrix, confidence_score

    def personalized_pagerank(self, seed_nodes: List[str], num_iterations: int = 100, tolerance: float = 1e-6) -> Dict[str, float]:
        if self.adjacency_matrix is None or len(self.nodes) == 0:
            return {}

        n = len(self.nodes)
        personalization = np.zeros(n)
        seed_indices = [self.node_id_to_index[sid] for sid in seed_nodes if sid in self.node_id_to_index]

        if seed_indices:
            personalization[seed_indices] = 1.0 / len(seed_indices)
        else:
            personalization[:] = 1.0 / n

        pagerank = np.ones(n) / n

        for iteration in range(num_iterations):
            prev_pagerank = pagerank.copy()
            pagerank = (1 - self.restart_probability) * (self.adjacency_matrix.T @ pagerank) + self.restart_probability * personalization
            if np.linalg.norm(pagerank - prev_pagerank, 1) < tolerance:
                break

        result = {}
        for node_id, idx in self.node_id_to_index.items():
            result[node_id] = float(pagerank[idx])

        return result

    def get_contributing_weights(self, target_node_id: str, pagerank_scores: Dict[str, float]) -> List[Tuple[str, float]]:
        if target_node_id not in self.node_id_to_index:
            return []

        contributions = []
        for node_id in self.nodes.keys():
            if node_id == target_node_id:
                continue
            edge_weight = self.edge_weights.get((node_id, target_node_id), 0.0)
            pagerank_score = pagerank_scores.get(node_id, 0.0)
            contribution = edge_weight * pagerank_score
            contributions.append((node_id, contribution))

        contributions.sort(key=lambda x: x[1], reverse=True)
        return contributions

    def compute_risk_score(self, seed_nodes: List[str], current_anomalies: Dict[str, float]) -> Tuple[Dict[str, float], Dict[str, List[Tuple[str, float]]], float]:
        self.build_adjacency_matrix(current_anomalies)
        pagerank_scores = self.personalized_pagerank(seed_nodes)
        contributing_weights = {}
        for node_id in self.nodes.keys():
            contributing_weights[node_id] = self.get_contributing_weights(node_id, pagerank_scores)
        _, confidence_score = self.build_adjacency_matrix(current_anomalies)
        return pagerank_scores, contributing_weights, confidence_score
