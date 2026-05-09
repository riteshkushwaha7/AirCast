from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.forecast_log import ForecastLog


class ForecastRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_log(self, log: ForecastLog) -> ForecastLog:
        self.session.add(log)
        self.session.commit()
        self.session.refresh(log)
        return log

    def list_latest_for_location(self, location_id, limit: int = 20) -> list[ForecastLog]:
        stmt = (
            select(ForecastLog)
            .where(ForecastLog.location_id == location_id)
            .order_by(ForecastLog.generated_at.desc())
            .limit(limit)
        )
        return list(self.session.execute(stmt).scalars())
