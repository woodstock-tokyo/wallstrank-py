"""Shared response models used across multiple Wall St. Rank endpoints."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from .enums import InsightSentiment, InsightType, SecurityType

__all__ = [
    "ChartBar",
    "Fund",
    "FundManager",
    "FundManagerRef",
    "FundManagerWithFund",
    "FundReturnBar",
    "FundSummary",
    "Holding",
    "Industry",
    "Insight",
    "Page",
    "PortfolioMetrics",
    "PortfolioSectorAllocation",
    "PositionInsight",
    "PositionRef",
    "Sector",
    "SectorRef",
    "Stock",
    "StockRef",
    "TradeInsight",
    "WallstrankModel",
]


class WallstrankModel(BaseModel):
    """Base model for all Wall St. Rank response objects.

    - ``extra="allow"`` keeps forward-compatibility: newly added fields on the
      server side won't break existing clients.
    - ``populate_by_name=True`` allows constructing models by either alias or
      field name.
    """

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
        str_strip_whitespace=True,
    )


class Page[ItemT](WallstrankModel):
    """Standard pagination envelope."""

    page: int
    page_size: int
    has_more_pages: bool
    items: list[ItemT]


# ---------------------------------------------------------------------------
# Reference / lookup objects
# ---------------------------------------------------------------------------


class Sector(WallstrankModel):
    """A sector entity returned by ``/v1/sectors``."""

    id: str
    name: str


class Industry(WallstrankModel):
    """An industry entity returned by ``/v1/industries``."""

    id: str
    name: str
    sector_id: str


class SectorRef(WallstrankModel):
    """Reference to a sector embedded in another response."""

    id: str
    name: str


# ---------------------------------------------------------------------------
# Stocks
# ---------------------------------------------------------------------------


class StockRef(WallstrankModel):
    """Reference to a stock (as returned in nested payloads)."""

    id: str
    ticker: str
    name: str
    active: bool | None = None


class Stock(StockRef):
    """A fully materialised stock. Currently identical to :class:`StockRef`."""


# ---------------------------------------------------------------------------
# Funds and fund managers
# ---------------------------------------------------------------------------


class FundSummary(WallstrankModel):
    """A compact fund reference embedded in nested responses."""

    id: str
    name: str
    icon_url: str | None = None


class Fund(WallstrankModel):
    """Full fund object returned by ``/v1/funds``."""

    id: str
    name: str
    profile: str | None = None
    icon_url: str | None = None
    city: str | None = None
    state_or_country: str | None = None
    latest_reporting_year: int | None = None
    latest_reporting_quarter: int | None = None
    latest_aum: int | None = None
    return_latest_quarter: float | None = None
    return_years_1: float | None = None
    return_years_3: float | None = None
    return_years_5: float | None = None
    return_years_10: float | None = None


class FundManagerRef(WallstrankModel):
    """Fund manager reference embedded in nested responses."""

    id: str
    name: str
    profile: str | None = None
    icon_url: str | None = None
    popularity_rank: int | None = None


class FundManagerWithFund(FundManagerRef):
    """Fund manager returned by ``/v1/fund-managers``, includes fund info."""

    fund: FundSummary | None = None


class FundManager(FundManagerRef):
    """Alias exposed for consistency with public naming."""


# ---------------------------------------------------------------------------
# Portfolios & positions
# ---------------------------------------------------------------------------


class PortfolioMetrics(WallstrankModel):
    """Portfolio-level metrics returned by portfolio endpoints."""

    reporting_year: int
    reporting_quarter: int
    quarter_return: float | None = None
    aum: int | None = None
    aum_last: int | None = None
    aum_change: int | None = None
    aum_change_percent: float | None = None
    aum_top_10: int | None = None
    aum_top_10_as_percent_of_aum: float | None = None
    capital_flow: int | None = None
    capital_flow_as_percent_of_aum: float | None = None
    etfs_percent: float | None = None
    turnover_percent: float | None = None
    holdings: int | None = None
    holdings_last: int | None = None
    holdings_change: int | None = None
    new_positions: int | None = None
    new_positions_last: int | None = None
    new_positions_change: int | None = None
    closed_positions: int | None = None
    closed_positions_last: int | None = None
    closed_positions_change: int | None = None
    increased_positions: int | None = None
    increased_positions_last: int | None = None
    increased_positions_change: int | None = None
    reduced_positions: int | None = None
    reduced_positions_last: int | None = None
    reduced_positions_change: int | None = None


class PositionRef(WallstrankModel):
    """A base position payload used across multiple endpoints."""

    security_type: SecurityType
    market_value: int | None = None
    status: str | None = None
    portfolio_weight: float | None = None
    shares: int | None = None
    shares_last: int | None = None
    shares_change: int | None = None
    shares_change_percent: float | None = None
    capital_flow: int | None = None


class Holding(PositionRef):
    """A single portfolio holding."""

    stock: StockRef


class PortfolioSectorAllocation(WallstrankModel):
    """Allocation of a portfolio to a sector."""

    sector: SectorRef
    percent: float


# ---------------------------------------------------------------------------
# Insights (fund confidence)
# ---------------------------------------------------------------------------


class Insight(WallstrankModel):
    """Base fund confidence insight."""

    id: str
    type: InsightType
    title: str
    year: int
    quarter: int
    sentiment: InsightSentiment | None = None


class PositionInsight(Insight):
    """A ``change`` or ``net`` insight expressed as counts / percentages."""

    current_value: float | None = None
    previous_value: float | None = None
    change_percent: float | None = None
    new_positions: int | None = None
    closed_positions: int | None = None
    increased_positions: int | None = None
    reduced_positions: int | None = None
    net_percent: float | None = None


class TradeInsight(Insight):
    """An insight on option flow."""

    calls_value: int | None = None
    puts_value: int | None = None
    net_percent: float | None = None


# ---------------------------------------------------------------------------
# Chart bars
# ---------------------------------------------------------------------------


class ChartBar(WallstrankModel):
    """A single AUM chart bar."""

    year: int
    quarter: int
    end_date: date
    aum: int | None = None


class FundReturnBar(WallstrankModel):
    """A single fund-return chart bar."""

    date: date
    percent: float | None = None
    spx_percent: float | None = None


class FeedItem(WallstrankModel):
    """A single item in the funds-portfolios feed."""

    fund: FundSummary
    reporting_year: int
    reporting_quarter: int
    updated_at: datetime = Field(...)
