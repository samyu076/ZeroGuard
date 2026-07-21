const API_BASE = '/api';

export async function fetchGraphState() {
  const res = await fetch(`${API_BASE}/graph-state`);
  if (!res.ok) throw new Error('Failed to fetch graph state');
  return res.json();
}

export async function injectAnomaly(sensorId, targetZScore) {
  const res = await fetch(`${API_BASE}/inject-anomaly`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      sensor_id: sensorId,
      target_z_score: targetZScore,
      duration_seconds: 60
    })
  });
  if (!res.ok) throw new Error('Failed to inject anomaly');
  return res.json();
}

export async function fetchEvidence(alertId) {
  const res = await fetch(`${API_BASE}/evidence/${alertId}`);
  if (!res.ok) throw new Error('Failed to fetch evidence path');
  return res.json();
}

export async function runComplianceCheck(permitType, queryText) {
  const res = await fetch(`${API_BASE}/compliance-check`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      permit_type: permitType || null,
      query_text: queryText || null
    })
  });
  if (!res.ok) throw new Error('Failed to run compliance check');
  return res.json();
}
