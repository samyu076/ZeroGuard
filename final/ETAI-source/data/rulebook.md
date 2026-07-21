> **CITATIONS MARKED 'UNVERIFIED' IN citation_verification_report.md HAVE NOT BEEN CONFIRMED AGAINST PRIMARY SOURCES AND MUST NOT BE PRESENTED TO JUDGES AS CONFIRMED REGULATORY FACT UNTIL A HUMAN TEAM MEMBER MANUALLY VERIFIES THEM AGAINST THE ACTUAL OISD/API 670 TEXT.**

# ZeroGuard Synthetic Scenario Generator — Legally Defensible Rulebook (Revised)

This document provides the formal audit specification for the ZeroGuard synthetic scenario dataset. Every generated scenario and ground-truth risk label (`SAFE`, `WATCH`, `WARNING`, `COMPOUND_CRITICAL`) is computed via a deterministic evaluation tree enforcing real-world plant operational rarity, spatial proximity math, and multi-signal interaction.

---

## 1. Spatial Edge-Weight & Risk Coupling Formula

The ZeroGuard Graph Engine evaluates risk propagation using the spatial coupling weight formula:

\[
W_{ij}(t) = \text{SpatialProximity}(i,j) \times \text{HazardSeverity}(i) \times \text{AnomalyZScore}(j)
\]

where:
- \(\text{SpatialProximity}(i,j) = \max\left(0, 1 - \frac{d_{ij}}{D_{\text{threshold}}}\right)\)
- \(d_{ij} = \sqrt{(x_i - x_j)^2 + (y_i - y_j)^2}\) is the Euclidean distance in meters between sensor \(i\) and permit/equipment \(j\) on the shared plant grid ([plant_layout.json](file:///c:/Users/samyu/OneDrive/Desktop/ETAI/data/plant_layout.json)).
- \(D_{\text{threshold}} = 35.0\text{ meters}\) (maximum interaction radius for atmospheric hydrocarbon gas and thermal dispersion).

---

## 2. Operational Rarity & Target Label Distribution

Industrial facilities operate in a `SAFE` state during the vast majority of operating hours. Compound critical risk events are rare multi-factor escalations.

### Distribution Targets across 520 Scenarios

| Ground-Truth Label | Operational State | Target Percentage | Target Scenario Count |
|---|---|---|---|
| **`SAFE`** | Normal baseline plant operations. All sensors within \(\pm 1.0\sigma\). No correlated risk signals. | **76.15%** | **396 scenarios** |
| **`WATCH`** | Single weak isolated anomaly (\(1.5 \le Z < 2.5\)) or minor shift log delay. No co-located active permits. | **14.23%** | **74 scenarios** |
| **`WARNING`** | Two correlated signals (e.g. sensor drift \(Z \ge 2.5\) + active permit in same zone, \(d_{ij} \le 35\text{m}\)). | **6.73%** | **35 scenarios** |
| **`COMPOUND_CRITICAL`** | Multi-signal correlated hazard (e.g. LEL gas drift \(Z \ge 3.0\) + active Hot Work / Line Break / Vessel Entry permit within \(d_{ij} \le 25\text{m}\) lacking statutory isolation). | **2.88%** | **15 scenarios** |
| **Total** | | **100.0%** | **520 scenarios** |

---

## 3. Multi-Signal Generation Rules & Statutory Citations

### Rule 1: Co-located Hot Work & Flammable Gas Drift (`COMPOUND_CRITICAL`)
- **Condition**: Active `HOT_WORK` permit co-located with a gas sensor recording aggregated LEL z-score \(Z \ge 3.0\) at Euclidean distance \(d_{ij} \le 25.0\text{ meters}\).
- **Ground-Truth Label**: **`COMPOUND_CRITICAL`**
- **Regulatory Citations**:
  - **OISD-STD-105 Clause 6.2.1** *(Unverified online; human PDF check required)*
  - **OSHA 29 CFR 1910.252(a)(2)** *(VERIFIED-FROM-SOURCE)*
  - **US Chemical Safety Board (CSB) Incident Report 2010-06-I-TX** *(Unverified online)*

### Rule 2: Vessel Confined Space Entry Without Positive Blind Isolation (`COMPOUND_CRITICAL`)
- **Condition**: Active `VESSEL_ENTRY` permit in process zone where vessel isolation status is logged as `VALVE_CLOSED_ONLY` (lacking spectacle blind insertion) and ambient gas sensor \(Z \ge 2.0\).
- **Ground-Truth Label**: **`COMPOUND_CRITICAL`**
- **Regulatory Citations**:
  - **OISD-STD-118 Section 5.4.2** *(Unverified online)*
  - **Factory Act 1948 Section 36** *(VERIFIED-FROM-SOURCE: Precautions against dangerous fumes & confined space entry)*
  - **OSHA 29 CFR 1910.146(d)(3)(iii)** *(VERIFIED-FROM-SOURCE)*

### Rule 3: Line Breaking Operation on Pressurized Hydrocarbon Header (`COMPOUND_CRITICAL`)
- **Condition**: Active `LINE_BREAK` permit with localized gas sensor drift \(Z \ge 3.0\) and header line pressure \(> 0.5\text{ bar}\) within \(d_{ij} \le 20.0\text{ meters}\).
- **Ground-Truth Label**: **`COMPOUND_CRITICAL`**
- **Regulatory Citations**:
  - **OISD-STD-105 Clause 7.1** *(Unverified online)*
  - **CSB Incident Report No. 2005-04-I-TX (BP Texas City Explosion)** *(VERIFIED-FROM-SOURCE)*

### Rule 4: High-Temperature Thermal Drift & Mechanical Vibration Spike (`WARNING`)
- **Condition**: Turbofan/Hydrocracker temperature sensor rate-of-change \(\Delta T / \Delta t > 2.5^\circ\text{C/s}\) coupled with bearing vibration sensor \(Z \ge 2.8\) in the same equipment zone (\(d_{ij} \le 30.0\text{m}\)).
- **Ground-Truth Label**: **`WARNING`**
- **Regulatory Citations**:
  - **API 670 Section 7.1** *(Unverified online)*
  - **OSHA 29 CFR 1910.119(j)** *(VERIFIED-FROM-SOURCE)*

---

## 4. Defense Guarantees

1. **Strict Spatial Integration**: Every scenario references [plant_layout.json](file:///c:/Users/samyu/OneDrive/Desktop/ETAI/data/plant_layout.json), containing explicit \((x, y)\) coordinates for every sensor and permit, along with pre-computed Euclidean distance matrices (`sensor_permit_distances`).
2. **Multi-Signal Coupling**: Every scenario contains 2 to 6 sensors and 0 to 3 active permits. No single-sensor, single-permit records exist.
3. **Exact Label Verification**: Dataset generation executes hard `assert` checks verifying that exact label counts match target operational rarity (396 SAFE, 74 WATCH, 35 WARNING, 15 COMPOUND_CRITICAL).
