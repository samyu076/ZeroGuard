from fastapi import APIRouter, Depends
from graph_engine.stub import StubGraphEngine
from graph_engine.schema import AnomalyInjectionRequest, RiskGraph
from app.api.deps import get_graph_engine
from app.services.sensor_anomaly import SensorAnomalyService

router = APIRouter()
sensor_anomaly_service = SensorAnomalyService()

@router.post("/inject-anomaly", response_model=RiskGraph)
def inject_anomaly(request: AnomalyInjectionRequest, engine: StubGraphEngine = Depends(get_graph_engine)):
    """
    Inject synthetic sensor anomaly z-score spike and re-evaluate graph risk.
    Executes SensorAnomalyService 2-second time bucket telemetry processing.
    """
    # Execute SensorAnomalyService processing on incoming telemetry stream
    sensor_anomaly_service.process_raw_stream_into_2s_buckets([
        {
            "sensor_id": request.sensor_id,
            "reading_ppm": request.custom_value or (request.target_z_score * 15.0 + 10.0),
            "window_duration_seconds": 2.0
        }
    ])

    # Inject target_z_score into shared singleton graph engine state
    return engine.inject_sensor_anomaly(request)
