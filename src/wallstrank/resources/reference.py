"""Reference endpoints: sectors and industries."""

from __future__ import annotations

from pydantic import TypeAdapter

from .._http import AsyncBaseHTTPClient, BaseHTTPClient
from ..models import Industry, Sector

__all__ = [
    "AsyncReferenceResource",
    "ReferenceResource",
]

_SECTORS_ADAPTER = TypeAdapter(list[Sector])
_INDUSTRIES_ADAPTER = TypeAdapter(list[Industry])


def _extract_sectors(payload: object) -> list[Sector]:
    if isinstance(payload, dict) and "sectors" in payload:
        return _SECTORS_ADAPTER.validate_python(payload["sectors"])
    return _SECTORS_ADAPTER.validate_python(payload)


def _extract_industries(payload: object) -> list[Industry]:
    if isinstance(payload, dict) and "industries" in payload:
        return _INDUSTRIES_ADAPTER.validate_python(payload["industries"])
    return _INDUSTRIES_ADAPTER.validate_python(payload)


class ReferenceResource:
    """Synchronous access to the sectors and industries reference endpoints."""

    def __init__(self, client: BaseHTTPClient) -> None:
        self._client = client

    def list_sectors(self) -> list[Sector]:
        """Return every sector in Wall St. Rank's taxonomy."""

        payload = self._client.get("/v1/sectors")
        return _extract_sectors(payload)

    def list_industries(self) -> list[Industry]:
        """Return every industry in Wall St. Rank's taxonomy."""

        payload = self._client.get("/v1/industries")
        return _extract_industries(payload)


class AsyncReferenceResource:
    """Asynchronous access to the sectors and industries reference endpoints."""

    def __init__(self, client: AsyncBaseHTTPClient) -> None:
        self._client = client

    async def list_sectors(self) -> list[Sector]:
        payload = await self._client.get("/v1/sectors")
        return _extract_sectors(payload)

    async def list_industries(self) -> list[Industry]:
        payload = await self._client.get("/v1/industries")
        return _extract_industries(payload)
