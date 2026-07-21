# ZeroGuard — Compound Industrial Risk Intelligence Platform

ZeroGuard is a production-ready Compound Industrial Risk Intelligence platform designed for oil refinery and chemical plant safety. It merges a high-performance Spatio-Temporal PageRank Risk Propagation graph engine with a hard statutory safety Rule-Guard layer to protect against catastrophic compound industrial failures.

---

## Key System Features

1. **Spatio-Temporal Weighted Propagation Graph Engine**:
   - Computes dynamic spatial coupling weights \(W_{ij} = \text{SpatialProximity}(i,j) \times \text{HazardSeverity}(i) \times \text{AnomalyZScore}(j)\) across shared 5-zone spatial plant grid coordinates.
   - Evaluates Personalized PageRank (Random Walk with Restart, \(\alpha=0.15\)) for emergent hazard detection.

2. **Deterministic Statutory Rule-Guard Layer**:
   - Enforces hard regulatory interlocks (OISD-STD-105 Clause 6.2.1, OSHA 29 CFR 1910.252(a)(2), Factory Act 1948 Section 36).
   - **Absolute Precedence**: When a statutory safety violation fires (e.g. active Hot Work + LEL z-score \(\ge 3.0\) within 25 meters), Rule-Guard forces `COMPOUND_CRITICAL` status (risk score 100.0) regardless of propagation confidence, while attaching PageRank propagation node weights as supporting evidence.

3. **Master 520-Scenario Dataset**:
   - `data/scenarios_500.json` contains 520 labeled synthetic operational scenarios matching real-world plant operational rarity:
     - **396 SAFE** (76.15%)
     - **74 WATCH** (14.23%)
     - **35 WARNING** (6.73%)
     - **15 COMPOUND_CRITICAL** (2.88%)

4. **Zero-Hallucination Evidence Explainer**:
   - Deterministically traces contributing sensor reading chains, permit distance matrices, and regulatory citations.

5. **Control-Room Industrial Frontend**:
   - Built with React 18, Vite 4, and Tailwind CSS.
   - Dark charcoal base (`#0B0F17` / `#151D2A`) with monospace font for live telemetry (`font-mono`).
   - Exactly three risk tier accent colors: Red (`#EF4444`) reserved **exclusively** for `COMPOUND_CRITICAL`.
   - SVG spatial zone overlay visualizer with live animated risk path lighting.

---

## Folder Structure

```
final/
├── data/                       # Canonical Data Layer
│   ├── scenarios_500.json      # Master 520-scenario dataset
│   ├── plant_layout.json       # 5-zone spatial layout coordinates
│   ├── oisd_standards.json     # OISD regulatory corpus
│   ├── factory_act.json        # Factory Act statutory text
│   ├── synthetic_permits.json  # Synthetic permit templates
│   └── rulebook.md             # Legally defensible synthetic rulebook
├── backend/                    # FastAPI Backend Gateway
│   ├── requirements.txt        # Unified dependencies
│   ├── test_merged_zeroguard.py# Comprehensive merge verification suite
│   ├── test_live_api_endpoints.py# Live REST API test suite
│   └── app/
│       ├── main.py             # FastAPI entry point (/api/v1)
│       ├── engine/             # Graph & Safety Engine (PageRank + RuleGuard)
│       ├── services/           # REST services (Scenario, Evidence, Compliance)
│       └── api/                # REST endpoints
├── frontend/                   # React Control-Room Dashboard
│   ├── package.json
│   ├── vite.config.js
│   ├── src/
│   │   ├── components/         # Header, GraphVisualizer, Tables, Modals
│   │   └── services/api.js     # Unified /api/v1 REST client
├── MERGE_AUDIT.md              # Phase 1 Discovery Report
└── MERGE_PLAN.md               # Phase 2 Architecture Plan
```

---

## Quick Start & Setup

### 1. Backend Setup (FastAPI + Python 3.9+)

```bash
cd final/backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend will start at `http://localhost:8000`. Swagger API docs available at `http://localhost:8000/docs`.

### 2. Frontend Setup (React + Vite)

```bash
cd final/frontend
npm install
npm run dev
```

Frontend dashboard will open at `http://localhost:3000`.

---

## Verification Test Commands

Run the comprehensive automated test suite to verify 100% pass rate across dataset, rule-guard precedence, dynamic compliance, and API endpoints:

```bash
cd final/backend
python test_merged_zeroguard.py
python test_live_api_endpoints.py
```
