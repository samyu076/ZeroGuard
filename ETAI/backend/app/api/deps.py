import os
from graph_engine.stub import StubGraphEngine

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Shared Singleton Graph Engine Instance across all API routes
_shared_graph_engine = StubGraphEngine(data_dir=DATA_DIR)

def get_graph_engine() -> StubGraphEngine:
    """FastAPI Dependency providing shared singleton Graph Engine instance."""
    return _shared_graph_engine
