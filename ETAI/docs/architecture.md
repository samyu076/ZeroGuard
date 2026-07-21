# ZeroGuard — System Architecture & Design Specification

## 1. Overview
ZeroGuard is a **Compound Industrial Risk Intelligence platform** designed to monitor high-hazard industrial facilities (refineries, chemical processing plants, offshore platforms). It integrates multivariable sensor streams, work permit logs, shift handovers, and statutory safety standards into a unified risk propagation model.

## 2. Core Architectural Principles

### 2.1 Graph Engine Isolation
The `graph-engine` module is strictly decoupled from the core application backend. It exposes explicit input and output interface contracts (`docs/api-contract.md` and `graph_engine/schema.py`). The graph engine implementation (graph topology algorithms, shortest-path traversals, propagation engines) is developed independently by separate engineering teams (e.g. Devin) against this frozen spec.

### 2.2 Dual-Layer Risk Evaluation Model
ZeroGuard separates risk evaluation into two distinct complementary layers:
1. **Rule-Guard Layer (`triggered_by: "rule_guard"`)**:
   - Deterministic, statutory safety checks.
   - Evaluates explicit violations of regulatory mandates (e.g. OISD-STD-105 Clause 6.2: "Hot Work Permit active in Zone B without blind isolation").
   - Instant response, zero ambiguity, high severity.
2. **Propagation Layer (`triggered_by: "propagation"`)**:
   - Multi-factor spatial/temporal graph propagation engine.
   - Combines sensor z-score drift across linked equipment/zones with permit activities to discover emergent non-obvious compound risks (e.g. Sensor T-201 drift + active maintenance permit + ambient gas elevation -> Hydrocarbon Flaring Risk).

### 2.3 Sensor Stream Windowed Aggregation (2-Second Buckets)
Industrial sensor telemetry (UCI Gas Sensor Array Drift, NASA C-MAPSS turbofan data) operates at 10–100Hz frequencies. To prevent downstream graph solvers and API endpoints from melting under raw sample rates:
- **Preprocessing Pipeline**: The `sensor_anomaly.py` service ingests high-frequency readings and applies a rolling **2-second time-bucket aggregation**.
- **Aggregated Metrics**: Computes `mean`, `max`, and `rate_of_change` (\(\Delta x / \Delta t\)) per sensor per 2-second bucket.
- **Z-Score Calculation**: Calculates rolling z-score \(z = \frac{x_{agg} - \mu_{baseline}}{\sigma_{baseline}}\) per aggregated window.

### 2.4 Evidence Explainer (Deterministic String Templating)
To eliminate LLM hallucination in safety-critical industrial operations, the **Evidence Explainer Service** uses zero generative models. It performs deterministic graph path traversal and converts node/edge chains directly into human-readable evidence strings via predefined string templates:
> `[RuleGuard/Propagation Alert ALT-9021] :: Path: Sensor [GAS-04] (Z=3.85, High Flammable Vapors) ──(MONITORS)──> Zone [HYDROCRACKER-PUMP-ROOM-2] <──(LOCATED_IN)── Permit [HW-2024-09: Hot Welding] ──> Compound Risk: Uncontained Ignition Hazard`

### 2.5 Compliance Citation Service (Exact Passage & Doc ID Matching)
The Compliance Citation Service indexes official statutory text (OISD standards, Factory Act 1948). Every citation returned MUST contain:
- Exact matched passage text.
- Standard Name (e.g., `OISD-STD-105`).
- Section / Clause number (e.g., `Clause 6.2.1`).
- Document Unique Identifier (`DOC-OISD-105-REV3`).

---

## 3. High-Level Data Flow

```
┌───────────────────────────┐      ┌───────────────────────────┐
│ UCI Gas Sensor Array      │      │ NASA C-MAPSS Turbofan     │
│ High-Freq Telemetry       │      │ Telemetry (10-100Hz)      │
└─────────────┬─────────────┘      └─────────────┬─────────────┘
              │                                  │
              └────────────────┬─────────────────┘
                               │ Raw High-Freq Stream
                               ▼
            ┌───────────────────────────────────────┐
            │  Sensor Anomaly Service               │
            │  - 2-Second Window Aggregation        │
            │  - Mean, Max, Rate of Change          │
            │  - Baseline Z-Score Computation       │
            └──────────────────┬────────────────────┘
                               │ Aggregated Z-Scores
                               ▼
┌───────────────────────────────────────────────────────────┐
│              Graph Engine Stub / Solver Interface         │
│  - Receives Aggregated Sensor States + Active Permits     │
│  - Evaluates Rule-Guards (triggered_by: "rule_guard")     │
│  - Evaluates Propagation (triggered_by: "propagation")    │
└──────────────────────────────┬────────────────────────────┘
                               │ RiskGraph & Alert List
                               ▼
┌───────────────────────────────────────────────────────────┐
│                    API Gateway (FastAPI)                  │
│  /api/graph-state           /api/inject-anomaly           │
│  /api/resimulate            /api/evidence/{alert_id}      │
│  /api/compliance-check                                    │
└──────────────────────────────┬────────────────────────────┘
                               │ REST / JSON
                               ▼
┌───────────────────────────────────────────────────────────┐
│           ZeroGuard Industrial Dashboard (React UI)       │
│  - Real-time Alert Feed with Confidence & Completeness     │
│  - Interactive Graph & Evidence Path Modal               │
│  - Compliance Citation Drawer & Permit Timeline           │
└──────────────────────────────┬────────────────────────────┘
```
