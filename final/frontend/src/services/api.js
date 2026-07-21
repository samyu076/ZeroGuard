/**
 * ZeroGuard Frontend API Service Client
 * Consistently routes all REST requests through /api/v1/ prefix.
 */

const API_BASE = '/api/v1';

async function handleResponse(response) {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(errorData.detail || `HTTP Error ${response.status}`);
  }
  return response.json();
}

export async function fetchScenarios(label = null) {
  const url = label ? `${API_BASE}/scenarios?label=${encodeURIComponent(label)}` : `${API_BASE}/scenarios`;
  const res = await fetch(url);
  return handleResponse(res);
}

export async function fetchScenarioById(scenarioId) {
  const res = await fetch(`${API_BASE}/scenarios/${encodeURIComponent(scenarioId)}`);
  return handleResponse(res);
}

export async function fetchPlantLayout() {
  const res = await fetch(`${API_BASE}/plant-layout`);
  return handleResponse(res);
}

export async function fetchGraphState() {
  const res = await fetch(`${API_BASE}/graph-state`);
  return handleResponse(res);
}

export async function injectAnomaly(sensorId, targetZScore) {
  const res = await fetch(`${API_BASE}/inject-anomaly`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ sensor_id: sensorId, target_z_score: parseFloat(targetZScore) })
  });
  return handleResponse(res);
}

export async function resimulateScenario(activePermitIds, injectedAnomalies) {
  const res = await fetch(`${API_BASE}/resimulate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      active_permit_ids: activePermitIds,
      injected_sensor_anomalies: injectedAnomalies
    })
  });
  return handleResponse(res);
}

export async function fetchEvidencePath(alertId) {
  const res = await fetch(`${API_BASE}/evidence/${encodeURIComponent(alertId)}`);
  return handleResponse(res);
}

export async function checkCompliance(params) {
  const queryParams = new URLSearchParams();
  if (params.zoneId) queryParams.append('zone_id', params.zoneId);
  if (params.permitType) queryParams.append('permit_type', params.permitType);
  if (params.queryText) queryParams.append('query_text', params.queryText);
  if (params.isolationStatus) queryParams.append('isolation_status', params.isolationStatus);
  if (params.gasZScore !== undefined) queryParams.append('gas_z_score', params.gasZScore);

  const res = await fetch(`${API_BASE}/compliance/check?${queryParams.toString()}`);
  return handleResponse(res);
}

export async function fetchMetrics() {
  const res = await fetch(`${API_BASE}/metrics`);
  return handleResponse(res);
}
