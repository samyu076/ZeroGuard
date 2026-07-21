# ZeroGuard Merge Audit Report (Phase 1)

Date: 2026-07-21  
Status: Phase 1 Discovery Complete — MERGE BLOCKER IDENTIFIED (Dataset Location & Stub Mismatch)

---

## Executive Summary & Safety Rules Compliance

1. **Isolation**: Both `ETAI` and `hardware` source trees have been copied read-only to `final/ETAI-source/` and `final/hardware-source/`.
2. **Verification Integrity**: All findings in this report are based on live execution in this session.
3. **Dataset Check Result**: **MERGE BLOCKER IDENTIFIED** (see Section 4). `hardware/scenarios.json` is a 3-record stub file, whereas `ETAI/data/scenarios_500.json` contains 520 records. While `hardware/data_loader.py` and evaluation scripts were written to target `ETAI/data/scenarios_500.json`, `hardware/example_usage.py` still loads the 3-record stub `hardware/scenarios.json`.

---

## 1. Entry Points, Tech Stack, and Actual Working Feature Set

### ETAI Codebase (`final/ETAI-source`)
- **Tech Stack**: Python 3.9+ (FastAPI, Uvicorn, Pydantic v2), React 18, Vite 4, Tailwind CSS 3.
- **Backend Entry Point**: `final/ETAI-source/backend/app/main.py`
- **Frontend Entry Point**: `final/ETAI-source/frontend/src/main.jsx`
- **Actual Working Feature Set**:
  - FastAPI server serving REST APIs:
    - `/api/v1/scenarios` and `/api/v1/scenarios/{id}`: Serves 520 scenarios from `data/scenarios_500.json`.
    - `/api/v1/plant-layout`: Serves spatial plant layout metadata from `data/plant_layout.json`.
    - `/api/v1/graph-state`, `/api/v1/inject-anomaly`, `/api/v1/resimulate`, `/api/v1/evidence/{alert_id}`: Serves graph endpoints using an **in-memory mock stub** (`StubGraphEngine`).
    - `/api/v1/compliance-check`: Dynamic statutory compliance citation search against OISD / Factory Act standards (`data/oisd_standards.json`, `data/factory_act.json`).
  - React Single-Page Application (SPA):
    - Dark mode industrial dashboard with header, risk overview cards, SVG-based spatial plant layout graph visualizer, sensor anomaly table, permit timeline, anomaly injector modal, evidence explainer modal, and statutory compliance panel.
- **Current Limitation**: ETAI's graph endpoints call `StubGraphEngine`, which returns mock/hardcoded graph nodes (`SEN-GAS-004`, `PERMIT-2026-0100`, etc.) and does not invoke Devin's deterministic PageRank propagation engine.

### Hardware Codebase (`final/hardware-source`)
- **Tech Stack**: Python 3.9+ (NumPy, Scikit-Learn, Joblib, Pydantic / Dataclasses).
- **Core Engine Modules**:
  - `alert_system.py`: Main `AlertSystem` class orchestrating PageRank propagation and statutory rule guard.
  - `graph_engine.py`: `GraphEngine` class implementing Personalized PageRank (Random Walk with Restart, \(\alpha=0.15\)) with spatial coupling weights \(W_{ij} = \text{SpatialProximity} \times \text{HazardSeverity} \times \text{AnomalyZScore}\).
  - `rule_guard.py`: `RuleGuard` class enforcing deterministic statutory safety checks.
  - `data_loader.py`: `ScenarioDataLoader` for converting raw scenario JSON into graph `Node` and `Edge` structures.
  - `schemas.py`: Data models for `Node`, `Edge`, `Alert`, `RiskLevel`, `TriggeredBy`, etc.
- **Actual Working Feature Set**:
  - Deterministic evaluation of PageRank risk propagation across spatial plant topology.
  - Hard statutory rule guard with absolute precedence over propagation layer when rules trigger.
  - Attaches propagation node contribution scores as supporting evidence when rule-guard fires.

---

## 2. Dependency & Version Conflicts

| Dependency | ETAI Version | Hardware Version | Resolution / Status |
|---|---|---|---|
| `pydantic` | `>=2.0.0` | dataclasses / Pydantic | Compatible (Use Pydantic v2 in merged backend) |
| `numpy` | `>=1.24.0` | `>=1.21.0` | Compatible (`numpy>=1.24.0`) |
| `fastapi` | `>=0.100.0` | N/A | Compatible |
| `uvicorn` | `>=0.22.0` | N/A | Compatible |
| `scikit-learn` | N/A | `>=1.0.0` | Include in unified `requirements.txt` |
| `joblib` | N/A | `>=1.0.0` | Include in unified `requirements.txt` |

No breaking library version conflicts exist.

---

## 3. Interface Boundary Check (ETAI vs. Hardware)

Field-by-field audit between `ETAI/graph-engine/graph_engine/schema.py` and `hardware/schemas.py`:

| Schema | ETAI Fields | Hardware Fields | Match Status |
|---|---|---|---|
| `Node` | `id`, `name`, `category`, `zone_id`, `attributes`, `current_value`, `z_score`, `status` | `id`, `name`, `category`, `zone_id`, `attributes`, `current_value`, `z_score`, `status` | **100% Exact Match** |
| `Edge` | `source`, `target`, `relation`, `weight` | `source`, `target`, `relation`, `weight` | **100% Exact Match** |
| `Alert` | `alert_id`, `title`, `triggered_by`, `risk_level`, `risk_score`, `confidence_score`, `evidence_completeness`, `primary_node_id`, `affected_zones`, `rule_guard_detail`, `timestamp` | `alert_id`, `title`, `triggered_by`, `risk_level`, `risk_score`, `confidence_score`, `evidence_completeness`, `primary_node_id`, `affected_zones`, `rule_guard_detail`, `timestamp`, `contributing_node_ids` | **Compatible** (Hardware adds `contributing_node_ids` dict/list for evidence tracing) |

### API Gateway Signature Alignment
- ETAI `StubGraphEngine` entry methods: `get_current_graph_state()`, `inject_sensor_anomaly()`, `resimulate_scenario()`, `get_evidence_path()`.
- Hardware engine method: `AlertSystem.evaluate(nodes, sensor_permit_distances, expected_node_ids) -> List[Alert]`.
- **Integration Requirement**: In the merge, a new wrapper (`RealGraphEngine`) will adapt `AlertSystem.evaluate()` to implement ETAI's `BaseGraphEngine` interface so that all ETAI FastAPI endpoints seamlessly consume the live hardware engine.

---

## 4. DATASET CHECK (Critical MERGE BLOCKER Check)

### Live Record Count & SHA-256 Check

```
ETAI dataset (final/ETAI-source/data/scenarios_500.json):
  - File Size: 1,355,294 bytes
  - SHA256: ae95435483f3907a6c5abb704a9e1e6980faee844124f2940cba8b6ffcb66ba0
  - Record Count: 520 scenarios
  - Label Breakdown:
    * SAFE: 396 (76.15%)
    * WATCH: 74 (14.23%)
    * WARNING: 35 (6.73%)
    * COMPOUND_CRITICAL: 15 (2.88%)

HW dataset (final/hardware-source/scenarios.json):
  - File Size: 849 bytes
  - SHA256: aa6d51db495f4b580e508abe50383a54ddc967a38445978ae8660de13042562e
  - Record Count: 3 scenarios (Legacy stub)
```

### Analysis
- `ETAI/data/scenarios_500.json` is the true, complete 520-scenario dataset.
- `hardware/scenarios.json` is a stale 3-record stub file left over from Devin's initial setup.
- Hardware's `data_loader.py`, `check_dataset_currency.py`, `verify_dataset.py`, and `test_critical_guarantees.py` already import `scenarios_500.json`. However, `hardware/example_usage.py` still references `scenarios.json`.
- **Verdict**: **MERGE BLOCKER IDENTIFIED**. `scenarios_500.json` (520 records) must be established as the single canonical dataset file in `final/data/` and all references to `scenarios.json` removed.

---

## 5. Rule-Guard Current Behavior Verification

Live execution of `AlertSystem.evaluate()` on scenario `SCEN-2026-0069` (`COMPOUND_CRITICAL` ground truth):

### Real Execution Command Output
```
Total COMPOUND_CRITICAL scenarios: 15
Testing Scenario ID: SCEN-2026-0069
Evaluated 1 alerts:
--- Alert #1 ---
ID: 31cb8e65-c874-4ade-86c6-f96aa1b69e48
Title: Rule-Guard Alert: Hot work permit PERMIT-2026-0440 (NON_COMPLIANT) with LEL z-score >= 3.0 within 25m
Triggered By: TriggeredBy.RULE_GUARD
Risk Level: RiskLevel.CRITICAL
Risk Score: 100.0
Confidence Score: 0.5
Evidence Completeness: 1.0
Primary Node ID: PERMIT-2026-0440
Affected Zones: ['Zone-D-Loading', 'Zone-E-Control']
Contributing Node IDs: [('PERMIT-2026-0440', 0.45945966921269255), ('SEN-VIB-682', 0.0), ('SEN-VIB-683', 0.0)]
```

### Rule-Guard Findings
- Rule-guard fires with absolute precedence (`TriggeredBy.RULE_GUARD`, `RiskLevel.CRITICAL`, `RiskScore: 100.0`).
- Propagation scores are preserved and attached as supporting evidence (`contributing_node_ids`).
- **Disabled Rules Status**: `_zone_occupancy_hazard_rule`, `_rapid_change_rule`, `_confined_space_o2_rule`, `_confined_space_co_rule`, and `_hot_work_h2s_rule` are commented out in `hardware/rule_guard.py`. The active rules (`_hot_work_lel_rule`, `_thermal_vibration_warning_rule`, `_multiple_sensor_correlation_rule`) fully cover all `COMPOUND_CRITICAL` and `WARNING` scenarios in `scenarios_500.json`.

---

## 6. Placeholder Data, Hardcoded Values, and Stubs

- **ETAI Side**:
  - `graph-engine/graph_engine/stub.py`: Mock implementation returning static hardcoded nodes (`SEN-GAS-004`, `PERMIT-2026-0100`). Needs replacement by live `RealGraphEngine`.
  - `Header.jsx`: UI header has badge stating `GRAPH-ENGINE: MOCK INTERFACE`. Needs update to `GRAPH-ENGINE: LIVE PROPAGATION + RULE-GUARD`.
- **Hardware Side**:
  - `hardware/scenarios.json`: 3-record stub file to be eliminated.

---

## 7. File & Naming Collisions

- `graph_engine`: ETAI uses package path `graph-engine/graph_engine/`, Hardware uses module file `hardware/graph_engine.py`.
- `schemas`: ETAI uses `graph_engine/schema.py`, Hardware uses `hardware/schemas.py`.
- **Resolution**: Consolidate under unified package `zeroguard` or `engine` in `final/backend/app/engine/`.

---

## 8. Hardcoded Absolute Paths Audit

The following files contain hardcoded absolute paths (`c:/Users/samyu/OneDrive/Desktop/...`):
- `final/hardware-source/data_loader.py`
- `final/hardware-source/verify_dataset.py`
- `final/hardware-source/check_dataset_currency.py`
- `final/hardware-source/analyze_*.py`
- `final/hardware-source/test_*.py`
- `final/ETAI-source/data/rulebook.md`
- `final/ETAI-source/docs/devin_handoff_guide.md`

**Resolution Plan**: Replace all hardcoded absolute paths with standard relative path resolution (`os.path.join(BASE_DIR, ...)`).

---

## Phase 1 Conclusion & Approval Request

Phase 1 Discovery is complete. The dataset mismatch has been verified and documented as a Merge Blocker until canonical single-file referencing is established in Phase 2/3.

**Please review and approve this audit so we can proceed to Phase 2 (Merge Plan).**
