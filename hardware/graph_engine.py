"""
Core graph engine implementing deterministic Spatio-Temporal Weighted Propagation.
Edge weight formula: W_ij(t) = SpatialProximity(i,j) × HazardSeverity(i) × AnomalyZScore(j)
Uses precomputed distance_meters from sensor_permit_distances[] for spatial proximity.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from schemas import Node, Edge, NodeCategory


class GraphEngine:
    """
    Deterministic graph engine for spatio-temporal weighted propagation.
    Uses precomputed distances from scenario data for spatial proximity.
    """
    
    def __init__(self, restart_probability: float = 0.15):
        self.nodes: Dict[str, Node] = {}
        self.adjacency_matrix: Optional[np.ndarray] = None
        self.node_id_to_index: Dict[str, int] = {}
        self.index_to_node_id: Dict[int, str] = {}
        self.restart_probability = restart_probability  # For Random Walk with Restart
        self.edge_weights: Dict[Tuple[str, str], float] = {}
        self.sensor_permit_distances: Dict[Tuple[str, str], float] = {}  # Precomputed distances
        
    def set_nodes(self, nodes: List[Node]) -> None:
        """Set all nodes in the graph and clear all derived state."""
        self.nodes = {node.id: node for node in nodes}
        # Clear all derived state to prevent state leak between evaluations
        self.adjacency_matrix = None
        self.edge_weights.clear()
        self._rebuild_index_mapping()
        
    def set_sensor_permit_distances(self, distances: Dict[Tuple[str, str], float]) -> None:
        """
        Set precomputed sensor-permit distances from scenario data.
        
        Args:
            distances: Dictionary mapping (sensor_id, permit_id) -> distance_meters
        """
        self.sensor_permit_distances = distances
        
    def _rebuild_index_mapping(self) -> None:
        """Rebuild the mapping between node IDs and matrix indices."""
        self.node_id_to_index = {node_id: idx for idx, node_id in enumerate(self.nodes.keys())}
        self.index_to_node_id = {idx: node_id for node_id, idx in self.node_id_to_index.items()}
        
    def calculate_spatial_proximity(self, 
                                   node_i_id: str,
                                   node_j_id: str) -> Optional[float]:
        """
        Calculate spatial proximity using precomputed distance_meters.
        
        Formula: 1 / (1 + distance_meters)
        
        Args:
            node_i_id: Source node ID
            node_j_id: Target node ID
            
        Returns:
            Spatial proximity score (0 to 1), or None if distance not available
        """
        # Check if we have precomputed distance for this pair
        key = (node_i_id, node_j_id)
        reverse_key = (node_j_id, node_i_id)
        
        if key in self.sensor_permit_distances:
            distance = self.sensor_permit_distances[key]
            if not np.isfinite(distance):
                return 0.0  # Invalid distance
            return 1.0 / (1.0 + distance)
        elif reverse_key in self.sensor_permit_distances:
            distance = self.sensor_permit_distances[reverse_key]
            if not np.isfinite(distance):
                return 0.0  # Invalid distance
            return 1.0 / (1.0 + distance)
        
        # No fallback - if distance is not precomputed, return None
        # This ensures dangling nodes (nodes without distance data) are handled correctly
        return None  # Distance undefined
    
    def calculate_edge_weight(self,
                             node_i_id: str,
                             node_j_id: str,
                             anomaly_z_score_j: float = 0.0) -> Tuple[float, bool]:
        """
        Calculate edge weight using the deterministic formula:
        W_ij(t) = SpatialProximity(i,j) × HazardSeverity(i) × AnomalyZScore(j)
        
        Args:
            node_i_id: Source node ID
            node_j_id: Target node ID
            anomaly_z_score_j: Anomaly z-score for target node (if sensor)
            
        Returns:
            Tuple of (edge_weight, confidence_valid)
            confidence_valid is False if spatial proximity was undefined
        """
        spatial_proximity = self.calculate_spatial_proximity(node_i_id, node_j_id)
        
        if spatial_proximity is None:
            return 0.0, False  # Undefined proximity -> low confidence
        
        node_i = self.nodes.get(node_i_id)
        if not node_i:
            return 0.0, False
        
        # Get hazard severity from attributes or use default
        hazard_severity = node_i.attributes.get("hazard_severity", 1.0)
        
        # Get anomaly score for target node
        node_j = self.nodes.get(node_j_id)
        if node_j and node_j.category == NodeCategory.SENSOR:
            anomaly_score = abs(anomaly_z_score_j) if anomaly_z_score_j else abs(node_j.z_score or 0)
        else:
            anomaly_score = 1.0
            
        weight = spatial_proximity * hazard_severity * anomaly_score
        # Clip weight to [0, 1] to prevent unbounded values
        weight = max(0.0, min(weight, 1.0))
        return weight, True
    
    def build_adjacency_matrix(self, 
                              current_anomalies: Dict[str, float]) -> Tuple[np.ndarray, float]:
        """
        Build the adjacency matrix with current edge weights.
        
        Args:
            current_anomalies: Mapping of sensor_id -> anomaly_z_score
            
        Returns:
            Tuple of (adjacency_matrix, confidence_score)
            confidence_score is fraction of edges with valid spatial data
        """
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
                
                # Get anomaly score for target node if it's a sensor
                anomaly_score_j = current_anomalies.get(node_id_j, 0.0)
                
                weight, is_valid = self.calculate_edge_weight(node_id_i, node_id_j, anomaly_score_j)
                self.adjacency_matrix[i, j] = weight
                self.edge_weights[(node_id_i, node_id_j)] = weight
                
                if is_valid:
                    valid_edges += 1
        
        # Calculate confidence score based on valid edges
        confidence_score = valid_edges / total_edges if total_edges > 0 else 1.0
        
        # Row-normalize to create stochastic matrix for PageRank
        # Proper handling of dangling nodes: rows with zero sums remain zero
        # The restart probability in PageRank will handle dangling nodes
        row_sums = self.adjacency_matrix.sum(axis=1)
        
        # Only normalize rows that have non-zero sums
        # Dangling nodes (row_sum = 0) remain as zero rows
        nonzero_rows = row_sums > 0
        self.adjacency_matrix[nonzero_rows] = self.adjacency_matrix[nonzero_rows] / row_sums[nonzero_rows, np.newaxis]
        
        return self.adjacency_matrix, confidence_score
    
    def personalized_pagerank(self,
                            seed_nodes: List[str],
                            num_iterations: int = 100,
                            tolerance: float = 1e-6) -> Dict[str, float]:
        """
        Compute Personalized PageRank (Random Walk with Restart) from seed nodes.
        
        Args:
            seed_nodes: List of starting node IDs for the random walk
            num_iterations: Maximum number of iterations
            tolerance: Convergence tolerance
            
        Returns:
            Dictionary mapping node_id -> PageRank score
        """
        if self.adjacency_matrix is None or len(self.nodes) == 0:
            return {}
            
        n = len(self.nodes)
        
        # Create personalization vector (uniform over seed nodes)
        personalization = np.zeros(n)
        seed_indices = [self.node_id_to_index[sid] for sid in seed_nodes if sid in self.node_id_to_index]
        
        if seed_indices:
            personalization[seed_indices] = 1.0 / len(seed_indices)
        else:
            personalization[:] = 1.0 / n  # Uniform if no valid seeds
        
        # Initialize PageRank vector
        pagerank = np.ones(n) / n
        
        # Power iteration with restart
        for iteration in range(num_iterations):
            prev_pagerank = pagerank.copy()
            
            # PR = (1 - alpha) * M * PR + alpha * personalization
            pagerank = (1 - self.restart_probability) * self.adjacency_matrix.T @ pagerank + \
                       self.restart_probability * personalization
            
            # Check convergence
            if np.linalg.norm(pagerank - prev_pagerank, 1) < tolerance:
                break
        
        # Convert to dictionary
        result = {}
        for node_id, idx in self.node_id_to_index.items():
            result[node_id] = pagerank[idx]
            
        return result
    
    def get_contributing_weights(self, 
                                target_node_id: str,
                                pagerank_scores: Dict[str, float]) -> List[Tuple[str, float]]:
        """
        Get the contributing nodes and their individual weights for a target node.
        
        Args:
            target_node_id: Node to analyze
            pagerank_scores: PageRank scores from propagation
            
        Returns:
            List of (node_id, weight) tuples sorted by weight descending
        """
        if target_node_id not in self.node_id_to_index:
            return []
            
        contributions = []
        
        for node_id in self.nodes.keys():
            if node_id == target_node_id:
                continue
                
            # Get the edge weight from this node to target
            edge_weight = self.edge_weights.get((node_id, target_node_id), 0.0)
            pagerank_score = pagerank_scores.get(node_id, 0.0)
            
            # Combined contribution: edge weight * pagerank score
            contribution = edge_weight * pagerank_score
            contributions.append((node_id, contribution))
        
        # Sort by contribution descending
        contributions.sort(key=lambda x: x[1], reverse=True)
        return contributions
    
    def compute_risk_score(self, 
                          seed_nodes: List[str],
                          current_anomalies: Dict[str, float]) -> Tuple[Dict[str, float], Dict[str, List[Tuple[str, float]]], float]:
        """
        Compute risk scores for all nodes via propagation.
        
        Args:
            seed_nodes: Nodes with initial anomalous signals
            current_anomalies: Current anomaly z-scores for sensors
            
        Returns:
            Tuple of (pagerank_scores, contributing_weights_dict, confidence_score)
        """
        # Build adjacency matrix with current edge weights
        self.build_adjacency_matrix(current_anomalies)
        
        # Run Personalized PageRank
        pagerank_scores = self.personalized_pagerank(seed_nodes)
        
        # Get contributing weights for each node
        contributing_weights = {}
        for node_id in self.nodes.keys():
            contributing_weights[node_id] = self.get_contributing_weights(node_id, pagerank_scores)
        
        # Calculate confidence score
        _, confidence_score = self.build_adjacency_matrix(current_anomalies)
        
        return pagerank_scores, contributing_weights, confidence_score
