"""Fund trends endpoints under ``/v1/fund-trends/*``."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from .._http import AsyncBaseHTTPClient, BaseHTTPClient
from ..enums import (
    MarketCap,
    NetPositionSortBy,
    NetTradeSortBy,
    SecurityUniverse,
    SortDir,
    StockTrendSortBy,
)
from ..models import StockRef, WallstrankModel

__all__ = [
    "AsyncFundTrendsResource",
    "FundTrendsResource",
    "NetPositionTrend",
    "NetPositionTrendsResponse",
    "NetTradeTrend",
    "NetTradeTrendsResponse",
    "StockTrend",
    "StockTrendsResponse",
]


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class StockTrend(WallstrankModel):
    """A single row in a count/value-based fund-trend response."""

    stock: StockRef
    current: float | None = None
    previous: float | None = None
    change: float | None = None
    change_percent: float | None = None


class StockTrendsResponse(WallstrankModel):
    """Response body for count/value-based fund-trend endpoints."""

    page: int
    page_size: int
    has_more_pages: bool
    reporting_year: int
    reporting_quarter: int
    stocks: list[StockTrend]


class NetPositionTrend(WallstrankModel):
    """A single row in the net position change trend responses."""

    stock: StockRef
    new_positions: int | None = None
    closed_positions: int | None = None
    increased_positions: int | None = None
    reduced_positions: int | None = None
    net_new_positions: int | None = None
    net_closed_positions: int | None = None
    net_increased_positions: int | None = None
    net_reduced_positions: int | None = None


class NetPositionTrendsResponse(WallstrankModel):
    """Response body for the net position change trend endpoints."""

    page: int
    page_size: int
    has_more_pages: bool
    reporting_year: int
    reporting_quarter: int
    stocks: list[NetPositionTrend]


class NetTradeTrend(WallstrankModel):
    """A single row in the net calls/puts trend responses."""

    stock: StockRef
    calls: int | None = None
    puts: int | None = None
    net_calls: int | None = None
    net_puts: int | None = None


class NetTradeTrendsResponse(WallstrankModel):
    """Response body for the net calls/puts trend endpoints."""

    page: int
    page_size: int
    has_more_pages: bool
    reporting_year: int
    reporting_quarter: int
    stocks: list[NetTradeTrend]


# ---------------------------------------------------------------------------
# Request helpers
# ---------------------------------------------------------------------------


def _stock_trend_params(
    *,
    type: SecurityUniverse | str | None,
    market_cap: MarketCap | str | Iterable[MarketCap | str] | None,
    sector: str | None,
    industry: str | None,
    sort_by: StockTrendSortBy | str | None,
    sort_dir: SortDir | str | None,
    page: int | None,
    page_size: int | None,
) -> dict[str, Any]:
    return {
        "type": type,
        "market_cap": market_cap,
        "sector": sector,
        "industry": industry,
        "sort_by": sort_by,
        "sort_dir": sort_dir,
        "page": page,
        "page_size": page_size,
    }


def _net_position_params(
    *,
    type: SecurityUniverse | str | None,
    market_cap: MarketCap | str | Iterable[MarketCap | str] | None,
    sector: str | None,
    industry: str | None,
    sort_by: NetPositionSortBy | str | None,
    sort_dir: SortDir | str | None,
    page: int | None,
    page_size: int | None,
) -> dict[str, Any]:
    return {
        "type": type,
        "market_cap": market_cap,
        "sector": sector,
        "industry": industry,
        "sort_by": sort_by,
        "sort_dir": sort_dir,
        "page": page,
        "page_size": page_size,
    }


def _net_trade_params(
    *,
    type: SecurityUniverse | str | None,
    market_cap: MarketCap | str | Iterable[MarketCap | str] | None,
    sector: str | None,
    industry: str | None,
    sort_by: NetTradeSortBy | str | None,
    sort_dir: SortDir | str | None,
    page: int | None,
    page_size: int | None,
) -> dict[str, Any]:
    return {
        "type": type,
        "market_cap": market_cap,
        "sector": sector,
        "industry": industry,
        "sort_by": sort_by,
        "sort_dir": sort_dir,
        "page": page,
        "page_size": page_size,
    }


_FUND_TREND_ENDPOINTS = {
    "holding": "/v1/fund-trends/holding",
    "holding_in_top_10": "/v1/fund-trends/holding-in-top-10",
    "new_positions": "/v1/fund-trends/new-positions",
    "closed_positions": "/v1/fund-trends/closed-positions",
    "increased_positions": "/v1/fund-trends/increased-positions",
    "reduced_positions": "/v1/fund-trends/reduced-positions",
    "calls": "/v1/fund-trends/calls",
    "puts": "/v1/fund-trends/puts",
    "net_new_positions": "/v1/fund-trends/net-new-positions",
    "net_closed_positions": "/v1/fund-trends/net-closed-positions",
    "net_increased_positions": "/v1/fund-trends/net-increased-positions",
    "net_reduced_positions": "/v1/fund-trends/net-reduced-positions",
    "net_calls": "/v1/fund-trends/net-calls",
    "net_puts": "/v1/fund-trends/net-puts",
}


# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------


class FundTrendsResource:
    """Synchronous fund-trend endpoints."""

    def __init__(self, client: BaseHTTPClient) -> None:
        self._client = client

    # --- count / value based ------------------------------------------------

    def _get_stock_trend(
        self,
        path: str,
        *,
        type: SecurityUniverse | str | None,
        market_cap: MarketCap | str | Iterable[MarketCap | str] | None,
        sector: str | None,
        industry: str | None,
        sort_by: StockTrendSortBy | str | None,
        sort_dir: SortDir | str | None,
        page: int | None,
        page_size: int | None,
    ) -> StockTrendsResponse:
        payload = self._client.get(
            path,
            params=_stock_trend_params(
                type=type,
                market_cap=market_cap,
                sector=sector,
                industry=industry,
                sort_by=sort_by,
                sort_dir=sort_dir,
                page=page,
                page_size=page_size,
            ),
        )
        return StockTrendsResponse.model_validate(payload)

    def holding(
        self,
        *,
        type: SecurityUniverse | str | None = None,
        market_cap: MarketCap | str | Iterable[MarketCap | str] | None = None,
        sector: str | None = None,
        industry: str | None = None,
        sort_by: StockTrendSortBy | str | None = None,
        sort_dir: SortDir | str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> StockTrendsResponse:
        return self._get_stock_trend(
            _FUND_TREND_ENDPOINTS["holding"],
            type=type,
            market_cap=market_cap,
            sector=sector,
            industry=industry,
            sort_by=sort_by,
            sort_dir=sort_dir,
            page=page,
            page_size=page_size,
        )

    def holding_in_top_10(
        self,
        *,
        type: SecurityUniverse | str | None = None,
        market_cap: MarketCap | str | Iterable[MarketCap | str] | None = None,
        sector: str | None = None,
        industry: str | None = None,
        sort_by: StockTrendSortBy | str | None = None,
        sort_dir: SortDir | str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> StockTrendsResponse:
        return self._get_stock_trend(
            _FUND_TREND_ENDPOINTS["holding_in_top_10"],
            type=type,
            market_cap=market_cap,
            sector=sector,
            industry=industry,
            sort_by=sort_by,
            sort_dir=sort_dir,
            page=page,
            page_size=page_size,
        )

    def new_positions(
        self,
        *,
        type: SecurityUniverse | str | None = None,
        market_cap: MarketCap | str | Iterable[MarketCap | str] | None = None,
        sector: str | None = None,
        industry: str | None = None,
        sort_by: StockTrendSortBy | str | None = None,
        sort_dir: SortDir | str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> StockTrendsResponse:
        return self._get_stock_trend(
            _FUND_TREND_ENDPOINTS["new_positions"],
            type=type,
            market_cap=market_cap,
            sector=sector,
            industry=industry,
            sort_by=sort_by,
            sort_dir=sort_dir,
            page=page,
            page_size=page_size,
        )

    def closed_positions(
        self,
        *,
        type: SecurityUniverse | str | None = None,
        market_cap: MarketCap | str | Iterable[MarketCap | str] | None = None,
        sector: str | None = None,
        industry: str | None = None,
        sort_by: StockTrendSortBy | str | None = None,
        sort_dir: SortDir | str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> StockTrendsResponse:
        return self._get_stock_trend(
            _FUND_TREND_ENDPOINTS["closed_positions"],
            type=type,
            market_cap=market_cap,
            sector=sector,
            industry=industry,
            sort_by=sort_by,
            sort_dir=sort_dir,
            page=page,
            page_size=page_size,
        )

    def increased_positions(
        self,
        *,
        type: SecurityUniverse | str | None = None,
        market_cap: MarketCap | str | Iterable[MarketCap | str] | None = None,
        sector: str | None = None,
        industry: str | None = None,
        sort_by: StockTrendSortBy | str | None = None,
        sort_dir: SortDir | str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> StockTrendsResponse:
        return self._get_stock_trend(
            _FUND_TREND_ENDPOINTS["increased_positions"],
            type=type,
            market_cap=market_cap,
            sector=sector,
            industry=industry,
            sort_by=sort_by,
            sort_dir=sort_dir,
            page=page,
            page_size=page_size,
        )

    def reduced_positions(
        self,
        *,
        type: SecurityUniverse | str | None = None,
        market_cap: MarketCap | str | Iterable[MarketCap | str] | None = None,
        sector: str | None = None,
        industry: str | None = None,
        sort_by: StockTrendSortBy | str | None = None,
        sort_dir: SortDir | str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> StockTrendsResponse:
        return self._get_stock_trend(
            _FUND_TREND_ENDPOINTS["reduced_positions"],
            type=type,
            market_cap=market_cap,
            sector=sector,
            industry=industry,
            sort_by=sort_by,
            sort_dir=sort_dir,
            page=page,
            page_size=page_size,
        )

    def calls(
        self,
        *,
        type: SecurityUniverse | str | None = None,
        market_cap: MarketCap | str | Iterable[MarketCap | str] | None = None,
        sector: str | None = None,
        industry: str | None = None,
        sort_by: StockTrendSortBy | str | None = None,
        sort_dir: SortDir | str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> StockTrendsResponse:
        return self._get_stock_trend(
            _FUND_TREND_ENDPOINTS["calls"],
            type=type,
            market_cap=market_cap,
            sector=sector,
            industry=industry,
            sort_by=sort_by,
            sort_dir=sort_dir,
            page=page,
            page_size=page_size,
        )

    def puts(
        self,
        *,
        type: SecurityUniverse | str | None = None,
        market_cap: MarketCap | str | Iterable[MarketCap | str] | None = None,
        sector: str | None = None,
        industry: str | None = None,
        sort_by: StockTrendSortBy | str | None = None,
        sort_dir: SortDir | str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> StockTrendsResponse:
        return self._get_stock_trend(
            _FUND_TREND_ENDPOINTS["puts"],
            type=type,
            market_cap=market_cap,
            sector=sector,
            industry=industry,
            sort_by=sort_by,
            sort_dir=sort_dir,
            page=page,
            page_size=page_size,
        )

    # --- net position ------------------------------------------------------

    def _get_net_position(
        self,
        path: str,
        *,
        type: SecurityUniverse | str | None,
        market_cap: MarketCap | str | Iterable[MarketCap | str] | None,
        sector: str | None,
        industry: str | None,
        sort_by: NetPositionSortBy | str | None,
        sort_dir: SortDir | str | None,
        page: int | None,
        page_size: int | None,
    ) -> NetPositionTrendsResponse:
        payload = self._client.get(
            path,
            params=_net_position_params(
                type=type,
                market_cap=market_cap,
                sector=sector,
                industry=industry,
                sort_by=sort_by,
                sort_dir=sort_dir,
                page=page,
                page_size=page_size,
            ),
        )
        return NetPositionTrendsResponse.model_validate(payload)

    def net_new_positions(
        self,
        *,
        type: SecurityUniverse | str | None = None,
        market_cap: MarketCap | str | Iterable[MarketCap | str] | None = None,
        sector: str | None = None,
        industry: str | None = None,
        sort_by: NetPositionSortBy | str | None = None,
        sort_dir: SortDir | str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> NetPositionTrendsResponse:
        return self._get_net_position(
            _FUND_TREND_ENDPOINTS["net_new_positions"],
            type=type,
            market_cap=market_cap,
            sector=sector,
            industry=industry,
            sort_by=sort_by,
            sort_dir=sort_dir,
            page=page,
            page_size=page_size,
        )

    def net_closed_positions(
        self,
        *,
        type: SecurityUniverse | str | None = None,
        market_cap: MarketCap | str | Iterable[MarketCap | str] | None = None,
        sector: str | None = None,
        industry: str | None = None,
        sort_by: NetPositionSortBy | str | None = None,
        sort_dir: SortDir | str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> NetPositionTrendsResponse:
        return self._get_net_position(
            _FUND_TREND_ENDPOINTS["net_closed_positions"],
            type=type,
            market_cap=market_cap,
            sector=sector,
            industry=industry,
            sort_by=sort_by,
            sort_dir=sort_dir,
            page=page,
            page_size=page_size,
        )

    def net_increased_positions(
        self,
        *,
        type: SecurityUniverse | str | None = None,
        market_cap: MarketCap | str | Iterable[MarketCap | str] | None = None,
        sector: str | None = None,
        industry: str | None = None,
        sort_by: NetPositionSortBy | str | None = None,
        sort_dir: SortDir | str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> NetPositionTrendsResponse:
        return self._get_net_position(
            _FUND_TREND_ENDPOINTS["net_increased_positions"],
            type=type,
            market_cap=market_cap,
            sector=sector,
            industry=industry,
            sort_by=sort_by,
            sort_dir=sort_dir,
            page=page,
            page_size=page_size,
        )

    def net_reduced_positions(
        self,
        *,
        type: SecurityUniverse | str | None = None,
        market_cap: MarketCap | str | Iterable[MarketCap | str] | None = None,
        sector: str | None = None,
        industry: str | None = None,
        sort_by: NetPositionSortBy | str | None = None,
        sort_dir: SortDir | str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> NetPositionTrendsResponse:
        return self._get_net_position(
            _FUND_TREND_ENDPOINTS["net_reduced_positions"],
            type=type,
            market_cap=market_cap,
            sector=sector,
            industry=industry,
            sort_by=sort_by,
            sort_dir=sort_dir,
            page=page,
            page_size=page_size,
        )

    # --- net trade ---------------------------------------------------------

    def _get_net_trade(
        self,
        path: str,
        *,
        type: SecurityUniverse | str | None,
        market_cap: MarketCap | str | Iterable[MarketCap | str] | None,
        sector: str | None,
        industry: str | None,
        sort_by: NetTradeSortBy | str | None,
        sort_dir: SortDir | str | None,
        page: int | None,
        page_size: int | None,
    ) -> NetTradeTrendsResponse:
        payload = self._client.get(
            path,
            params=_net_trade_params(
                type=type,
                market_cap=market_cap,
                sector=sector,
                industry=industry,
                sort_by=sort_by,
                sort_dir=sort_dir,
                page=page,
                page_size=page_size,
            ),
        )
        return NetTradeTrendsResponse.model_validate(payload)

    def net_calls(
        self,
        *,
        type: SecurityUniverse | str | None = None,
        market_cap: MarketCap | str | Iterable[MarketCap | str] | None = None,
        sector: str | None = None,
        industry: str | None = None,
        sort_by: NetTradeSortBy | str | None = None,
        sort_dir: SortDir | str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> NetTradeTrendsResponse:
        return self._get_net_trade(
            _FUND_TREND_ENDPOINTS["net_calls"],
            type=type,
            market_cap=market_cap,
            sector=sector,
            industry=industry,
            sort_by=sort_by,
            sort_dir=sort_dir,
            page=page,
            page_size=page_size,
        )

    def net_puts(
        self,
        *,
        type: SecurityUniverse | str | None = None,
        market_cap: MarketCap | str | Iterable[MarketCap | str] | None = None,
        sector: str | None = None,
        industry: str | None = None,
        sort_by: NetTradeSortBy | str | None = None,
        sort_dir: SortDir | str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> NetTradeTrendsResponse:
        return self._get_net_trade(
            _FUND_TREND_ENDPOINTS["net_puts"],
            type=type,
            market_cap=market_cap,
            sector=sector,
            industry=industry,
            sort_by=sort_by,
            sort_dir=sort_dir,
            page=page,
            page_size=page_size,
        )


class AsyncFundTrendsResource:
    """Asynchronous fund-trend endpoints."""

    def __init__(self, client: AsyncBaseHTTPClient) -> None:
        self._client = client

    async def _get_stock_trend(
        self,
        path: str,
        *,
        type: SecurityUniverse | str | None,
        market_cap: MarketCap | str | Iterable[MarketCap | str] | None,
        sector: str | None,
        industry: str | None,
        sort_by: StockTrendSortBy | str | None,
        sort_dir: SortDir | str | None,
        page: int | None,
        page_size: int | None,
    ) -> StockTrendsResponse:
        payload = await self._client.get(
            path,
            params=_stock_trend_params(
                type=type,
                market_cap=market_cap,
                sector=sector,
                industry=industry,
                sort_by=sort_by,
                sort_dir=sort_dir,
                page=page,
                page_size=page_size,
            ),
        )
        return StockTrendsResponse.model_validate(payload)

    async def holding(
        self,
        *,
        type: SecurityUniverse | str | None = None,
        market_cap: MarketCap | str | Iterable[MarketCap | str] | None = None,
        sector: str | None = None,
        industry: str | None = None,
        sort_by: StockTrendSortBy | str | None = None,
        sort_dir: SortDir | str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> StockTrendsResponse:
        return await self._get_stock_trend(
            _FUND_TREND_ENDPOINTS["holding"],
            type=type,
            market_cap=market_cap,
            sector=sector,
            industry=industry,
            sort_by=sort_by,
            sort_dir=sort_dir,
            page=page,
            page_size=page_size,
        )

    async def holding_in_top_10(
        self,
        *,
        type: SecurityUniverse | str | None = None,
        market_cap: MarketCap | str | Iterable[MarketCap | str] | None = None,
        sector: str | None = None,
        industry: str | None = None,
        sort_by: StockTrendSortBy | str | None = None,
        sort_dir: SortDir | str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> StockTrendsResponse:
        return await self._get_stock_trend(
            _FUND_TREND_ENDPOINTS["holding_in_top_10"],
            type=type,
            market_cap=market_cap,
            sector=sector,
            industry=industry,
            sort_by=sort_by,
            sort_dir=sort_dir,
            page=page,
            page_size=page_size,
        )

    async def new_positions(
        self,
        *,
        type: SecurityUniverse | str | None = None,
        market_cap: MarketCap | str | Iterable[MarketCap | str] | None = None,
        sector: str | None = None,
        industry: str | None = None,
        sort_by: StockTrendSortBy | str | None = None,
        sort_dir: SortDir | str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> StockTrendsResponse:
        return await self._get_stock_trend(
            _FUND_TREND_ENDPOINTS["new_positions"],
            type=type,
            market_cap=market_cap,
            sector=sector,
            industry=industry,
            sort_by=sort_by,
            sort_dir=sort_dir,
            page=page,
            page_size=page_size,
        )

    async def closed_positions(
        self,
        *,
        type: SecurityUniverse | str | None = None,
        market_cap: MarketCap | str | Iterable[MarketCap | str] | None = None,
        sector: str | None = None,
        industry: str | None = None,
        sort_by: StockTrendSortBy | str | None = None,
        sort_dir: SortDir | str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> StockTrendsResponse:
        return await self._get_stock_trend(
            _FUND_TREND_ENDPOINTS["closed_positions"],
            type=type,
            market_cap=market_cap,
            sector=sector,
            industry=industry,
            sort_by=sort_by,
            sort_dir=sort_dir,
            page=page,
            page_size=page_size,
        )

    async def increased_positions(
        self,
        *,
        type: SecurityUniverse | str | None = None,
        market_cap: MarketCap | str | Iterable[MarketCap | str] | None = None,
        sector: str | None = None,
        industry: str | None = None,
        sort_by: StockTrendSortBy | str | None = None,
        sort_dir: SortDir | str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> StockTrendsResponse:
        return await self._get_stock_trend(
            _FUND_TREND_ENDPOINTS["increased_positions"],
            type=type,
            market_cap=market_cap,
            sector=sector,
            industry=industry,
            sort_by=sort_by,
            sort_dir=sort_dir,
            page=page,
            page_size=page_size,
        )

    async def reduced_positions(
        self,
        *,
        type: SecurityUniverse | str | None = None,
        market_cap: MarketCap | str | Iterable[MarketCap | str] | None = None,
        sector: str | None = None,
        industry: str | None = None,
        sort_by: StockTrendSortBy | str | None = None,
        sort_dir: SortDir | str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> StockTrendsResponse:
        return await self._get_stock_trend(
            _FUND_TREND_ENDPOINTS["reduced_positions"],
            type=type,
            market_cap=market_cap,
            sector=sector,
            industry=industry,
            sort_by=sort_by,
            sort_dir=sort_dir,
            page=page,
            page_size=page_size,
        )

    async def calls(
        self,
        *,
        type: SecurityUniverse | str | None = None,
        market_cap: MarketCap | str | Iterable[MarketCap | str] | None = None,
        sector: str | None = None,
        industry: str | None = None,
        sort_by: StockTrendSortBy | str | None = None,
        sort_dir: SortDir | str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> StockTrendsResponse:
        return await self._get_stock_trend(
            _FUND_TREND_ENDPOINTS["calls"],
            type=type,
            market_cap=market_cap,
            sector=sector,
            industry=industry,
            sort_by=sort_by,
            sort_dir=sort_dir,
            page=page,
            page_size=page_size,
        )

    async def puts(
        self,
        *,
        type: SecurityUniverse | str | None = None,
        market_cap: MarketCap | str | Iterable[MarketCap | str] | None = None,
        sector: str | None = None,
        industry: str | None = None,
        sort_by: StockTrendSortBy | str | None = None,
        sort_dir: SortDir | str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> StockTrendsResponse:
        return await self._get_stock_trend(
            _FUND_TREND_ENDPOINTS["puts"],
            type=type,
            market_cap=market_cap,
            sector=sector,
            industry=industry,
            sort_by=sort_by,
            sort_dir=sort_dir,
            page=page,
            page_size=page_size,
        )

    async def _get_net_position(
        self,
        path: str,
        *,
        type: SecurityUniverse | str | None,
        market_cap: MarketCap | str | Iterable[MarketCap | str] | None,
        sector: str | None,
        industry: str | None,
        sort_by: NetPositionSortBy | str | None,
        sort_dir: SortDir | str | None,
        page: int | None,
        page_size: int | None,
    ) -> NetPositionTrendsResponse:
        payload = await self._client.get(
            path,
            params=_net_position_params(
                type=type,
                market_cap=market_cap,
                sector=sector,
                industry=industry,
                sort_by=sort_by,
                sort_dir=sort_dir,
                page=page,
                page_size=page_size,
            ),
        )
        return NetPositionTrendsResponse.model_validate(payload)

    async def net_new_positions(
        self,
        *,
        type: SecurityUniverse | str | None = None,
        market_cap: MarketCap | str | Iterable[MarketCap | str] | None = None,
        sector: str | None = None,
        industry: str | None = None,
        sort_by: NetPositionSortBy | str | None = None,
        sort_dir: SortDir | str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> NetPositionTrendsResponse:
        return await self._get_net_position(
            _FUND_TREND_ENDPOINTS["net_new_positions"],
            type=type,
            market_cap=market_cap,
            sector=sector,
            industry=industry,
            sort_by=sort_by,
            sort_dir=sort_dir,
            page=page,
            page_size=page_size,
        )

    async def net_closed_positions(
        self,
        *,
        type: SecurityUniverse | str | None = None,
        market_cap: MarketCap | str | Iterable[MarketCap | str] | None = None,
        sector: str | None = None,
        industry: str | None = None,
        sort_by: NetPositionSortBy | str | None = None,
        sort_dir: SortDir | str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> NetPositionTrendsResponse:
        return await self._get_net_position(
            _FUND_TREND_ENDPOINTS["net_closed_positions"],
            type=type,
            market_cap=market_cap,
            sector=sector,
            industry=industry,
            sort_by=sort_by,
            sort_dir=sort_dir,
            page=page,
            page_size=page_size,
        )

    async def net_increased_positions(
        self,
        *,
        type: SecurityUniverse | str | None = None,
        market_cap: MarketCap | str | Iterable[MarketCap | str] | None = None,
        sector: str | None = None,
        industry: str | None = None,
        sort_by: NetPositionSortBy | str | None = None,
        sort_dir: SortDir | str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> NetPositionTrendsResponse:
        return await self._get_net_position(
            _FUND_TREND_ENDPOINTS["net_increased_positions"],
            type=type,
            market_cap=market_cap,
            sector=sector,
            industry=industry,
            sort_by=sort_by,
            sort_dir=sort_dir,
            page=page,
            page_size=page_size,
        )

    async def net_reduced_positions(
        self,
        *,
        type: SecurityUniverse | str | None = None,
        market_cap: MarketCap | str | Iterable[MarketCap | str] | None = None,
        sector: str | None = None,
        industry: str | None = None,
        sort_by: NetPositionSortBy | str | None = None,
        sort_dir: SortDir | str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> NetPositionTrendsResponse:
        return await self._get_net_position(
            _FUND_TREND_ENDPOINTS["net_reduced_positions"],
            type=type,
            market_cap=market_cap,
            sector=sector,
            industry=industry,
            sort_by=sort_by,
            sort_dir=sort_dir,
            page=page,
            page_size=page_size,
        )

    async def _get_net_trade(
        self,
        path: str,
        *,
        type: SecurityUniverse | str | None,
        market_cap: MarketCap | str | Iterable[MarketCap | str] | None,
        sector: str | None,
        industry: str | None,
        sort_by: NetTradeSortBy | str | None,
        sort_dir: SortDir | str | None,
        page: int | None,
        page_size: int | None,
    ) -> NetTradeTrendsResponse:
        payload = await self._client.get(
            path,
            params=_net_trade_params(
                type=type,
                market_cap=market_cap,
                sector=sector,
                industry=industry,
                sort_by=sort_by,
                sort_dir=sort_dir,
                page=page,
                page_size=page_size,
            ),
        )
        return NetTradeTrendsResponse.model_validate(payload)

    async def net_calls(
        self,
        *,
        type: SecurityUniverse | str | None = None,
        market_cap: MarketCap | str | Iterable[MarketCap | str] | None = None,
        sector: str | None = None,
        industry: str | None = None,
        sort_by: NetTradeSortBy | str | None = None,
        sort_dir: SortDir | str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> NetTradeTrendsResponse:
        return await self._get_net_trade(
            _FUND_TREND_ENDPOINTS["net_calls"],
            type=type,
            market_cap=market_cap,
            sector=sector,
            industry=industry,
            sort_by=sort_by,
            sort_dir=sort_dir,
            page=page,
            page_size=page_size,
        )

    async def net_puts(
        self,
        *,
        type: SecurityUniverse | str | None = None,
        market_cap: MarketCap | str | Iterable[MarketCap | str] | None = None,
        sector: str | None = None,
        industry: str | None = None,
        sort_by: NetTradeSortBy | str | None = None,
        sort_dir: SortDir | str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> NetTradeTrendsResponse:
        return await self._get_net_trade(
            _FUND_TREND_ENDPOINTS["net_puts"],
            type=type,
            market_cap=market_cap,
            sector=sector,
            industry=industry,
            sort_by=sort_by,
            sort_dir=sort_dir,
            page=page,
            page_size=page_size,
        )
