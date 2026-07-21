"""
Test CRITICAL #2 fix: PageRank normalization for dangling nodes.
Verify that nodes with zero valid spatial proximity do NOT get uniform distribution.
"""

from schemas import Node, NodeCategory
from graph_engine import GraphEngine
import numpy as np

def test_dangling_node_normalization():
    """
    Create a node with zero valid spatial proximity to anything else.
    Verify the adjacency row is NOT uniform (should remain zero).
    """
    print("=" * 70)
    print("TEST: Dangling node normalization fix")
    print("=" * 70)
    
    # Create nodes: one isolated node (no distances to others)
    nodes = [
        Node(
            id="isolated_node",
            name="Isolated Node",
            category=NodeCategory.SENSOR,
            zone_id="zone_1",
            attributes={"x": 0, "y": 0},
            current_value=5.0,
            z_score=0.5,
            status="NORMAL"
        ),
        Node(
            id="connected_node_1",
            name="Connected Node 1",
            category=NodeCategory.SENSOR,
            zone_id="zone_1",
            attributes={"x": 10, "y": 10},
            current_value=6.0,
            z_score=0.5,
            status="NORMAL"
        ),
        Node(
            id="connected_node_2",
            name="Connected Node 2",
            category=NodeCategory.SENSOR,
            zone_id="zone_1",
            attributes={"x": 20, "y": 20},
            current_value=7.0,
            z_score=0.5,
            status="NORMAL"
        )
    ]
    
    # Only provide distances for connected nodes, NOT for isolated node
    distances = {
        ("connected_node_1", "connected_node_2"): 14.14,  # sqrt(10^2 + 10^2)
        ("connected_node_2", "connected_node_1"): 14.14
    }
    
    graph = GraphEngine()
    graph.set_nodes(nodes)
    graph.set_sensor_permit_distances(distances)
    
    # Build adjacency matrix
    current_anomalies = {node.id: node.z_score for node in nodes if node.z_score}
    adjacency_matrix, confidence = graph.build_adjacency_matrix(current_anomalies)
    
    print(f"\nAdjacency matrix shape: {adjacency_matrix.shape}")
    print(f"Confidence score: {confidence}")
    
    # Get the row for the isolated node
    isolated_idx = graph.node_id_to_index["isolated_node"]
    isolated_row = adjacency_matrix[isolated_idx]
    
    print(f"\nIsolated node row (index {isolated_idx}):")
    print(f"  {isolated_row}")
    print(f"  Row sum: {isolated_row.sum()}")
    print(f"  Is all zeros: {np.all(isolated_row == 0)}")
    
    # Verify the row is NOT uniform (should be all zeros)
    if np.all(isolated_row == 0):
        print("\n✓ PASS: Isolated node row is all zeros (NOT uniform)")
        print("✓ PASS: Dangling node handled correctly")
        return True
    else:
        print("\n✗ FAIL: Isolated node row is NOT all zeros")
        print(f"✗ FAIL: Row values: {isolated_row}")
        return False

if __name__ == "__main__":
    success = test_dangling_node_normalization()
    exit(0 if success else 1)
