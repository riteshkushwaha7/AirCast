from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.influx import InfluxProvider, get_influx_provider
from app.db.postgres import get_db_session

router = APIRouter(prefix="/admin", tags=["admin"])


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
        influx_ok = influx_provider.client.ping()
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
        "note": "Placeholder metrics. Wire to monitoring/warehouse in production.",
    }
