'''
Global Exception Handler Middleware
A place where every exception gets caught and converted to HTTP responses [JSON]
'''

from __future__ import annotations

import traceback
import uuid
from typing import Callable

from fastapi import Request,Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse

from cars.server.src.exceptions1 import ShelbyBaseException
from src.logger import get_logger
from src.schemas import ErrorResponse

logger=get_logger(__name__)


'''HELPER (for consistent error responses)'''

def _build_error_response(
    *,
    status_code: int,
    error_code: str,
    message: str,
    path: str,
    detail: object = None,
)->JSONResponse:
    body=ErrorResponse(
        error=True,
        error_code=error_code,
        message=message,
        detail=detail,
        path=path,
        status_code=status_code)

    return JSONResponse(status_code=status_code,content=body.model_dump())


'''STARLETTE MIDDLEWARE (catches everything)'''

class ExceptionMiddleware(BaseHTTPMiddleware):
    """
    the catch-all middleware that wraps every request/response cycle.

    execution order (outermost first):
        ExceptionMiddleware → ... → Router → Service → Exception raised
                                                              ↓
                            ExceptionMiddleware catches it here
    """

    async def dispatch(self, request:Request, call_next:Callable)->StarletteResponse:
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id=request_id

        logger.info(
            "→ %s %s",
            request.method,  #!log this
            request.url.path, #!log this
            extra={"request_id":request_id,"client":request.client and request.client.host} #!log this
        )

        try:
            response:Response=await call_next(request)

            logger.info(
                "← %s %s [%d]",
                request.method,
                request.url.path,
                response.status_code,
                extra={
                    "request_id":request_id,
                    "status":response.status_code
                }
            )

            return response
        
        except ShelbyBaseException as exc:
            logger.warning(
                "Application exception: %s",
                exc.message,
                extra={
                    "request_id":request_id,
                    "error_code":exc.error_code,
                    "status_code":exc.status_code,
                    **exc.context         #!wtf is this?
                }
            )
            return _build_error_response(
                status_code=exc.status_code,
                error_code=exc.error_code,
                message=exc.message,
                path=request.url.path,
                detail=exc.detail
            )
        
        except Exception as exc:

            tb=traceback.format_exc() #*returns the entire stack trace of the most recent exception
            logger.error(
                "Unhandled exception on %s %s: %s",
                request.method,
                request.url.path,
                exc,
                extra={
                    "request_id":request_id,
                    "traceback":tb
                }
            )

            return _build_error_response(
                status_code=500,
                error_code="INTERNAL SERVER ERROR",
                message="An unexpected internal error occurred. Please try again later.",
                path=request.path.url,
                detail=None #!never leak tracebacks to clients.
            )

'''FAST API (exceptions registration)'''
async def pydantic_validation_exception_handler(
        request:Request,exc:RequestValidationError
)->JSONResponse:
    """
    FastAPI raises RequestValidationError for request body / query param
    validation failures.  We reformat Pydantic's verbose errors into our
    clean envelope.
    """
    errors=[]
    '''
    exc.errors() -> example
    [
    {
        "type": "value_error",
        "loc": ("body", "make"),
        "msg": "string should have at least 2 characters",
        "input": "A",
        "ctx": {"min_length": 2}
    },
    {
        "type": "int_parsing",
        "loc": ("body", "price"),
        "msg": "Input should be a valid integer",
        "input": "expensive",
        "ctx": {"error": "invalid literal..."}
    },
    {
        "type": "missing",
        "loc": ("body", "year"),
        "msg": "Field required",
        "input": {"make": "Ferrari"},
        "ctx": None
    }
]
'''
    for err in exc.errors():
        loc=" → ".join(str(p) for p in err["loc"] if p!="body")
        errors.append(
            {
                "field":loc or None,
                "message":err["msg"]
            }
        )

    logger.warning(
        "Request validation failed",
        extra={
            "path":request.path.url,
            "errors":errors
        }
    )

    return _build_error_response(
        status_code=422,
        error_code="VALIDATION_ERROR",
        message="One or more fields failed validation.",
        path=request.url.path,
        detail=errors,
    )



async def shelby_exception_handler(
        request:Request,exc:ShelbyBaseException
)->JSONResponse:
    """
    handles ShelbyBaseException raised inside FastAPI route handlers
    (before the middleware gets a chance to catch them).
    """

    logger.warning(
        "Application exception (handler): %s",
        exc.message,
        extra={
            "error_code":exc.error_code,
            "path":request.url.path,
            **exc.context
        }
    )

    return _build_error_response(
        status_code=exc.status_code,
        error_code=exc.error_code,
        message=exc.message,
        path=request.url.path,
        detail=exc.detail,
    )

async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    fallback for any exception not caught by the middleware
    """
    logger.exception(
        "Unhandled exception (handler): %s %s",
        request.method,
        request.url.path,
    )
    return _build_error_response(
        status_code=500,
        error_code="INTERNAL_ERROR",
        message="An unexpected internal error occurred.",
        path=request.url.path,
    )
