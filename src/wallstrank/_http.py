"""Low-level HTTP transport for the Wall St. Rank API.

Provides synchronous and asynchronous base clients built on top of
:mod:`httpx`, with retry, error mapping, and consistent parameter encoding.
"""

from __future__ import annotations

import time
from collections.abc import Iterable, Mapping
from enum import Enum
from types import TracebackType
from typing import Any, Final, Self
from urllib.parse import quote

import httpx

from .__about__ import __version__
from .exceptions import APIError, WallstrankError, error_for_status

__all__ = [
    "DEFAULT_BASE_URL",
    "DEFAULT_TIMEOUT",
    "AsyncBaseHTTPClient",
    "BaseHTTPClient",
    "encode_params",
]

DEFAULT_BASE_URL: Final[str] = "https://api.wallstrank.com"
DEFAULT_TIMEOUT: Final[float] = 30.0
DEFAULT_MAX_RETRIES: Final[int] = 3
DEFAULT_RETRY_BACKOFF: Final[float] = 0.5
_RETRYABLE_STATUS_CODES: Final[frozenset[int]] = frozenset({408, 429, 500, 502, 503, 504})
_USER_AGENT: Final[str] = f"wallstrank-py/{__version__}"


def _encode_path_segment(value: str) -> str:
    """Percent-encode a single path segment, without touching ``/``.

    Wall St. Rank tickers usually contain only ``[A-Z0-9._-]`` but user input
    can vary, so we defensively encode.
    """

    return quote(value, safe="")


def _flatten_value(value: Any) -> str | None:
    """Normalise a single query-parameter value for the API.

    - ``None`` values are stripped (so callers can pass optional kwargs directly).
    - ``bool`` becomes lowercase JSON style ("true"/"false").
    - :class:`Enum` values use their ``.value``.
    - Everything else is coerced via ``str``.
    """

    if value is None:
        return None
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, Enum):
        return str(value.value)
    return str(value)


def encode_params(params: Mapping[str, Any] | None) -> dict[str, str]:
    """Encode a params mapping for use as HTTP query parameters.

    Iterables are joined with commas (matching the API's convention for
    parameters like ``status`` and ``market_cap``). ``None`` values are dropped.
    """

    if not params:
        return {}
    encoded: dict[str, str] = {}
    for key, raw in params.items():
        if raw is None:
            continue
        if isinstance(raw, str | bytes):
            flat = _flatten_value(raw)
        elif isinstance(raw, Iterable) and not isinstance(raw, Mapping):
            parts = [flat for flat in (_flatten_value(item) for item in raw) if flat is not None]
            flat = ",".join(parts) if parts else None
        else:
            flat = _flatten_value(raw)
        if flat is None or flat == "":
            continue
        encoded[key] = flat
    return encoded


class _BaseClient:
    """Common configuration shared by sync/async clients."""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_backoff: float = DEFAULT_RETRY_BACKOFF,
        user_agent: str | None = None,
    ) -> None:
        if not api_key:
            raise WallstrankError("An API key is required to instantiate a Wall St. Rank client.")
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._max_retries = max_retries
        self._retry_backoff = retry_backoff
        self._user_agent = user_agent or _USER_AGENT

    @property
    def base_url(self) -> str:
        return self._base_url

    def _default_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Accept": "application/json",
            "User-Agent": self._user_agent,
        }

    def _build_url(self, path: str) -> str:
        if not path.startswith("/"):
            path = f"/{path}"
        return f"{self._base_url}{path}"

    def _parse_response(self, response: httpx.Response) -> Any:
        """Parse and validate an HTTP response, raising typed errors on failure."""

        try:
            body: Any = response.json() if response.content else None
        except ValueError:
            body = response.text or None

        if response.is_success:
            return body

        message = _extract_error_message(body) or response.reason_phrase or "API request failed"
        raise error_for_status(
            response.status_code,
            message=message,
            response_body=body,
            request_url=str(response.request.url) if response.request else None,
        )


def _extract_error_message(body: Any) -> str | None:
    """Best-effort extraction of an error message from a response body."""

    if isinstance(body, Mapping):
        for key in ("message", "error", "detail"):
            value = body.get(key)
            if isinstance(value, str) and value:
                return value
        error = body.get("error")
        if isinstance(error, Mapping):
            msg = error.get("message")
            if isinstance(msg, str) and msg:
                return msg
    if isinstance(body, str):
        return body or None
    return None


class BaseHTTPClient(_BaseClient):
    """Synchronous transport used by :class:`wallstrank.WallstrankClient`."""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_backoff: float = DEFAULT_RETRY_BACKOFF,
        user_agent: str | None = None,
        http_client: httpx.Client | None = None,
    ) -> None:
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            retry_backoff=retry_backoff,
            user_agent=user_agent,
        )
        self._owns_client = http_client is None
        self._client = http_client or httpx.Client(timeout=self._timeout)

    def close(self) -> None:
        """Close the underlying HTTP client if it was created by this instance."""

        if self._owns_client:
            self._client.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.close()

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> Any:
        url = self._build_url(path)
        query = encode_params(params)
        last_error: Exception | None = None
        for attempt in range(self._max_retries + 1):
            try:
                response = self._client.request(
                    method,
                    url,
                    params=query,
                    headers=self._default_headers(),
                )
            except httpx.TransportError as exc:
                last_error = exc
                if attempt >= self._max_retries:
                    raise WallstrankError(f"Network error contacting Wall St. Rank: {exc}") from exc
                time.sleep(self._retry_backoff * (2**attempt))
                continue

            if response.status_code in _RETRYABLE_STATUS_CODES and attempt < self._max_retries:
                time.sleep(self._retry_backoff * (2**attempt))
                continue

            return self._parse_response(response)

        # Unreachable in practice; keep for type checkers.
        assert last_error is not None
        raise WallstrankError("Wall St. Rank request failed") from last_error

    def get(self, path: str, *, params: Mapping[str, Any] | None = None) -> Any:
        return self._request("GET", path, params=params)


class AsyncBaseHTTPClient(_BaseClient):
    """Asynchronous transport used by :class:`wallstrank.AsyncWallstrankClient`."""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_backoff: float = DEFAULT_RETRY_BACKOFF,
        user_agent: str | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            retry_backoff=retry_backoff,
            user_agent=user_agent,
        )
        self._owns_client = http_client is None
        self._client = http_client or httpx.AsyncClient(timeout=self._timeout)

    async def aclose(self) -> None:
        """Close the underlying HTTP client if it was created by this instance."""

        if self._owns_client:
            await self._client.aclose()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.aclose()

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> Any:
        import asyncio

        url = self._build_url(path)
        query = encode_params(params)
        last_error: Exception | None = None
        for attempt in range(self._max_retries + 1):
            try:
                response = await self._client.request(
                    method,
                    url,
                    params=query,
                    headers=self._default_headers(),
                )
            except httpx.TransportError as exc:
                last_error = exc
                if attempt >= self._max_retries:
                    raise WallstrankError(f"Network error contacting Wall St. Rank: {exc}") from exc
                await asyncio.sleep(self._retry_backoff * (2**attempt))
                continue

            if response.status_code in _RETRYABLE_STATUS_CODES and attempt < self._max_retries:
                await asyncio.sleep(self._retry_backoff * (2**attempt))
                continue

            return self._parse_response(response)

        assert last_error is not None
        raise WallstrankError("Wall St. Rank request failed") from last_error

    async def get(self, path: str, *, params: Mapping[str, Any] | None = None) -> Any:
        return await self._request("GET", path, params=params)


# Re-exported so resources can build URLs consistently.
encode_path_segment = _encode_path_segment


# Silence unused-import warnings for consumers of ``APIError`` re-export.
_ = APIError
