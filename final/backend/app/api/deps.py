"""
ZeroGuard API Dependency Injection
Provides shared singleton RealGraphEngine state.
"""

import os
from app.engine.real_engine import RealGraphEngine

# BASE_DIR = final/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DATA_DIR = os.path.join(BASE_DIR, "data")

_shared_graph_engine: RealGraphEngine = None

def get_graph_engine() -> RealGraphEngine:
    global _shared_graph_engine
    if _shared_graph_engine is None:
        _shared_graph_engine = RealGraphEngine(data_dir=DATA_DIR)
    return _shared_graph_engine
