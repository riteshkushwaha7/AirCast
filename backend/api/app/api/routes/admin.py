from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.deps import (
    get_dataset_service,
    get_ingestion_service,
    get_preprocessing_service,
)
from app.db.influx import InfluxProvider, get_influx_provider
from app.db.postgres import get_db_session
from app.schemas.ingestion import (
    DatasetBuildResponse,
    IngestionBackfillRequest,
    IngestionRunCurrentRequest,
    IngestionSummaryResponse,
    IngestionTriggerResponse,
    PreprocessingRunRequest,
    PreprocessingTriggerResponse,
    TrainingDatasetRequest,
)
from app.services.dataset_service import DatasetService
from app.services.ingestion_service import IngestionService
from app.services.preprocessing_service import PreprocessingService

router = APIRouter(prefix="/admin", tags=["admin"])

LATEST_INGESTION_SUMMARY = None


@router.get("/health")
def admin_health(
    session: Session = Depends(get_db_session),
    influx_provider: InfluxProvider = Depends(get_influx_provider),
) -> dict:
    postgres_ok = True
    influx_ok = True

    try:
        session.execute(text("SELECT 1"))
    except Exception:
        postgres_ok = False

    try:
        influx_ok = bool(influx_provider.client.ping())
    except Exception:
        influx_ok = False

    return {
        "status": "healthy" if postgres_ok and influx_ok else "degraded",
        "postgres": postgres_ok,
        "influx": influx_ok,
        "checked_at": datetime.now(tz=UTC).isoformat(),
    }


@router.get("/metrics-summary")
def metrics_summary() -> dict:
    return {
        "active_users_24h": 24,
        "forecast_requests_24h": 185,
        "notifications_sent_24h": 132,
        "average_forecast_latency_ms": 142,
        "ingestion_pipeline_status": "configured",
        "note": "Placeholder metrics. Wire this endpoint to monitoring/warehouse in production.",
    }


@router.post("/ingestion/run-current", response_model=IngestionTriggerResponse)
def run_current_ingestion(
    payload: IngestionRunCurrentRequest,
    ingestion_service: IngestionService = Depends(get_ingestion_service),
) -> IngestionTriggerResponse:
    global LATEST_INGESTION_SUMMARY
    summary = ingestion_service.ingest_current_from_cpcb(city=payload.city, limit=payload.limit)
    LATEST_INGESTION_SUMMARY = summary
    return IngestionTriggerResponse(message="Current ingestion run completed", summary=summary)


@router.post("/ingestion/backfill", response_model=IngestionTriggerResponse)
def run_backfill_ingestion(
    payload: IngestionBackfillRequest,
    ingestion_service: IngestionService = Depends(get_ingestion_service),
) -> IngestionTriggerResponse:
    global LATEST_INGESTION_SUMMARY
    summary = ingestion_service.backfill_from_openaq(
        city=payload.city,
        days=payload.days,
        start_at=payload.start_at,
        end_at=payload.end_at,
        limit=payload.limit,
    )
    LATEST_INGESTION_SUMMARY = summary
    return IngestionTriggerResponse(message="Historical backfill completed", summary=summary)


@router.post("/preprocessing/run", response_model=PreprocessingTriggerResponse)
def run_preprocessing(
    payload: PreprocessingRunRequest,
    preprocessing_service: PreprocessingService = Depends(get_preprocessing_service),
) -> PreprocessingTriggerResponse:
    summary = preprocessing_service.run_preprocessing(
        city=payload.city,
        station_id=payload.station_id,
        lookback_hours=payload.lookback_hours,
    )
    return PreprocessingTriggerResponse(message="Preprocessing run completed", summary=summary)


@router.get("/ingestion/summary", response_model=IngestionSummaryResponse)
def get_latest_ingestion_summary(
    ingestion_service: IngestionService = Depends(get_ingestion_service),
) -> IngestionSummaryResponse:
    summary = ingestion_service.get_latest_summary() or LATEST_INGESTION_SUMMARY
    return IngestionSummaryResponse(summary=summary)


@router.post("/datasets/build", response_model=DatasetBuildResponse)
def build_dataset(
    payload: TrainingDatasetRequest,
    dataset_service: DatasetService = Depends(get_dataset_service),
) -> DatasetBuildResponse:
    if payload.station_id:
        dataset = dataset_service.build_station_dataset(
            station_id=payload.station_id,
            start_at=payload.start_at,
            end_at=payload.end_at,
        )
    elif payload.city:
        dataset = dataset_service.build_city_dataset(
            city=payload.city,
            start_at=payload.start_at,
            end_at=payload.end_at,
        )
    else:
        dataset = dataset_service.build_city_dataset(city="Delhi")

    export_path = None
    if payload.export_path:
        export_path = dataset_service.export_training_dataset(dataset, payload.export_path)

    summary = dataset_service.dataset_summary(dataset, export_path=export_path)
    return DatasetBuildResponse(**summary)
