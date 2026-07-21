# PRODUCTION-GRADE VERIFICATION AUDIT REPORT

**Audit Date**: 2026-07-21
**Scope**: Graph engine for refinery safety system
**Severity Levels**: Critical (immediate safety risk), High (significant risk), Medium (moderate risk), Low (minor issue)

---

## 1. Mathematical Errors in Propagation Formula

**No issues found.** The edge weight formula `W_ij(t) = SpatialProximity(i,j) × HazardSeverity(i) × AnomalyZScore(j)` is implemented correctly at line 123 in graph_engine.py.

---

## 2. Floating Point Instability

**Severity: Medium**
**File**: c:/Users/samyu/OneDrive/Desktop/hardware/graph_engine.py
**Function**: build_adjacency_matrix
**Line**: 171-172
**Why it fails**: Row normalization uses `row_sums[row_sums == 0] = 1.0` which replaces zero sums with 1.0. However, very small row_sums (e.g., 1e-15) are not handled, leading to division by a tiny number that can produce extremely large values due to floating point precision loss. This can cause numerical instability in the PageRank iteration.
**Minimal reproduction**: Create a graph where all edge weights for a node are extremely small (e.g., 1e-16), causing row_sum to be near-zero but not exactly zero.
**Expected behavior**: Should handle near-zero row_sums by either setting a minimum threshold or using a more robust normalization method.
**Actual behavior**: Division by near-zero values can produce large floating point errors.
**Suggested fix**: Add a minimum threshold: `row_sums = np.maximum(row_sums, 1e-10)` before normalization.

---

## 3. Overflow, Underflow, Division by Zero

**Severity: High**
**File**: c:/Users/samyu/OneDrive/Desktop/hardware/graph_engine.py
**Function**: calculate_spatial_proximity
**Line**: 67, 70, 83
**Why it fails**: The formula `1.0 / (1.0 + distance)` can produce underflow for extremely large distances (e.g., distance > 1e308), though this is unlikely in practice. More critically, if distance is NaN or infinity, the result will be NaN without validation.
**Minimal reproduction**: Pass a node with coordinates containing NaN or infinity values.
**Expected behavior**: Should validate that distance is finite and non-NaN before division.
**Actual behavior**: No validation - can propagate NaN values through the entire computation.
**Suggested fix**: Add `if not np.isfinite(distance): return 0.0` before division.

---

## 4. Normalization Mistakes

**Severity: Critical**
**File**: c:/Users/samyu/OneDrive/Desktop/hardware/graph_engine.py
**Function**: build_adjacency_matrix
**Line**: 169-172
**Why it fails**: The row normalization creates a stochastic matrix for PageRank, but the normalization happens AFTER edge weights are computed. If a row has all zero weights (no valid spatial proximity for any edge), it's set to 1.0 and then normalized, creating a uniform distribution. This is incorrect for PageRank - rows with no valid edges should remain zero (dangling node), not become uniform.
**Minimal reproduction**: Create a node with no valid spatial proximity data to any other node. The row will be [0, 0, ..., 0], then set to [1, 1, ..., 1], then normalized to [1/n, 1/n, ..., 1/n], incorrectly treating it as fully connected.
**Expected behavior**: Dangling nodes (rows with all zeros) should be handled via the teleportation (restart) mechanism in PageRank, not by artificially creating uniform distributions.
**Actual behavior**: Artificially creates uniform distribution for disconnected nodes, violating PageRank semantics.
**Suggested fix**: Remove line 171, handle dangling nodes properly in the PageRank iteration by adding the restart probability contribution uniformly.

---

## 5. Infinite Loops or Unbounded Propagation

**No issues found.** The PageRank iteration has a hard limit of 100 iterations (line 178), preventing infinite loops.

---

## 6. Graph Inconsistencies

**Severity: High**
**File**: c:/Users/samyu/OneDrive/Desktop/hardware/graph_engine.py
**Function**: calculate_edge_weight
**Line**: 124
**Why it fails**: The function uses `max(0.0, weight)` to ensure non-negative weights, but there is no validation that weights are bounded above. If spatial_proximity, hazard_severity, and anomaly_score are all large, weight can be arbitrarily large, breaking the stochastic matrix assumption.
**Minimal reproduction**: Set hazard_severity = 1000, anomaly_score = 1000, spatial_proximity = 1.0, resulting in weight = 1,000,000.
**Expected behavior**: Edge weights should be bounded (e.g., clipped to [0, 1]) before normalization.
**Actual behavior**: Unbounded weights can cause numerical instability and incorrect PageRank results.
**Suggested fix**: Add weight clipping: `weight = min(max(0.0, weight), 1.0)` or normalize weights before building the adjacency matrix.

---

## 7. Determinism Violations

**No issues found.** The determinism test passed (20 identical runs produced byte-identical output). No unseeded random number generation or non-deterministic operations detected.

---

## 8. Race Conditions or Thread Safety Issues

**Severity: Medium**
**File**: c:/Users/samyu/OneDrive/Desktop/hardware/alert_system.py
**Function**: evaluate
**Line**: 21, 116
**Why it fails**: The `alert_counter` is an instance variable that is incremented without any synchronization. If AlertSystem.evaluate() is called concurrently from multiple threads, the alert_counter could race, leading to duplicate or skipped alert IDs.
**Minimal reproduction**: Call AlertSystem.evaluate() concurrently from multiple threads on the same instance.
**Expected behavior**: Alert IDs should be unique even under concurrent access.
**Actual behavior**: No thread safety - alert_counter can race, potentially producing duplicate alert IDs.
**Suggested fix**: Use a thread-safe counter (e.g., `threading.Lock` or `itertools.count()` which is atomic in CPython).

---

## 9. Memory Leaks, Unbounded Growth

**Severity: High**
**File**: c:/Users/samyu/OneDrive/Desktop/hardware/graph_engine.py
**Function**: set_nodes
**Line**: 29
**Why it fails**: The `self.nodes` dictionary is replaced on each call to `set_nodes()`, but `self.adjacency_matrix`, `self.edge_weights`, and other instance variables are not explicitly cleared. If `set_nodes()` is called repeatedly with different node sets, old data in these variables could cause memory leaks or stale data contamination.
**Minimal reproduction**: Call `set_nodes()` with 10,000 nodes, then call it again with 10 different nodes, repeatedly in a loop.
**Expected behavior**: All instance variables should be cleared/reset when nodes are reset.
**Actual behavior**: Old adjacency matrices and edge weights may persist in memory.
**Suggested fix**: Add explicit cleanup in `set_nodes()`: clear `self.adjacency_matrix`, `self.edge_weights`, `self.node_id_to_index`, `self.index_to_node_id`.

---

## 10. Hidden State

**Severity: Critical**
**File**: c:/Users/samyu/OneDrive/Desktop/hardware/graph_engine.py
**Function**: Multiple
**Line**: 19-25
**Why it fails**: The GraphEngine maintains persistent instance state (`self.nodes`, `self.adjacency_matrix`, `self.edge_weights`, `self.sensor_permit_distances`) between calls to `evaluate()`. If `set_nodes()` is not called before each evaluation, stale data from a previous evaluation will leak into the current one. The `evaluate()` function in alert_system.py does call `set_nodes()`, but this is fragile - if the calling pattern changes, state will leak.
**Minimal reproduction**: Call `evaluate()` with one set of nodes, then call it again with a different set without calling `set_nodes()` in between. The second evaluation will use stale adjacency matrix from the first.
**Expected behavior**: Each evaluation should be stateless or explicitly reset all state before computation.
**Actual behavior**: State persists between evaluations, creating a hidden dependency on calling order.
**Suggested fix**: Either make the engine stateless (pass all data as parameters) or add explicit state reset at the start of each public method.

---

## 11. Rule-guard Precedence Bugs

**Severity: Critical**
**File**: c:/Users/samyu/OneDrive/Desktop/hardware/alert_system.py
**Function**: evaluate
**Line**: 58-132
**Why it fails**: The rule-guard layer is NOT integrated into AlertSystem.evaluate(). The rule_guard.py module exists but is never called. The docstring claims "Evaluate both propagation and rule-guard layers" but only the propagation layer is actually executed. This means rule-guard statutory checks are completely non-functional in production.
**Minimal reproduction**: Create a scenario with active hot-work permit + H2S > 10ppm (should trigger COMPOUND_CRITICAL per rule-guard). The evaluate() function will NOT trigger this rule.
**Expected behavior**: Both propagation and rule-guard layers should be evaluated and results merged according to defined precedence.
**Actual behavior**: Only propagation layer runs. Rule-guard is completely non-functional.
**Suggested fix**: Integrate rule_guard.RuleGuard.evaluate_rules() into AlertSystem.evaluate() and define precedence logic for when both layers fire.

---

## 12. Sensor/Timestamp Bugs

**Severity: High**
**File**: c:/Users/samyu/OneDrive/Desktop/hardware/alert_system.py
**Function**: evaluate
**Line**: 86-89
**Why it fails**: The code checks `if node.z_score` to identify anomalous sensors, but it does not validate that `node.z_score` is finite (not NaN or infinity). If a sensor returns NaN (e.g., due to communication error), it will be treated as non-anomalous (False in boolean context), silently ignoring the bad reading.
**Minimal reproduction**: Create a sensor node with `z_score = float('nan')`. It will be silently ignored instead of triggering an error or being handled as invalid data.
**Expected behavior**: Invalid sensor readings (NaN, infinity) should be detected and handled explicitly (e.g., trigger a sensor fault alert).
**Actual behavior**: Invalid readings are silently treated as normal due to Python's boolean evaluation of NaN as False.
**Suggested fix**: Add explicit validation: `if node.z_score is not None and np.isfinite(node.z_score)` before using z_score.

**Severity: Medium**
**File**: c:/Users/samyu/OneDrive/Desktop/hardware/alert_system.py
**Function**: evaluate
**Line**: 128
**Why it fails**: The timestamp uses `datetime.now().isoformat()` which reflects wall-clock time. If the system clock changes (NTP adjustment, manual correction, timezone change), timestamps can be non-monotonic or jump backward, breaking any time-based analysis or alert ordering.
**Minimal reproduction**: Manually set the system clock backward during evaluation. Timestamps will be out of order.
**Expected behavior**: Should use a monotonic clock or sequence number for alert ordering, with wall-clock time as a separate field.
**Actual behavior**: Wall-clock time can jump backward, breaking temporal ordering assumptions.
**Suggested fix**: Use `time.monotonic_ns()` for ordering and include wall-clock time as a separate field.

---

## 13. Statistical Impossibilities in Output

**Severity: High**
**File**: c:/Users/samyu/OneDrive/Desktop/hardware/alert_system.py
**Function**: evaluate
**Line**: 103
**Why it fails**: The risk score is calculated as `max_risk * 100` where `max_risk` is a PageRank score. PageRank scores should sum to 1.0 across all nodes, so individual scores are in [0, 1]. However, due to the normalization bug (Issue #4), scores could exceed 1.0, resulting in risk_score > 100. There is no validation that risk_score stays in [0, 100].
**Minimal reproduction**: Trigger the normalization bug (Issue #4) to get PageRank scores > 1.0, resulting in risk_score > 100.
**Expected behavior**: Risk score should be clipped to [0, 100] range before being used.
**Actual behavior**: No validation - risk_score can exceed 100 or be negative if PageRank is corrupted.
**Suggested fix**: Add validation: `risk_score_100 = max(0.0, min(max_risk * 100, 100.0))`

**Severity: Medium**
**File**: c:/Users/samyu/OneDrive/Desktop/hardware/alert_system.py
**Function**: _calculate_evidence_completeness
**Line**: 56
**Why it fails**: The evidence completeness calculation uses `present_count / total_expected` which can produce values outside [0, 1] if there are duplicate node IDs in the input (present_count could exceed total_expected).
**Minimal reproduction**: Pass a list of nodes with duplicate IDs. present_count will count duplicates, potentially exceeding total_expected.
**Expected behavior**: Should use a set for current_ids (already done) but also validate that the result is in [0, 1].
**Actual behavior**: No validation - completeness could exceed 1.0 with duplicate IDs.
**Suggested fix**: Add clipping: `return min(max(present_count / total_expected, 0.0), 1.0) if total_expected > 0 else 1.0`

---

## 14. Incorrect Aggregation in Time-bucketing

**Severity: Medium**
**File**: c:/Users/samyu/OneDrive/Desktop/hardware/time_bucketing.py
**Function**: get_completed_buckets
**Line**: 55-57
**Why it fails**: The bucket extraction uses `while buffer and buffer[0][0] <= cutoff_time` which extracts ALL readings older than the cutoff, but doesn't actually group them into discrete 2-second windows. It puts all extracted readings into a single "window" regardless of their actual time span. If readings span 10 seconds, they'll all be aggregated together instead of being split into 5 separate 2-second windows.
**Minimal reproduction**: Add readings at t=0, t=1, t=3, t=5, t=7 seconds. Call get_completed_buckets at t=10. All 5 readings will be in one bucket instead of being split into [0,1], [3,5], [7,9] windows.
**Expected behavior**: Should group readings into discrete non-overlapping 2-second windows (e.g., [0,2), [2,4), [4,6), etc.).
**Actual behavior**: All readings older than cutoff are lumped into a single bucket, violating the 2-second windowing requirement.
**Suggested fix**: Implement proper windowing logic that groups readings by their window start time: `window_start = int(timestamp.timestamp() // window_seconds) * window_seconds`.

---

## 15. Performance Issues

**Severity: High**
**File**: c:/Users/samyu/OneDrive/Desktop/hardware/graph_engine.py
**Function**: build_adjacency_matrix
**Line**: 149-164
**Why it fails**: The adjacency matrix construction uses nested loops over all node pairs: `for i, node_id_i in enumerate(node_ids): for j, node_id_j in enumerate(node_ids):`. This is O(n²) where n is the number of nodes. For a refinery with 10,000 sensors, this is 100 million iterations per evaluation, which is unnecessarily slow. The graph should be sparse (sensors only connect to nearby permits), so this should use an adjacency list representation instead of a dense matrix.
**Minimal reproduction**: Create a graph with 10,000 nodes. The nested loops will execute 100,000,000 times.
**Expected behavior**: Should use sparse matrix operations or adjacency lists for O(E) complexity where E is the number of edges (typically much smaller than n²).
**Actual behavior**: O(n²) dense matrix construction is inefficient for large sparse graphs.
**Suggested fix**: Use scipy.sparse matrix or adjacency list representation, only computing edges for node pairs that have valid spatial proximity data.

---

## 16. Missing Edge Cases in Tests

**Severity: High**
**File**: test_alert_system.py
**Function**: Multiple
**Line**: Various
**Why it fails**: The current tests do not cover:
- Nodes with NaN or infinity values
- Empty node lists
- Single node graphs
- Disconnected graphs (no edges between any nodes)
- Nodes with duplicate IDs
- Negative z-scores (only positive tested)
- Zero hazard_severity
- Very large distances (> 1e6 meters)
- Concurrent evaluation (thread safety)
- Clock skew or backward time jumps
- Sensor readings at exact threshold boundaries (e.g., z_score = 2.0 exactly)
**Minimal reproduction**: Any of the above scenarios would not be caught by current tests.
**Expected behavior**: Tests should cover edge cases that could cause crashes or incorrect behavior.
**Actual behavior**: Tests only cover happy paths with well-formed data.
**Suggested fix**: Add comprehensive edge case tests for each of the above scenarios.

---

## 17. Weak Tests

**Severity: Medium**
**File**: test_alert_system.py
**Function**: test_correlated_anomalies_can_trigger_high
**Line**: 88-107
**Why it fails**: The test only checks that alerts are generated (`len(alerts) > 0`) but does not verify the actual risk_level, risk_score, or contributing_node_ids. A test that passes with any alert being generated doesn't actually verify the correlation logic works correctly.
**Minimal reproduction**: The test would pass even if the alert system generated a LOW risk alert for correlated HIGH anomalies.
**Expected behavior**: Should assert specific risk_level (e.g., HIGH or CRITICAL) and verify contributing_node_ids includes the correlated sensors.
**Actual behavior**: Only checks that some alert exists, not that it's the correct alert.
**Suggested fix**: Add assertions for expected risk_level and verify contributing_node_ids contains the expected correlated sensors.

**Severity: Medium**
**File**: test_alert_system.py
**Function**: test_alert_output_structure
**Line**: 109-133
**Why it fails**: The test checks that fields exist but doesn't validate their values are within expected ranges (except for a few basic checks). It doesn't verify that risk_score is actually computed correctly from the PageRank scores, or that confidence_score reflects the actual edge validity.
**Minimal reproduction**: The test would pass even if risk_score was hardcoded to 50.0.
**Expected behavior**: Should verify that output values are consistent with input (e.g., higher z-scores produce higher risk scores).
**Actual behavior**: Only checks field presence and basic range validation.
**Suggested fix**: Add assertions that output values correlate with input severity (e.g., higher anomaly scores produce higher risk levels).

---

## SUMMARY TABLE

| Category | Critical | High | Medium | Low | Total |
|----------|----------|------|--------|-----|-------|
| 1. Mathematical errors | 0 | 0 | 0 | 0 | 0 |
| 2. Floating point instability | 0 | 0 | 1 | 0 | 1 |
| 3. Overflow, underflow, division by zero | 0 | 1 | 0 | 0 | 1 |
| 4. Normalization mistakes | 1 | 0 | 0 | 0 | 1 |
| 5. Infinite loops | 0 | 0 | 0 | 0 | 0 |
| 6. Graph inconsistencies | 0 | 1 | 0 | 0 | 1 |
| 7. Determinism violations | 0 | 0 | 0 | 0 | 0 |
| 8. Race conditions | 0 | 0 | 1 | 0 | 1 |
| 9. Memory leaks | 0 | 1 | 0 | 0 | 1 |
| 10. Hidden state | 1 | 0 | 0 | 0 | 1 |
| 11. Rule-guard precedence | 1 | 0 | 0 | 0 | 1 |
| 12. Sensor/timestamp bugs | 0 | 1 | 1 | 0 | 2 |
| 13. Statistical impossibilities | 0 | 1 | 1 | 0 | 2 |
| 14. Incorrect aggregation | 0 | 0 | 1 | 0 | 1 |
| 15. Performance issues | 0 | 1 | 0 | 0 | 1 |
| 16. Missing edge cases | 0 | 1 | 0 | 0 | 1 |
| 17. Weak tests | 0 | 0 | 2 | 0 | 2 |
| **TOTAL** | **3** | **7** | **7** | **0** | **17** |

---

## OVERALL ASSESSMENT

**CRITICAL FINDINGS (3):**
1. Normalization mistake in PageRank - dangling nodes incorrectly handled
2. Hidden state between evaluations - state leak risk
3. Rule-guard layer completely non-functional - statutory checks not executed

**HIGH SEVERITY FINDINGS (7):**
1. No validation for NaN/infinity in spatial proximity calculation
2. Unbounded edge weights can break stochastic matrix assumption
3. Memory leak risk from uncleared instance variables
4. Invalid sensor readings (NaN) silently ignored
5. Risk score can exceed valid range [0, 100]
6. O(n²) performance for sparse graphs
7. Missing edge case test coverage

**MEDIUM SEVERITY FINDINGS (7):**
1. Floating point instability with near-zero row sums
2. Thread safety issue with alert_counter
3. Wall-clock time can jump backward
4. Evidence completeness can exceed 1.0 with duplicates
5. Time-bucketing doesn't properly group into discrete windows
6. Test for correlated anomalies doesn't verify correct output
7. Alert output structure test doesn't validate value correctness

**CONCLUSION: NOT PRODUCTION READY**

This graph engine has 3 critical safety issues that must be fixed before deployment in a real refinery. The most critical is that the rule-guard layer (statutory safety checks) is completely non-functional, meaning statutory violations would not be detected. Additionally, the PageRank normalization is incorrect, and hidden state between evaluations could cause unpredictable behavior.
