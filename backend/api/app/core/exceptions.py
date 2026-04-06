from collections.abc import Callable

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    status_code: int = 400
    code: str = "app_error"

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


class UnauthorizedException(AppException):
    status_code = 401
    code = "unauthorized"


class NotFoundException(AppException):
    status_code = 404
    code = "not_found"


class ConflictException(AppException):
    status_code = 409
    code = "conflict"


class ValidationException(AppException):
    status_code = 422
    code = "validation_error"


def _error_payload(exc: AppException) -> dict:
    return {
        "success": False,
        "error": {
            "code": exc.code,
            "message": exc.detail,
        },
    }


def register_exception_handlers(app: FastAPI) -> None:
    async def app_exception_handler(_: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content=_error_payload(exc))

    async def generic_exception_handler(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "internal_server_error",
                    "message": str(exc),
                },
            },
        )

    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
    async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": "http_error",
                    "message": str(exc.detail),
                },
            },
        )
