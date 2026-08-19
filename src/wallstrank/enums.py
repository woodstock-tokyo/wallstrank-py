"""Shared enums used across Wall St. Rank API requests and responses."""

from __future__ import annotations

from enum import StrEnum

__all__ = [
    "ChartTimeframe",
    "FundHolderSortBy",
    "FundSortBy",
    "HolderStatus",
    "InsightSentiment",
    "InsightType",
    "MarketCap",
    "NetPositionSortBy",
    "NetTradeSortBy",
    "PortfolioSortBy",
    "Quarter",
    "SecurityType",
    "SecurityUniverse",
    "SortDir",
    "StockTrendSortBy",
]


class SortDir(StrEnum):
    """Sort direction for list endpoints."""

    ASC = "asc"
    DESC = "desc"


class Quarter(StrEnum):
    """Reporting quarter (rendered as a plain integer over the wire)."""

    Q1 = "1"
    Q2 = "2"
    Q3 = "3"
    Q4 = "4"


class SecurityType(StrEnum):
    """Security type for a fund position."""

    EQUITY = "equity"
    PUT = "put"
    CALL = "call"


class HolderStatus(StrEnum):
    """Position status returned for a fund holding."""

    NEW = "new"
    INCREASED = "increased"
    MAINTAINED = "maintained"
    REDUCED = "reduced"
    CLOSED = "closed"


class SecurityUniverse(StrEnum):
    """Universe filter used by fund-trend endpoints."""

    STOCK = "stock"
    ETF = "etf"


class MarketCap(StrEnum):
    """Market-cap bucket filter."""

    MEGA_CAP = "mega_cap"
    LARGE_CAP = "large_cap"
    MID_CAP = "mid_cap"
    SMALL_CAP = "small_cap"
    MICRO_CAP = "micro_cap"


class FundSortBy(StrEnum):
    """Sort fields for the /v1/funds endpoint."""

    LATEST_AUM = "latest_aum"
    RETURN_LATEST_QUARTER = "return_latest_quarter"
    RETURN_YEARS_1 = "return_years_1"
    RETURN_YEARS_3 = "return_years_3"
    RETURN_YEARS_5 = "return_years_5"
    RETURN_YEARS_10 = "return_years_10"


class PortfolioSortBy(StrEnum):
    """Sort fields for the /v1/funds-portfolios endpoint."""

    AUM = "aum"
    AUM_CHANGE_PERCENT = "aum_change_percent"


class FundHolderSortBy(StrEnum):
    """Sort fields for the fund-holders and holdings endpoints."""

    MARKET_VALUE = "market_value"
    SHARES = "shares"
    SHARES_LAST = "shares_last"
    SHARES_CHANGE = "shares_change"
    SHARES_CHANGE_PERCENT = "shares_change_percent"
    CAPITAL_FLOW = "capital_flow"
    PORTFOLIO_WEIGHT = "portfolio_weight"


class StockTrendSortBy(StrEnum):
    """Sort fields for count-based fund-trend endpoints."""

    CURRENT = "current"
    CHANGE = "change"
    CHANGE_PERCENT = "change_percent"


class NetPositionSortBy(StrEnum):
    """Sort fields for net new/closed/increased/reduced position endpoints."""

    NET = "net"
    NEW = "new"
    CLOSED = "closed"
    INCREASED = "increased"
    REDUCED = "reduced"


class NetTradeSortBy(StrEnum):
    """Sort fields for net calls/puts endpoints."""

    NET = "net"
    CALLS = "calls"
    PUTS = "puts"


class InsightType(StrEnum):
    """Type of insight in the fund confidence response."""

    CHANGE = "change"
    NET = "net"


class InsightSentiment(StrEnum):
    """Sentiment marker attached to fund confidence insights."""

    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class ChartTimeframe(StrEnum):
    """Timeframe keys returned by the return chart-bar endpoints."""

    ONE_MONTH = "1-month"
    THREE_MONTH = "3-month"
    SIX_MONTH = "6-month"
    YEAR_TO_DATE = "year-to-date"
    ONE_YEAR = "1-year"
    THREE_YEAR = "3-year"
    FIVE_YEAR = "5-year"
    TEN_YEAR = "10-year"
    ALL = "all"
