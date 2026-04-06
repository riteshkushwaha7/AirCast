from fastapi import APIRouter, Depends

from app.api.deps import get_assistant_service, get_current_db_user
from app.models.user import User
from app.schemas.assistant import AssistantExplainRequest, AssistantExplainResponse
from app.services.assistant_service import AssistantService

router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.post("/explain", response_model=AssistantExplainResponse)
def explain_context(
    payload: AssistantExplainRequest,
    _: User = Depends(get_current_db_user),
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> AssistantExplainResponse:
    return assistant_service.explain(payload)
