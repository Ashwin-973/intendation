

from __future__ import annotations

from typing import Any


'''BASE'''

class ShelbyBaseException(Exception):
    """
    root of every custom exception in this project
    """
    status_code:int=500
    error_code:str="INTERNAL_SERVER_ERROR"
    default_message:str="An unexpected error occurred"

    def __init__(
            self,
            message:str|None=None,
            *,
            detail: Any = None,
            context: dict[str, Any] | None = None,
    )->None:
        self.message=message or self.default_message
        self.detail=detail
        self.context:dict[str,Any]=context or {}

        super().__init__(self.message)

    def __repr__(self)->str:
        return (
            f"{self.__class__.__name__}("
            f"status_code={self.status_code}, "
            f"error_code={self.error_code!r}, "
            f"message={self.message!r})"
        )
        

'''400 - Validation / Bad Request'''

class ValidationException(ShelbyBaseException):
    """Raised when incoming data fails business-level validation"""

    status_code=400
    error_code="VALIDATION_ERROR"
    default_message="The provided data is invalid"

class InvalidPriceFormatException(ValidationException):
    """Raised when a price string doesn't match the expected pattern"""

    error_code = "INVALID_PRICE_FORMAT"
    default_message = "Price must follow the format '₹X.XX Cr' (e.g. '₹10.37 Cr')"

class InvalidIDException(ValidationException):
    """Raised when a path/query parameter ID is not a positive integer"""

    error_code = "INVALID_ID"
    default_message = "ID must be a positive integer"

class EmptyPayloadException(ValidationException):
    """Raised when an update/create request body contains no usable fields"""

    error_code = "EMPTY_PAYLOAD"
    default_message = "Request body must contain at least one field"

'''401/403 - AUTHN/AUTHZ'''

class AuthenticationException(ShelbyBaseException):
    status_code = 401
    error_code = "UNAUTHENTICATED"
    default_message = "Authentication credentials are missing or invalid"

class AuthorizationException(ShelbyBaseException):
    status_code = 403
    error_code = "FORBIDDEN"
    default_message = "You do not have permission to perform this action"


'''404 - NOT FOUND'''

class NotFoundException(ShelbyBaseException):
    status_code = 404
    error_code = "NOT_FOUND"
    default_message = "The requested resource was not found"

class CarNotFoundException(ShelbyBaseException):
    error_code = "CAR_NOT_FOUND"
    default_message = "No car with that ID exists"


'''408 - REQUEST TIMEOUT'''

class RequestTimeoutException(ShelbyBaseException):
    status_code = 408
    error_code = "REQUEST_TIMEOUT"
    default_message = "The request took too long to process"


'''409 - CONCFLICT/DUPLICATE'''

class ConflictException(ShelbyBaseException):
    status_code = 409
    error_code = "CONFLICT"
    default_message = "A resource conflict occurred"


class DuplicateCarException(ConflictException):
    error_code = "DUPLICATE_CAR"
    default_message = "A car with the same name and brand already exists"


'''422 - UNPROCESSABLE'''

class UnprocessableException(ShelbyBaseException):
    status_code = 422
    error_code = "UNPROCESSABLE_ENTITY"
    default_message = "The request is well-formed but semantically incorrect."


'''429 - RATE LIMITING'''

class RateLimitException(ShelbyBaseException):
    status_code = 429
    error_code = "RATE_LIMIT_EXCEEDED"
    default_message = "Too many requests. Please slow down."


'''500/503 - SERVER SIDE'''

class InternalServerException(ShelbyBaseException):
    status_code = 500
    error_code = "INTERNAL_ERROR"
    default_message = "An internal server error occurred."


class DatabaseException(InternalServerException):
    error_code = "DATABASE_ERROR"
    default_message = "A database operation failed."


class ServiceUnavailableException(ShelbyBaseException):
    status_code = 503
    error_code = "SERVICE_UNAVAILABLE"
    default_message = "The service is temporarily unavailable."