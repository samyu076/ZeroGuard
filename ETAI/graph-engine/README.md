# ZeroGuard Graph Engine Interface & Stub Module

> **WARNING: DO NOT EDIT INTERNAL ENGINE LOGIC HERE**
> This directory (`graph-engine`) is an isolated module containing ONLY the input/output schemas and stubbed interfaces for ZeroGuard.
> The actual Graph Engine implementation is spec'd and built separately in Devin against `docs/api-contract.md`.

## Structure
- `graph_engine/schema.py`: Frozen Pydantic models matching `docs/api-contract.md`.
- `graph_engine/interfaces.py`: Abstract Protocol base class (`BaseGraphEngine`).
- `graph_engine/stub.py`: Mock implementation returning sample industrial risk graphs, rule-guard violations, and evidence paths.
