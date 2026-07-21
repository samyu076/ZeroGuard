import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.api.router import api_router
print("Router OK")
for r in api_router.routes:
    print(" ", getattr(r, 'methods', ''), getattr(r, 'path', ''))
