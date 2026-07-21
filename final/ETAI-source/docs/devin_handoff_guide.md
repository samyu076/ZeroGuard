# ZeroGuard — Devin Build Team Handoff & Dataset Checksum Specification

This document provides the exact frozen specifications, dataset checksums, and handoff instructions for the external Graph Engine build team (Devin).

---

## 1. Dataset SHA-256 Checksums (Single Source of Truth)

Before training, fitting parameters, or running unit tests in Devin's workspace, verify that your local copies of the dataset and frozen contract match these exact SHA-256 checksums:

| File Path | Description | Required SHA-256 Checksum |
|---|---|---|
| [`docs/api-contract.md`](file:///c:/Users/samyu/OneDrive/Desktop/ETAI/docs/api-contract.md) | Frozen OpenAPI 3.0 & Pydantic Schema Specification | `56f51...` |
| [`data/plant_layout.json`](file:///c:/Users/samyu/OneDrive/Desktop/ETAI/data/plant_layout.json) | Shared 5-Zone Grid Layout \((x, y)\) in meters | `6745cbb6be84bb12b23536b7432b46df69d6a1e3071d6e7a226835ce5d7f26eb` |
| [`data/scenarios_500.json`](file:///c:/Users/samyu/OneDrive/Desktop/ETAI/data/scenarios_500.json) | 520 Labeled Scenarios (76.15% SAFE, 2.88% COMPOUND_CRITICAL) | `ae95435483f3907a6c5abb704a9e1e6980faee844124f2940cba8b6ffcb66ba0` |

### Checksum Verification Command (PowerShell / Bash)
```powershell
Get-FileHash -Algorithm SHA256 data/scenarios_500.json
Get-FileHash -Algorithm SHA256 data/plant_layout.json
Get-FileHash -Algorithm SHA256 docs/api-contract.md
```

---

## 2. Key Graph Engine Input Specifications

- **Edge Weight Formula**:
  \[
  W_{ij}(t) = \text{SpatialProximity}(i,j) \times \text{HazardSeverity}(i) \times \text{AnomalyZScore}(j)
  \]
  where \(\text{SpatialProximity}(i,j) = \max\left(0, 1 - \frac{d_{ij}}{35.0}\right)\).
- **Euclidean Distances**: Precomputed in `scenarios_500.json` under `sensor_permit_distances[]`.
- **Alert Trigger Layer**: All alert outputs must populate `triggered_by: "rule_guard" | "propagation"`.
- **Confidence & Evidence Completeness**: Every alert and risk graph state MUST return `confidence_score` (0.0 to 1.0) and `evidence_completeness` (0.0 to 1.0).

---

## 3. Human Citation Verification Checklist

> [!IMPORTANT]
> **Pre-Pitch Human Audit Required**:
> Before demoing to judges, manually cross-check these statutory references against external official PDFs:
> 1. **Factory Act 1948 Section 36** *(VERIFIED-FROM-SOURCE)*: Precautions against dangerous fumes & confined space ingress.
> 2. **OISD-STD-105 Clause 6.2.1**: Gas testing & hot work isolation.
> 3. **OISD-STD-118 Clause 5.4.2**: Confined space spectacle blind isolation.
