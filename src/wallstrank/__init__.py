"""Wall St. Rank API client library.

The public API surface exposes two clients — :class:`WallstrankClient` and
:class:`AsyncWallstrankClient` — along with typed request/response models and
the exception hierarchy.

See https://www.wallstrank.com/docs/api/v1/introduction for full API details.
"""

from __future__ import annotations

from .__about__ import __version__
from .client import AsyncWallstrankClient, WallstrankClient
from .enums import (
    ChartTimeframe,
    FundHolderSortBy,
    FundSortBy,
    HolderStatus,
    InsightSentiment,
    InsightType,
    MarketCap,
    NetPositionSortBy,
    NetTradeSortBy,
    PortfolioSortBy,
    Quarter,
    SecurityType,
    SecurityUniverse,
    SortDir,
    StockTrendSortBy,
)
from .exceptions import (
    APIError,
    AuthenticationError,
    BadRequestError,
    ForbiddenError,
    NotFoundError,
    RequestFailedError,
    ServerError,
    WallstrankError,
)
from .pagination import (
    DEFAULT_MAX_PAGES,
    HasMorePages,
    PaginationLimitExceededError,
    apaginate,
    paginate,
)
from .periods import iter_quarters, prior_quarter
from .tickers import TICKER_PATTERN, normalize_ticker, parse_tickers, validate_ticker

__all__ = [
    "DEFAULT_MAX_PAGES",
    "TICKER_PATTERN",
    "APIError",
    "AsyncWallstrankClient",
    "AuthenticationError",
    "BadRequestError",
    "ChartTimeframe",
    "ForbiddenError",
    "FundHolderSortBy",
    "FundSortBy",
    "HasMorePages",
    "HolderStatus",
    "InsightSentiment",
    "InsightType",
    "MarketCap",
    "NetPositionSortBy",
    "NetTradeSortBy",
    "NotFoundError",
    "PaginationLimitExceededError",
    "PortfolioSortBy",
    "Quarter",
    "RequestFailedError",
    "SecurityType",
    "SecurityUniverse",
    "ServerError",
    "SortDir",
    "StockTrendSortBy",
    "WallstrankClient",
    "WallstrankError",
    "__version__",
    "apaginate",
    "iter_quarters",
    "normalize_ticker",
    "paginate",
    "parse_tickers",
    "prior_quarter",
    "validate_ticker",
]
