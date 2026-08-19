"""Feeds endpoints under ``/v1/feeds/*``."""

from __future__ import annotations

from typing import Any

from .._http import AsyncBaseHTTPClient, BaseHTTPClient
from ..models import FeedItem, WallstrankModel

__all__ = [
    "AsyncFeedsResource",
    "FeedsResource",
    "FundsPortfoliosFeedResponse",
]


class FundsPortfoliosFeedResponse(WallstrankModel):
    """Response body for ``/v1/feeds/funds-portfolios``."""

    page: int
    page_size: int
    has_more_pages: bool
    items: list[FeedItem]


def _feed_params(*, page: int | None, page_size: int | None) -> dict[str, Any]:
    return {"page": page, "page_size": page_size}


class FeedsResource:
    """Synchronous feed endpoints."""

    def __init__(self, client: BaseHTTPClient) -> None:
        self._client = client

    def funds_portfolios(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
    ) -> FundsPortfoliosFeedResponse:
        payload = self._client.get(
            "/v1/feeds/funds-portfolios",
            params=_feed_params(page=page, page_size=page_size),
        )
        return FundsPortfoliosFeedResponse.model_validate(payload)


class AsyncFeedsResource:
    """Asynchronous feed endpoints."""

    def __init__(self, client: AsyncBaseHTTPClient) -> None:
        self._client = client

    async def funds_portfolios(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
    ) -> FundsPortfoliosFeedResponse:
        payload = await self._client.get(
            "/v1/feeds/funds-portfolios",
            params=_feed_params(page=page, page_size=page_size),
        )
        return FundsPortfoliosFeedResponse.model_validate(payload)
