# Spatio-Temporal Weighted Propagation Graph Engine

A deterministic, fully explainable graph-based alert system for industrial safety monitoring. This is NOT a neural network - all components are based on explicit mathematical formulas with no black-box components.

## Overview

The engine processes high-frequency sensor data (10-100Hz) through time-bucketing, builds a weighted graph with Sensor, Permit, and Zone nodes, and propagates risk signals using Personalized PageRank (Random Walk with Restart). A deterministic rule-guard layer provides statutory safety checks that fire independently of the propagation layer.

## Architecture

### Components

1. **schemas.py** - Node type definitions (Sensor, Permit, Zone)
2. **time_bucketing.py** - Aggregates 10-100Hz input into 2-second windows (mean, max, rate-of-change)
3. **graph_engine.py** - Core graph with deterministic edge weight formula and PageRank propagation
4. **rule_guard.py** - Hardcoded statutory safety checks
5. **alert_system.py** - Combines propagation and rule-guard layers, outputs structured alerts
6. **parameter_fitting.py** - Gradient-boosted regression for fitting HazardSeverity and decay coefficients
7. **scenario_generator.py** - Synthetic labeled dataset generator for training
8. **test_alert_system.py** - Unit tests proving key safety guarantees

## Key Formulas

### Edge Weight
```
W_ij(t) = SpatialProximity(i,j) × HazardSeverity(i) × AnomalyZScore(j)
```

Where:
- SpatialProximity(i,j) = 1 / (1 + distance(i,j))
- HazardSeverity(i) is a learned parameter fitted via gradient-boosted regression
- AnomalyZScore(j) is the current z-score for sensor j (or 1.0 for non-sensors)

### Propagation
Personalized PageRank (Random Walk with Restart):
```
PR = (1 - α) × M × PR + α × personalization_vector
```
Where α = 0.15 (restart probability), M is the row-normalized adjacency matrix.

## Installation

```bash
pip install -r requirements.txt
```

Dependencies:
- numpy >= 1.21.0
- scikit-learn >= 1.0.0
- joblib >= 1.0.0

## Usage

### Basic Example

```python
from alert_system import AlertSystem
from scenario_generator import ScenarioGenerator

# Create alert system
alert_system = AlertSystem()

# Generate test scenario
scenario_gen = ScenarioGenerator()
sensors, permits, zones = scenario_gen.generate_correlated_anomaly_scenario()

# Combine nodes
nodes = {}
nodes.update(sensors)
nodes.update(permits)
nodes.update(zones)

# Evaluate alerts
alerts = alert_system.evaluate(nodes)

# Get top alert
top_alert = alert_system.get_top_alert(alerts)
print(f"Top alert: {top_alert.alert_level.value} from {top_alert.layer_source}")
```

### Time-Bucketing High-Frequency Data

```python
from time_bucketing import TimeBucketAggregator
from datetime import datetime, timedelta

aggregator = TimeBucketAggregator(window_seconds=2.0)

# Add raw readings at 50Hz
for i in range(100):
    timestamp = datetime.now() + timedelta(milliseconds=i * 20)
    aggregator.add_reading("sensor_1", value, timestamp)

# Get completed 2-second buckets
buckets = aggregator.get_completed_buckets(datetime.now())
```

### Parameter Fitting

```python
from parameter_fitting import ParameterFitter
from scenario_generator import ScenarioGenerator

# Generate training data
scenario_gen = ScenarioGenerator()
samples = scenario_gen.generate_training_dataset(n_samples=1000)

# Train models
fitter = ParameterFitter()
metrics = fitter.train(samples)

# Save models
fitter.save_models()
```

## Rule-Guard Layer

The rule-guard layer implements hardcoded statutory checks:

- **Hot Work + H2S > 10ppm within 15m** → COMPOUND_CRITICAL
- **Hot Work + LEL > 10% within 15m** → COMPOUND_CRITICAL
- **Confined Space + O2 < 19.5% or > 23.5% within 15m** → COMPOUND_CRITICAL
- **Confined Space + CO > 35ppm within 15m** → COMPOUND_CRITICAL
- **Multiple anomalous sensors within 20m** → HIGH
- **High occupancy zone + hazardous sensor** → HIGH
- **Permit expiring within 5 minutes** → MEDIUM
- **Rapid sensor change** → MEDIUM

These rules fire independently of the propagation layer's confidence.

## Alert Output Structure

Each alert provides structured data for the Evidence Explainer:

```python
{
    "alert_id": "PROP_1",
    "timestamp": "2026-07-21T08:28:00",
    "risk_score": 0.75,
    "confidence": 0.85,
    "alert_level": "high",
    "layer_source": "propagation",  # or "rule_guard" or "both"
    "contributing_nodes": [
        {"node_id": "sensor_1", "weight": 0.45},
        {"node_id": "sensor_2", "weight": 0.30}
    ],
    "contributing_weights": {
        "sensor_1": 0.45,
        "sensor_2": 0.30
    },
    "metadata": {...}
}
```

## Safety Guarantees

The system enforces two critical safety properties:

### 1. Single Anomaly Constraint
A single anomalous signal alone never triggers COMPOUND_CRITICAL without a correlated second signal. This is enforced by:
- Propagation layer requiring correlation for high-risk scores
- Rule-guard layer only triggering on specific multi-factor conditions

### 2. Rule-Guard Independence
The rule-guard layer fires independent of the propagation layer's confidence. Statutory rules always take precedence when conditions are met, regardless of propagation scores.

## Running Tests

```bash
python -m pytest test_alert_system.py -v
```

Or run directly:
```bash
python test_alert_system.py
```

Key tests:
- `test_single_anomaly_no_compound_critical` - Proves single anomaly constraint
- `test_rule_guard_fires_independent_of_propagation` - Proves rule-guard independence
- `test_rule_guard_with_low_propagation_confidence` - Validates independence under low confidence

## Running Examples

```bash
python example_usage.py
```

This demonstrates:
- Time-bucketing of high-frequency data
- Graph propagation with Personalized PageRank
- Rule-guard layer evaluation
- Complete alert system workflow
- Parameter fitting with gradient-boosted regression
- Single anomaly safety test

## Deterministic Properties

The entire system is deterministic and explainable:

1. **Edge weights** - Explicit formula with no learned components
2. **Propagation** - Standard PageRank algorithm with fixed restart probability
3. **Rule-guard** - Hardcoded statutory checks with clear conditions
4. **Parameter fitting** - Only affects HazardSeverity and decay coefficients, not core logic
5. **No neural networks** - All components are formula-based

## File Structure

```
hardware/
├── schemas.py                  # Node type definitions
├── time_bucketing.py          # High-frequency data aggregation
├── graph_engine.py            # Core graph and propagation
├── rule_guard.py              # Statutory safety checks
├── alert_system.py            # Alert generation and output
├── parameter_fitting.py       # Gradient-boosted regression
├── scenario_generator.py      # Synthetic data generator
├── test_alert_system.py       # Unit tests
├── example_usage.py           # Usage examples
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## License

This is a deterministic safety-critical system. All formulas are explicit and explainable.
