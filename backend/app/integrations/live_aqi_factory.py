from app.core.config import get_settings
from app.integrations.cpcb_client import CPCBClient
from app.integrations.live_aqi_adapter import LiveAQIAdapter
from app.integrations.waqi_client import WAQIClient


def get_live_aqi_adapter() -> LiveAQIAdapter:
    settings = get_settings()
    provider = settings.live_aqi_provider.lower().strip()

    if provider == "waqi":
        return WAQIClient()
    return CPCBClient()
