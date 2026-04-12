from app.core.config import get_settings
from app.integrations.cpcb_client import CPCBClient
from app.integrations.live_aqi_adapter import LiveAQIAdapter
from app.integrations.openaq_client import OpenAQClient


def get_live_aqi_adapter() -> LiveAQIAdapter:
    settings = get_settings()
    provider = settings.live_aqi_provider.lower().strip()

    if provider == "openaq":
        return OpenAQClient()
    return CPCBClient()
