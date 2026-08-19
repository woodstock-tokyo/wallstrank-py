"""Top-level Wall St. Rank clients that expose all resources."""

from __future__ import annotations

from types import TracebackType
from typing import Self

import httpx

from ._http import (
    DEFAULT_BASE_URL,
    DEFAULT_TIMEOUT,
    AsyncBaseHTTPClient,
    BaseHTTPClient,
)
from .resources import (
    AsyncFeedsResource,
    AsyncFundChartBarsResource,
    AsyncFundsResource,
    AsyncFundTrendsResource,
    AsyncReferenceResource,
    AsyncStocksResource,
    FeedsResource,
    FundChartBarsResource,
    FundsResource,
    FundTrendsResource,
    ReferenceResource,
    StocksResource,
)

__all__ = [
    "AsyncWallstrankClient",
    "WallstrankClient",
]


class WallstrankClient:
    """Synchronous Wall St. Rank API client.

    All resources are exposed as attributes: ``stocks``, ``funds``,
    ``fund_trends``, ``fund_chart_bars``, ``reference``, and ``feeds``.

    Example:
        >>> from wallstrank import WallstrankClient
        >>> client = WallstrankClient(api_key="...")
        >>> aapl_holders = client.stocks.fund_holders("AAPL", page_size=10)
        >>> len(aapl_holders.holders)
        10
    """

    stocks: StocksResource
    funds: FundsResource
    fund_trends: FundTrendsResource
    fund_chart_bars: FundChartBarsResource
    reference: ReferenceResource
    feeds: FeedsResource

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = 3,
        retry_backoff: float = 0.5,
        user_agent: str | None = None,
        http_client: httpx.Client | None = None,
    ) -> None:
        self._http = BaseHTTPClient(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            retry_backoff=retry_backoff,
            user_agent=user_agent,
            http_client=http_client,
        )
        self.stocks = StocksResource(self._http)
        self.funds = FundsResource(self._http)
        self.fund_trends = FundTrendsResource(self._http)
        self.fund_chart_bars = FundChartBarsResource(self._http)
        self.reference = ReferenceResource(self._http)
        self.feeds = FeedsResource(self._http)

    @property
    def base_url(self) -> str:
        return self._http.base_url

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.close()


class AsyncWallstrankClient:
    """Asynchronous Wall St. Rank API client.

    Example:
        >>> import asyncio
        >>> from wallstrank import AsyncWallstrankClient
        >>>
        >>> async def main() -> None:
        ...     async with AsyncWallstrankClient(api_key="...") as client:
        ...         funds = await client.funds.list(page_size=5)
        ...         print(len(funds.funds))
        >>>
        >>> asyncio.run(main())
    """

    stocks: AsyncStocksResource
    funds: AsyncFundsResource
    fund_trends: AsyncFundTrendsResource
    fund_chart_bars: AsyncFundChartBarsResource
    reference: AsyncReferenceResource
    feeds: AsyncFeedsResource

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = 3,
        retry_backoff: float = 0.5,
        user_agent: str | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._http = AsyncBaseHTTPClient(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            retry_backoff=retry_backoff,
            user_agent=user_agent,
            http_client=http_client,
        )
        self.stocks = AsyncStocksResource(self._http)
        self.funds = AsyncFundsResource(self._http)
        self.fund_trends = AsyncFundTrendsResource(self._http)
        self.fund_chart_bars = AsyncFundChartBarsResource(self._http)
        self.reference = AsyncReferenceResource(self._http)
        self.feeds = AsyncFeedsResource(self._http)

    @property
    def base_url(self) -> str:
        return self._http.base_url

    async def aclose(self) -> None:
        await self._http.aclose()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.aclose()
