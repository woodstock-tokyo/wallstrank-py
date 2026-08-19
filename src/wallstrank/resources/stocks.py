"""Stocks endpoints: fund holders, fund stats, fund confidence."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from .._http import AsyncBaseHTTPClient, BaseHTTPClient, encode_path_segment
from ..enums import FundHolderSortBy, HolderStatus, SecurityType, SortDir
from ..models import (
    FundSummary,
    Insight,
    PositionInsight,
    PositionRef,
    TradeInsight,
    WallstrankModel,
)

__all__ = [
    "AsyncStocksResource",
    "FundConfidenceResponse",
    "FundHolder",
    "FundHoldersResponse",
    "FundStats",
    "FundStatsResponse",
    "StocksResource",
]


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class FundHolder(PositionRef):
    """A single row in the fund-holders response."""

    fund: FundSummary
    portfolio_rank: int | None = None


class FundHoldersResponse(WallstrankModel):
    """Response body for ``/v1/stocks/:id_or_ticker/fund-holders``."""

    page: int
    page_size: int
    has_more_pages: bool
    reporting_year: int
    reporting_quarter: int
    holders: list[FundHolder]


class FundStats(WallstrankModel):
    """Aggregate stats on the number of funds holding a stock."""

    total_positions: int
    new_positions: int
    increased_positions: int
    maintained_positions: int
    reduced_positions: int
    closed_positions: int


class FundStatsResponse(WallstrankModel):
    """Response body for ``/v1/stocks/:id_or_ticker/fund-stats``."""

    reporting_year: int
    reporting_quarter: int
    holders: FundStats


class FundConfidenceResponse(WallstrankModel):
    """Response body for ``/v1/stocks/:ticker/fund-confidence``."""

    insights: list[PositionInsight | TradeInsight | Insight]


# ---------------------------------------------------------------------------
# Request helpers
# ---------------------------------------------------------------------------


def _fund_holders_params(
    *,
    year: int | None,
    quarter: int | None,
    status: HolderStatus | str | Iterable[HolderStatus | str] | None,
    security_type: SecurityType | str | None,
    sort_by: FundHolderSortBy | str | None,
    sort_dir: SortDir | str | None,
    page: int | None,
    page_size: int | None,
) -> dict[str, Any]:
    return {
        "year": year,
        "quarter": quarter,
        "status": status,
        "security_type": security_type,
        "sort_by": sort_by,
        "sort_dir": sort_dir,
        "page": page,
        "page_size": page_size,
    }


def _fund_stats_params(
    *,
    year: int | None,
    quarter: int | None,
    include_ongoing: bool | None,
) -> dict[str, Any]:
    return {
        "year": year,
        "quarter": quarter,
        "include_ongoing": include_ongoing,
    }


# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------


class _StocksBase:
    @staticmethod
    def _holders_path(id_or_ticker: str) -> str:
        return f"/v1/stocks/{encode_path_segment(id_or_ticker)}/fund-holders"

    @staticmethod
    def _stats_path(id_or_ticker: str) -> str:
        return f"/v1/stocks/{encode_path_segment(id_or_ticker)}/fund-stats"

    @staticmethod
    def _confidence_path(ticker: str) -> str:
        return f"/v1/stocks/{encode_path_segment(ticker)}/fund-confidence"


class StocksResource(_StocksBase):
    """Synchronous stocks endpoints."""

    def __init__(self, client: BaseHTTPClient) -> None:
        self._client = client

    def fund_holders(
        self,
        id_or_ticker: str,
        *,
        year: int | None = None,
        quarter: int | None = None,
        status: HolderStatus | str | Iterable[HolderStatus | str] | None = None,
        security_type: SecurityType | str | None = None,
        sort_by: FundHolderSortBy | str | None = None,
        sort_dir: SortDir | str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> FundHoldersResponse:
        """Fetch the funds holding ``id_or_ticker`` for a given period."""

        payload = self._client.get(
            self._holders_path(id_or_ticker),
            params=_fund_holders_params(
                year=year,
                quarter=quarter,
                status=status,
                security_type=security_type,
                sort_by=sort_by,
                sort_dir=sort_dir,
                page=page,
                page_size=page_size,
            ),
        )
        return FundHoldersResponse.model_validate(payload)

    def fund_stats(
        self,
        id_or_ticker: str,
        *,
        year: int | None = None,
        quarter: int | None = None,
        include_ongoing: bool | None = None,
    ) -> FundStatsResponse:
        """Fetch fund-position counts for ``id_or_ticker``."""

        payload = self._client.get(
            self._stats_path(id_or_ticker),
            params=_fund_stats_params(
                year=year,
                quarter=quarter,
                include_ongoing=include_ongoing,
            ),
        )
        return FundStatsResponse.model_validate(payload)

    def fund_confidence(self, ticker: str) -> FundConfidenceResponse:
        """Fetch fund-manager confidence insights for ``ticker``."""

        payload = self._client.get(self._confidence_path(ticker))
        return FundConfidenceResponse.model_validate(payload)


class AsyncStocksResource(_StocksBase):
    """Asynchronous stocks endpoints."""

    def __init__(self, client: AsyncBaseHTTPClient) -> None:
        self._client = client

    async def fund_holders(
        self,
        id_or_ticker: str,
        *,
        year: int | None = None,
        quarter: int | None = None,
        status: HolderStatus | str | Iterable[HolderStatus | str] | None = None,
        security_type: SecurityType | str | None = None,
        sort_by: FundHolderSortBy | str | None = None,
        sort_dir: SortDir | str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> FundHoldersResponse:
        payload = await self._client.get(
            self._holders_path(id_or_ticker),
            params=_fund_holders_params(
                year=year,
                quarter=quarter,
                status=status,
                security_type=security_type,
                sort_by=sort_by,
                sort_dir=sort_dir,
                page=page,
                page_size=page_size,
            ),
        )
        return FundHoldersResponse.model_validate(payload)

    async def fund_stats(
        self,
        id_or_ticker: str,
        *,
        year: int | None = None,
        quarter: int | None = None,
        include_ongoing: bool | None = None,
    ) -> FundStatsResponse:
        payload = await self._client.get(
            self._stats_path(id_or_ticker),
            params=_fund_stats_params(
                year=year,
                quarter=quarter,
                include_ongoing=include_ongoing,
            ),
        )
        return FundStatsResponse.model_validate(payload)

    async def fund_confidence(self, ticker: str) -> FundConfidenceResponse:
        payload = await self._client.get(self._confidence_path(ticker))
        return FundConfidenceResponse.model_validate(payload)
