"""Exception hierarchy for the Wall St. Rank API client."""

from __future__ import annotations

from typing import Any

__all__ = [
    "APIError",
    "AuthenticationError",
    "BadRequestError",
    "ForbiddenError",
    "NotFoundError",
    "RequestFailedError",
    "ServerError",
    "WallstrankError",
]


class WallstrankError(Exception):
    """Base class for all wallstrank-py errors."""


class APIError(WallstrankError):
    """Raised when the Wall St. Rank API returns a non-2xx response.

    Attributes:
        status_code: The HTTP status code returned by the API.
        message: A human-readable error message.
        response_body: The raw parsed response body, if any.
        request_url: The URL of the failing request.
    """

    status_code: int

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        response_body: Any = None,
        request_url: str | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_body = response_body
        self.request_url = request_url

    def __str__(self) -> str:
        prefix = f"[{self.status_code}] " if self.status_code else ""
        return f"{prefix}{self.message}"


class BadRequestError(APIError):
    """HTTP 400 - The request was unacceptable."""


class AuthenticationError(APIError):
    """HTTP 401 - No valid API key was provided."""


class RequestFailedError(APIError):
    """HTTP 402 - The parameters were valid but the request failed."""


class ForbiddenError(APIError):
    """HTTP 403 - The API key doesn't have permissions to perform the request."""


class NotFoundError(APIError):
    """HTTP 404 - The requested resource doesn't exist."""


class ServerError(APIError):
    """HTTP 5xx - Something went wrong on Wall St. Rank's servers."""


_STATUS_TO_EXCEPTION: dict[int, type[APIError]] = {
    400: BadRequestError,
    401: AuthenticationError,
    402: RequestFailedError,
    403: ForbiddenError,
    404: NotFoundError,
}


def error_for_status(
    status_code: int,
    *,
    message: str,
    response_body: Any = None,
    request_url: str | None = None,
) -> APIError:
    """Return the appropriate :class:`APIError` subclass for a given status code."""

    if 500 <= status_code < 600:
        exc_cls: type[APIError] = ServerError
    else:
        exc_cls = _STATUS_TO_EXCEPTION.get(status_code, APIError)
    return exc_cls(
        message,
        status_code=status_code,
        response_body=response_body,
        request_url=request_url,
    )
