import logging
from datetime import UTC, datetime, timedelta
from typing import Any, Iterable

from app.integrations.cpcb_client import CPCBClient
from app.integrations.openaq_client import OpenAQClient
from app.repositories.aqi_timeseries_repository import AQITimeSeriesRepository
from app.schemas.ingestion import IngestionSummary, NormalizedAQIRecord
from app.utils.validators import validate_pollutant_value

logger = logging.getLogger(__name__)


class IngestionService:
    def __init__(
        self,
        timeseries_repository: AQITimeSeriesRepository,
        cpcb_client: CPCBClient | None = None,
        openaq_client: OpenAQClient | None = None,
    ) -> None:
        self.timeseries_repository = timeseries_repository
        self.cpcb_client = cpcb_client or CPCBClient()
        self.openaq_client = openaq_client or OpenAQClient()
        self._latest_summary: IngestionSummary | None = None

    def ingest_current_from_cpcb(self, city: str | None = None, limit: int | None = None) -> IngestionSummary:
        fetched = self.cpcb_client.fetch_current_records(city=city, limit=limit)
        return self.ingest_records(records=fetched, source="cpcb", mode="current")

    def backfill_from_openaq(
        self,
        city: str,
        days: int = 30,
        start_at: datetime | None = None,
        end_at: datetime | None = None,
        limit: int | None = None,
    ) -> IngestionSummary:
        end_dt = _utc(end_at) if end_at else datetime.now(tz=UTC)
        start_dt = _utc(start_at) if start_at else end_dt - timedelta(days=days)
        fetched = self.openaq_client.fetch_historical_records(city=city, start_at=start_dt, end_at=end_dt, limit=limit)
        return self.ingest_records(records=fetched, source="openaq", mode="historical_backfill")

    def ingest_records(self, records: Iterable[NormalizedAQIRecord | dict[str, Any]], source: str, mode: str) -> IngestionSummary:
        started_at = datetime.now(tz=UTC)
        input_records = list(records)
        fetched_count = len(input_records)
        normalized = self.normalize_records(input_records)
        normalization_failures = fetched_count - len(normalized)

        valid_records, invalid_reasons = self.validate_records(normalized)
        deduped_records, duplicate_count = self.deduplicate_records(valid_records)
        written_count = self.timeseries_repository.write_raw_records(deduped_records)

        ended_at = datetime.now(tz=UTC)
        summary = IngestionSummary(
            source=source,
            mode=mode,
            fetched_count=fetched_count,
            valid_count=len(valid_records),
            invalid_count=normalization_failures + len(invalid_reasons),
            duplicate_count=duplicate_count,
            written_count=written_count,
            started_at=started_at,
            ended_at=ended_at,
            invalid_reasons=(invalid_reasons + (["normalization_failed"] * normalization_failures))[:25],
        )
        self._latest_summary = summary
        logger.info(
            "Ingestion completed source=%s mode=%s fetched=%s valid=%s invalid=%s duplicate=%s written=%s",
            source,
            mode,
            fetched_count,
            len(valid_records),
            len(invalid_reasons),
            duplicate_count,
            written_count,
        )
        return summary

    def normalize_records(self, records: Iterable[NormalizedAQIRecord | dict[str, Any]]) -> list[NormalizedAQIRecord]:
        normalized: list[NormalizedAQIRecord] = []
        for item in records:
            try:
                if isinstance(item, NormalizedAQIRecord):
                    normalized.append(item)
                elif isinstance(item, dict):
                    normalized.append(NormalizedAQIRecord.model_validate(item))
                else:
                    normalized.append(NormalizedAQIRecord.model_validate(item.__dict__))
            except Exception as exc:
                logger.warning("Failed to normalize AQI record %s: %s", item, exc)
        return normalized

    def validate_records(self, records: Iterable[NormalizedAQIRecord]) -> tuple[list[NormalizedAQIRecord], list[str]]:
        valid: list[NormalizedAQIRecord] = []
        invalid_reasons: list[str] = []

        for record in records:
            try:
                if record.observed_at is None:
                    raise ValueError("observed_at is required")
                if record.station_id is None and record.city is None and (record.latitude is None or record.longitude is None):
                    raise ValueError("station_id or location data is required")
                if record.aqi is not None and record.aqi > 1000:
                    raise ValueError("aqi beyond supported threshold")

                validate_pollutant_value("pm25", record.pm25)
                validate_pollutant_value("pm10", record.pm10)
                validate_pollutant_value("no2", record.no2)
                validate_pollutant_value("so2", record.so2)
                validate_pollutant_value("co", record.co)
                validate_pollutant_value("o3", record.o3)
                validate_pollutant_value("nh3", record.nh3)

                valid.append(record)
            except Exception as exc:
                invalid_reasons.append(str(exc))

        return valid, invalid_reasons

    def deduplicate_records(self, records: Iterable[NormalizedAQIRecord]) -> tuple[list[NormalizedAQIRecord], int]:
        output: list[NormalizedAQIRecord] = []
        seen: set[str] = set()
        duplicate_count = 0

        for record in records:
            key = self._dedupe_key(record)
            if key in seen:
                duplicate_count += 1
                continue
            seen.add(key)
            output.append(record)

        return output, duplicate_count

    def get_latest_summary(self) -> IngestionSummary | None:
        return self._latest_summary

    def _dedupe_key(self, record: NormalizedAQIRecord) -> str:
        observed = _utc(record.observed_at).isoformat()
        if record.station_id:
            return f"{record.source}|{record.station_id}|{observed}"
        city = (record.city or "unknown").lower()
        lat = record.latitude if record.latitude is not None else "na"
        lon = record.longitude if record.longitude is not None else "na"
        return f"{record.source}|{city}|{lat}|{lon}|{observed}"


def _utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)
