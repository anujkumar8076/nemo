import logging
from typing import Any
from uuid import UUID, uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHttpException

from autodev_api.schemas import ErrorDetail, ErrorResponse

logger = logging.getLogger(__name__)


class ApiError(Exception):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        *,
        details: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details
        self.headers = headers


def correlation_id(request: Request) -> UUID:
    value = getattr(request.state, "correlation_id", None)
    return value if isinstance(value, UUID) else uuid4()


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHttpException)
    async def http_error_handler(request: Request, error: StarletteHttpException) -> JSONResponse:
        code = "not_found" if error.status_code == 404 else "http_error"
        payload = ErrorResponse(
            error=ErrorDetail(
                code=code,
                message=str(error.detail),
                correlation_id=correlation_id(request),
            )
        )
        return JSONResponse(
            status_code=error.status_code,
            content=payload.model_dump(mode="json"),
            headers=error.headers,
        )

    @app.exception_handler(ApiError)
    async def api_error_handler(request: Request, error: ApiError) -> JSONResponse:
        payload = ErrorResponse(
            error=ErrorDetail(
                code=error.code,
                message=error.message,
                correlation_id=correlation_id(request),
                details=error.details,
            )
        )
        return JSONResponse(
            status_code=error.status_code,
            content=payload.model_dump(mode="json"),
            headers=error.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, error: RequestValidationError
    ) -> JSONResponse:
        details: list[dict[str, Any]] = [
            {key: value for key, value in item.items() if key != "ctx"} for item in error.errors()
        ]
        payload = ErrorResponse(
            error=ErrorDetail(
                code="validation_error",
                message="The request did not pass validation.",
                correlation_id=correlation_id(request),
                details=details,
            )
        )
        return JSONResponse(status_code=422, content=payload.model_dump(mode="json"))

    @app.exception_handler(Exception)
    async def unexpected_error_handler(request: Request, error: Exception) -> JSONResponse:
        request_correlation_id = correlation_id(request)
        logger.exception(
            "Unhandled API exception (correlation_id=%s)",
            request_correlation_id,
            exc_info=error,
        )
        payload = ErrorResponse(
            error=ErrorDetail(
                code="internal_error",
                message="The request could not be completed.",
                correlation_id=request_correlation_id,
            )
        )
        return JSONResponse(status_code=500, content=payload.model_dump(mode="json"))
