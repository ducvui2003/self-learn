"""Shared API exceptions (handled globally by RestDispatcherView).

Spring equivalent: custom exceptions handled by @RestControllerAdvice + @ExceptionHandler.
"""


class ApiError(Exception):
    """Base structured REST API exception."""

    def __init__(self, code, message, status=400, details=None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status = status
        self.details = details


class ValidationError(ApiError):
    """400 Bad Request with field-level validation details (like Spring MethodArgumentNotValidException)."""

    def __init__(self, details, message="Input validation failed."):
        super().__init__(
            code="E_VALIDATION",
            message=message,
            status=400,
            details=details,
        )


class NotFoundError(ApiError):
    """404 Not Found."""

    def __init__(self, message):
        super().__init__(code="E_NOT_FOUND", message=message, status=404)


class ConflictError(ApiError):
    """409 Conflict (duplicate key or optimistic locking version mismatch)."""

    def __init__(self, code, message):
        super().__init__(code=code, message=message, status=409)
