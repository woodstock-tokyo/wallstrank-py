"""Fund endpoints: /v1/funds, /v1/fund-managers, /v1/funds-portfolios, portfolio detail, holdings,
top buys & sells, sector composition."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from .._http import AsyncBaseHTTPClient, BaseHTTPClient, encode_path_segment
from ..enums import (
    FundHolderSortBy,
    FundSortBy,
    PortfolioSortBy,
    SecurityType,
    SortDir,
)
from ..models import (
    Fund,
    FundManagerRef,
    FundManagerWithFund,
    Holding,
    PortfolioMetrics,
    PortfolioSectorAllocation,
    PositionRef,
    StockRef,
    WallstrankModel,
)

__all__ = [
    "AsyncFundsResource",
    "FundHolding",
    "FundManagerListResponse",
    "FundPortfolio",
    "FundsListResponse",
    "FundsResource",
    "HoldingsResponse",
    "PortfolioResponse",
    "PortfoliosResponse",
    "SectorCompositionResponse",
    "TopBuysSellsResponse",
    "TopTrade",
]


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class FundsListResponse(WallstrankModel):
    """Response body for ``/v1/funds``."""

    page: int
    page_size: int
    has_more_pages: bool
    funds: list[Fund]


class FundManagerListResponse(WallstrankModel):
    """Response body for ``/v1/fund-managers``."""

    page: int
    page_size: int
    has_more_pages: bool
    managers: list[FundManagerWithFund]


class FundPortfolio(PortfolioMetrics):
    """A single entry in the fund-portfolios list."""

    fund: Fund
    fund_managers: list[FundManagerRef] = Field(default_factory=list)


class PortfoliosResponse(WallstrankModel):
    """Response body for ``/v1/funds-portfolios``."""

    page: int
    page_size: int
    has_more_pages: bool
    reporting_year: int
    reporting_quarter: int
    portfolios: list[FundPortfolio]


class PortfolioResponse(PortfolioMetrics):
    """Response body for ``/v1/funds/:fund_or_mgr_id/portfolio``."""

    fund: Fund
    fund_managers: list[FundManagerRef] = Field(default_factory=list)


class FundHolding(Holding):
    """A holding entry within a fund portfolio."""


class HoldingsResponse(WallstrankModel):
    """Response body for ``/v1/funds-portfolios/:fund_or_mgr_id/holdings``."""

    page: int
    page_size: int
    has_more_pages: bool
    reporting_year: int
    reporting_quarter: int
    holdings: list[FundHolding]


class TopTrade(PositionRef):
    """A single top buy or sell."""

    stock: StockRef


class TopBuysSellsResponse(WallstrankModel):
    """Response body for ``/v1/funds/:fund_or_mgr_id/top-buys-sells``."""

    reporting_year: int
    reporting_quarter: int
    buys: list[TopTrade]
    sells: list[TopTrade]


class SectorCompositionResponse(WallstrankModel):
    """Response body for ``/v1/funds/:fund_or_mgr_id/sector-composition``."""

    reporting_year: int
    reporting_quarter: int
    composition: list[PortfolioSectorAllocation]


# ---------------------------------------------------------------------------
# Request helpers
# ---------------------------------------------------------------------------


def _funds_params(
    *,
    year: int | None,
    quarter: int | None,
    sort_by: FundSortBy | str | None,
    sort_dir: SortDir | str | None,
    page: int | None,
    page_size: int | None,
) -> dict[str, Any]:
    return {
        "year": year,
        "quarter": quarter,
        "sort_by": sort_by,
        "sort_dir": sort_dir,
        "page": page,
        "page_size": page_size,
    }


def _fund_managers_params(
    *,
    page: int | None,
    page_size: int | None,
) -> dict[str, Any]:
    return {"page": page, "page_size": page_size}


def _portfolios_params(
    *,
    year: int | None,
    quarter: int | None,
    include_ongoing: bool | None,
    sort_by: PortfolioSortBy | str | None,
    sort_dir: SortDir | str | None,
    page: int | None,
    page_size: int | None,
) -> dict[str, Any]:
    return {
        "year": year,
        "quarter": quarter,
        "include_ongoing": include_ongoing,
        "sort_by": sort_by,
        "sort_dir": sort_dir,
        "page": page,
        "page_size": page_size,
    }


def _period_params(
    *,
    year: int | None,
    quarter: int | None,
) -> dict[str, Any]:
    return {"year": year, "quarter": quarter}


def _holdings_params(
    *,
    year: int | None,
    quarter: int | None,
    security_type: SecurityType | str | None,
    sort_by: FundHolderSortBy | str | None,
    sort_dir: SortDir | str | None,
    page: int | None,
    page_size: int | None,
) -> dict[str, Any]:
    return {
        "year": year,
        "quarter": quarter,
        "security_type": security_type,
        "sort_by": sort_by,
        "sort_dir": sort_dir,
        "page": page,
        "page_size": page_size,
    }


# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------


class _FundsBase:
    _FUNDS = "/v1/funds"
    _FUND_MANAGERS = "/v1/fund-managers"
    _PORTFOLIOS = "/v1/funds-portfolios"

    @staticmethod
    def _portfolio_path(fund_or_mgr_id: str) -> str:
        return f"/v1/funds/{encode_path_segment(fund_or_mgr_id)}/portfolio"

    @staticmethod
    def _holdings_path(fund_or_mgr_id: str) -> str:
        return f"/v1/funds-portfolios/{encode_path_segment(fund_or_mgr_id)}/holdings"

    @staticmethod
    def _top_buys_sells_path(fund_or_mgr_id: str) -> str:
        return f"/v1/funds/{encode_path_segment(fund_or_mgr_id)}/top-buys-sells"

    @staticmethod
    def _sector_composition_path(fund_or_mgr_id: str) -> str:
        return f"/v1/funds/{encode_path_segment(fund_or_mgr_id)}/sector-composition"


class FundsResource(_FundsBase):
    """Synchronous funds endpoints."""

    def __init__(self, client: BaseHTTPClient) -> None:
        self._client = client

    def list(
        self,
        *,
        year: int | None = None,
        quarter: int | None = None,
        sort_by: FundSortBy | str | None = None,
        sort_dir: SortDir | str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> FundsListResponse:
        """Paginated list of funds."""

        payload = self._client.get(
            self._FUNDS,
            params=_funds_params(
                year=year,
                quarter=quarter,
                sort_by=sort_by,
                sort_dir=sort_dir,
                page=page,
                page_size=page_size,
            ),
        )
        return FundsListResponse.model_validate(payload)

    def list_managers(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
    ) -> FundManagerListResponse:
        """Paginated list of fund managers."""

        payload = self._client.get(
            self._FUND_MANAGERS,
            params=_fund_managers_params(page=page, page_size=page_size),
        )
        return FundManagerListResponse.model_validate(payload)

    def list_portfolios(
        self,
        *,
        year: int | None = None,
        quarter: int | None = None,
        include_ongoing: bool | None = None,
        sort_by: PortfolioSortBy | str | None = None,
        sort_dir: SortDir | str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> PortfoliosResponse:
        """Paginated list of fund portfolios for a reporting period."""

        payload = self._client.get(
            self._PORTFOLIOS,
            params=_portfolios_params(
                year=year,
                quarter=quarter,
                include_ongoing=include_ongoing,
                sort_by=sort_by,
                sort_dir=sort_dir,
                page=page,
                page_size=page_size,
            ),
        )
        return PortfoliosResponse.model_validate(payload)

    def portfolio(
        self,
        fund_or_mgr_id: str,
        *,
        year: int | None = None,
        quarter: int | None = None,
    ) -> PortfolioResponse:
        """Fetch the latest or a specific historical portfolio for a fund/manager."""

        payload = self._client.get(
            self._portfolio_path(fund_or_mgr_id),
            params=_period_params(year=year, quarter=quarter),
        )
        return PortfolioResponse.model_validate(payload)

    def holdings(
        self,
        fund_or_mgr_id: str,
        *,
        year: int | None = None,
        quarter: int | None = None,
        security_type: SecurityType | str | None = None,
        sort_by: FundHolderSortBy | str | None = None,
        sort_dir: SortDir | str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> HoldingsResponse:
        """Fetch holdings for a given fund/manager portfolio."""

        payload = self._client.get(
            self._holdings_path(fund_or_mgr_id),
            params=_holdings_params(
                year=year,
                quarter=quarter,
                security_type=security_type,
                sort_by=sort_by,
                sort_dir=sort_dir,
                page=page,
                page_size=page_size,
            ),
        )
        return HoldingsResponse.model_validate(payload)

    def top_buys_sells(
        self,
        fund_or_mgr_id: str,
        *,
        year: int | None = None,
        quarter: int | None = None,
    ) -> TopBuysSellsResponse:
        payload = self._client.get(
            self._top_buys_sells_path(fund_or_mgr_id),
            params=_period_params(year=year, quarter=quarter),
        )
        return TopBuysSellsResponse.model_validate(payload)

    def sector_composition(
        self,
        fund_or_mgr_id: str,
        *,
        year: int | None = None,
        quarter: int | None = None,
    ) -> SectorCompositionResponse:
        payload = self._client.get(
            self._sector_composition_path(fund_or_mgr_id),
            params=_period_params(year=year, quarter=quarter),
        )
        return SectorCompositionResponse.model_validate(payload)


class AsyncFundsResource(_FundsBase):
    """Asynchronous funds endpoints."""

    def __init__(self, client: AsyncBaseHTTPClient) -> None:
        self._client = client

    async def list(
        self,
        *,
        year: int | None = None,
        quarter: int | None = None,
        sort_by: FundSortBy | str | None = None,
        sort_dir: SortDir | str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> FundsListResponse:
        payload = await self._client.get(
            self._FUNDS,
            params=_funds_params(
                year=year,
                quarter=quarter,
                sort_by=sort_by,
                sort_dir=sort_dir,
                page=page,
                page_size=page_size,
            ),
        )
        return FundsListResponse.model_validate(payload)

    async def list_managers(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
    ) -> FundManagerListResponse:
        payload = await self._client.get(
            self._FUND_MANAGERS,
            params=_fund_managers_params(page=page, page_size=page_size),
        )
        return FundManagerListResponse.model_validate(payload)

    async def list_portfolios(
        self,
        *,
        year: int | None = None,
        quarter: int | None = None,
        include_ongoing: bool | None = None,
        sort_by: PortfolioSortBy | str | None = None,
        sort_dir: SortDir | str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> PortfoliosResponse:
        payload = await self._client.get(
            self._PORTFOLIOS,
            params=_portfolios_params(
                year=year,
                quarter=quarter,
                include_ongoing=include_ongoing,
                sort_by=sort_by,
                sort_dir=sort_dir,
                page=page,
                page_size=page_size,
            ),
        )
        return PortfoliosResponse.model_validate(payload)

    async def portfolio(
        self,
        fund_or_mgr_id: str,
        *,
        year: int | None = None,
        quarter: int | None = None,
    ) -> PortfolioResponse:
        payload = await self._client.get(
            self._portfolio_path(fund_or_mgr_id),
            params=_period_params(year=year, quarter=quarter),
        )
        return PortfolioResponse.model_validate(payload)

    async def holdings(
        self,
        fund_or_mgr_id: str,
        *,
        year: int | None = None,
        quarter: int | None = None,
        security_type: SecurityType | str | None = None,
        sort_by: FundHolderSortBy | str | None = None,
        sort_dir: SortDir | str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> HoldingsResponse:
        payload = await self._client.get(
            self._holdings_path(fund_or_mgr_id),
            params=_holdings_params(
                year=year,
                quarter=quarter,
                security_type=security_type,
                sort_by=sort_by,
                sort_dir=sort_dir,
                page=page,
                page_size=page_size,
            ),
        )
        return HoldingsResponse.model_validate(payload)

    async def top_buys_sells(
        self,
        fund_or_mgr_id: str,
        *,
        year: int | None = None,
        quarter: int | None = None,
    ) -> TopBuysSellsResponse:
        payload = await self._client.get(
            self._top_buys_sells_path(fund_or_mgr_id),
            params=_period_params(year=year, quarter=quarter),
        )
        return TopBuysSellsResponse.model_validate(payload)

    async def sector_composition(
        self,
        fund_or_mgr_id: str,
        *,
        year: int | None = None,
        quarter: int | None = None,
    ) -> SectorCompositionResponse:
        payload = await self._client.get(
            self._sector_composition_path(fund_or_mgr_id),
            params=_period_params(year=year, quarter=quarter),
        )
        return SectorCompositionResponse.model_validate(payload)
