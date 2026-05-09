from typing import Any


def success_response(data: Any, status: int = 200) -> tuple[dict, int]:
    return {"success": True, "data": data}, status
