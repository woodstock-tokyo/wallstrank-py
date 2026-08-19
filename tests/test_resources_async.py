"""Async coverage for every endpoint documented at
https://www.wallstrank.com/docs/api/v1.

Mirrors ``tests/test_resources.py`` but exercises the async resource clients.
"""

from __future__ import annotations

import httpx
import respx

from conftest import load_fixture
from wallstrank import (
    AsyncWallstrankClient,
    ChartTimeframe,
    FundHolderSortBy,
    HolderStatus,
    MarketCap,
    SecurityType,
    SortDir,
)

# ---------------------------------------------------------------------------
# Reference
# ---------------------------------------------------------------------------


async def test_async_list_sectors(
    async_client: AsyncWallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/sectors").mock(
        return_value=httpx.Response(200, json=load_fixture("reference/sectors"))
    )
    sectors = await async_client.reference.list_sectors()
    assert len(sectors) == 3


async def test_async_list_industries(
    async_client: AsyncWallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/industries").mock(
        return_value=httpx.Response(200, json=load_fixture("reference/industries"))
    )
    industries = await async_client.reference.list_industries()
    assert industries[0].sector_id == "communication-services"


# ---------------------------------------------------------------------------
# Stocks
# ---------------------------------------------------------------------------


async def test_async_fund_holders(
    async_client: AsyncWallstrankClient, api_mock: respx.MockRouter
) -> None:
    route = api_mock.get("/v1/stocks/AAPL/fund-holders").mock(
        return_value=httpx.Response(200, json=load_fixture("stocks/fund-holders"))
    )
    result = await async_client.stocks.fund_holders(
        "AAPL",
        year=2025,
        quarter=1,
        status=[HolderStatus.NEW, HolderStatus.INCREASED],
        security_type=SecurityType.EQUITY,
        sort_by=FundHolderSortBy.MARKET_VALUE,
        sort_dir=SortDir.DESC,
        page=1,
        page_size=10,
    )
    query = dict(route.calls.last.request.url.params)
    assert query["status"] == "new,increased"
    assert result.holders[0].fund.id == "vanguard-group"


async def test_async_fund_stats(
    async_client: AsyncWallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/stocks/AAPL/fund-stats").mock(
        return_value=httpx.Response(200, json=load_fixture("stocks/fund-stats"))
    )
    stats = await async_client.stocks.fund_stats("AAPL", include_ongoing=True)
    assert stats.holders.total_positions == 4159


async def test_async_fund_confidence(
    async_client: AsyncWallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/stocks/AAPL/fund-confidence").mock(
        return_value=httpx.Response(200, json=load_fixture("stocks/fund-confidence"))
    )
    confidence = await async_client.stocks.fund_confidence("AAPL")
    assert len(confidence.insights) == 7


# ---------------------------------------------------------------------------
# Funds
# ---------------------------------------------------------------------------


async def test_async_funds_list(
    async_client: AsyncWallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/funds").mock(
        return_value=httpx.Response(200, json=load_fixture("funds/funds"))
    )
    funds = await async_client.funds.list(
        year=2025,
        quarter=1,
        sort_dir=SortDir.DESC,
        page=1,
        page_size=100,
    )
    assert funds.funds[0].id == "vanguard-group"


async def test_async_list_managers(
    async_client: AsyncWallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/fund-managers").mock(
        return_value=httpx.Response(200, json=load_fixture("funds/fund-managers"))
    )
    managers = await async_client.funds.list_managers(page=1, page_size=100)
    assert managers.managers[0].id == "warren-buffett"


async def test_async_list_portfolios(
    async_client: AsyncWallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/funds-portfolios").mock(
        return_value=httpx.Response(200, json=load_fixture("funds/portfolios"))
    )
    portfolios = await async_client.funds.list_portfolios(
        year=2025,
        quarter=1,
        include_ongoing=True,
    )
    assert portfolios.reporting_year == 2025


async def test_async_portfolio_single(
    async_client: AsyncWallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/funds/berkshire-hathaway/portfolio").mock(
        return_value=httpx.Response(200, json=load_fixture("funds/portfolio"))
    )
    portfolio = await async_client.funds.portfolio("berkshire-hathaway", year=2025, quarter=1)
    assert portfolio.fund.id == "berkshire-hathaway"


async def test_async_funds_holdings(
    async_client: AsyncWallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/funds-portfolios/berkshire-hathaway/holdings").mock(
        return_value=httpx.Response(200, json=load_fixture("funds/holdings"))
    )
    holdings = await async_client.funds.holdings(
        "berkshire-hathaway",
        year=2025,
        quarter=1,
        security_type=SecurityType.EQUITY,
        sort_dir=SortDir.DESC,
        page=1,
        page_size=100,
    )
    assert holdings.holdings[0].stock.ticker == "AAPL"


async def test_async_top_buys_sells(
    async_client: AsyncWallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/funds/berkshire-hathaway/top-buys-sells").mock(
        return_value=httpx.Response(200, json=load_fixture("funds/top-buys-sells"))
    )
    result = await async_client.funds.top_buys_sells("berkshire-hathaway", year=2025, quarter=1)
    assert result.buys[0].stock.ticker == "AAPL"


async def test_async_sector_composition(
    async_client: AsyncWallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/funds/berkshire-hathaway/sector-composition").mock(
        return_value=httpx.Response(200, json=load_fixture("funds/sector-composition"))
    )
    result = await async_client.funds.sector_composition("berkshire-hathaway", year=2025, quarter=1)
    assert result.composition[0].sector.id == "technology"


# ---------------------------------------------------------------------------
# Fund trends
# ---------------------------------------------------------------------------


async def test_async_fund_trends_holding(
    async_client: AsyncWallstrankClient, api_mock: respx.MockRouter
) -> None:
    route = api_mock.get("/v1/fund-trends/holding").mock(
        return_value=httpx.Response(200, json=load_fixture("fund-trends/holding"))
    )
    result = await async_client.fund_trends.holding(
        market_cap=[MarketCap.MEGA_CAP, MarketCap.LARGE_CAP],
        sector="technology",
    )
    query = dict(route.calls.last.request.url.params)
    assert query["market_cap"] == "mega_cap,large_cap"
    assert result.stocks[0].stock.ticker == "AAPL"


async def test_async_fund_trends_holding_in_top_10(
    async_client: AsyncWallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/fund-trends/holding-in-top-10").mock(
        return_value=httpx.Response(200, json=load_fixture("fund-trends/holding-in-top-10"))
    )
    result = await async_client.fund_trends.holding_in_top_10()
    assert result.stocks[0].current == 1477


async def test_async_fund_trends_new_positions(
    async_client: AsyncWallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/fund-trends/new-positions").mock(
        return_value=httpx.Response(200, json=load_fixture("fund-trends/new-positions"))
    )
    result = await async_client.fund_trends.new_positions()
    assert result.stocks[0].current == 451


async def test_async_fund_trends_closed_positions(
    async_client: AsyncWallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/fund-trends/closed-positions").mock(
        return_value=httpx.Response(200, json=load_fixture("fund-trends/closed-positions"))
    )
    result = await async_client.fund_trends.closed_positions()
    assert result.stocks[0].current == 191


async def test_async_fund_trends_increased_positions(
    async_client: AsyncWallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/fund-trends/increased-positions").mock(
        return_value=httpx.Response(200, json=load_fixture("fund-trends/increased-positions"))
    )
    result = await async_client.fund_trends.increased_positions()
    assert result.stocks[0].current == 1575


async def test_async_fund_trends_reduced_positions(
    async_client: AsyncWallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/fund-trends/reduced-positions").mock(
        return_value=httpx.Response(200, json=load_fixture("fund-trends/reduced-positions"))
    )
    result = await async_client.fund_trends.reduced_positions()
    assert result.stocks[0].current == 1918


async def test_async_fund_trends_calls(
    async_client: AsyncWallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/fund-trends/calls").mock(
        return_value=httpx.Response(200, json=load_fixture("fund-trends/calls"))
    )
    result = await async_client.fund_trends.calls()
    assert result.stocks[0].current == 120124623000


async def test_async_fund_trends_puts(
    async_client: AsyncWallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/fund-trends/puts").mock(
        return_value=httpx.Response(200, json=load_fixture("fund-trends/puts"))
    )
    result = await async_client.fund_trends.puts()
    assert result.stocks[0].current == 126155337000


async def test_async_fund_trends_net_new_positions(
    async_client: AsyncWallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/fund-trends/net-new-positions").mock(
        return_value=httpx.Response(200, json=load_fixture("fund-trends/net-new-positions"))
    )
    result = await async_client.fund_trends.net_new_positions()
    assert result.stocks[0].net_new_positions == 260


async def test_async_fund_trends_net_closed_positions(
    async_client: AsyncWallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/fund-trends/net-closed-positions").mock(
        return_value=httpx.Response(200, json=load_fixture("fund-trends/net-closed-positions"))
    )
    result = await async_client.fund_trends.net_closed_positions()
    assert result.stocks[0].net_closed_positions == -260


async def test_async_fund_trends_net_increased_positions(
    async_client: AsyncWallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/fund-trends/net-increased-positions").mock(
        return_value=httpx.Response(200, json=load_fixture("fund-trends/net-increased-positions"))
    )
    result = await async_client.fund_trends.net_increased_positions()
    assert result.stocks[0].net_increased_positions == -343


async def test_async_fund_trends_net_reduced_positions(
    async_client: AsyncWallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/fund-trends/net-reduced-positions").mock(
        return_value=httpx.Response(200, json=load_fixture("fund-trends/net-reduced-positions"))
    )
    result = await async_client.fund_trends.net_reduced_positions()
    assert result.stocks[0].net_reduced_positions == 343


async def test_async_fund_trends_net_calls(
    async_client: AsyncWallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/fund-trends/net-calls").mock(
        return_value=httpx.Response(200, json=load_fixture("fund-trends/net-calls"))
    )
    result = await async_client.fund_trends.net_calls()
    assert result.stocks[0].net_calls == -6030714000


async def test_async_fund_trends_net_puts(
    async_client: AsyncWallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/fund-trends/net-puts").mock(
        return_value=httpx.Response(200, json=load_fixture("fund-trends/net-puts"))
    )
    result = await async_client.fund_trends.net_puts()
    assert result.stocks[0].net_puts == 6030714000


# ---------------------------------------------------------------------------
# Fund chart bars
# ---------------------------------------------------------------------------


async def test_async_aum_chart(
    async_client: AsyncWallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/funds/berkshire-hathaway/chart-bars/aum").mock(
        return_value=httpx.Response(200, json=load_fixture("fund-chart-bars/aum"))
    )
    result = await async_client.fund_chart_bars.aum("berkshire-hathaway")
    assert result.bars[-1].aum == 5531119721493


async def test_async_return_chart(
    async_client: AsyncWallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/funds/vanguard-group/chart-bars/return").mock(
        return_value=httpx.Response(200, json=load_fixture("fund-chart-bars/return"))
    )
    result = await async_client.fund_chart_bars.return_("vanguard-group")
    assert ChartTimeframe.ONE_MONTH in result.bars_by_timeframe


async def test_async_top_20_return_chart(
    async_client: AsyncWallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/funds/vanguard-group/chart-bars/top-20-return").mock(
        return_value=httpx.Response(200, json=load_fixture("fund-chart-bars/top-20-return"))
    )
    result = await async_client.fund_chart_bars.top_20_return("vanguard-group")
    assert result.timeframe(ChartTimeframe.ONE_YEAR)[0].percent == 16.02


async def test_async_top_15_return_chart(
    async_client: AsyncWallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/funds/vanguard-group/chart-bars/top-15-return").mock(
        return_value=httpx.Response(200, json=load_fixture("fund-chart-bars/top-15-return"))
    )
    result = await async_client.fund_chart_bars.top_15_return("vanguard-group")
    assert result.timeframe(ChartTimeframe.ONE_YEAR)[0].percent == 17.4


async def test_async_top_10_return_chart(
    async_client: AsyncWallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/funds/vanguard-group/chart-bars/top-10-return").mock(
        return_value=httpx.Response(200, json=load_fixture("fund-chart-bars/top-10-return"))
    )
    result = await async_client.fund_chart_bars.top_10_return("vanguard-group")
    assert result.timeframe(ChartTimeframe.ONE_YEAR)[0].percent == 18.9


async def test_async_post_disclosure_return_chart(
    async_client: AsyncWallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/funds/vanguard-group/chart-bars/post-disclosure-return").mock(
        return_value=httpx.Response(
            200, json=load_fixture("fund-chart-bars/post-disclosure-return")
        )
    )
    result = await async_client.fund_chart_bars.post_disclosure_return("vanguard-group")
    assert result.timeframe(ChartTimeframe.ONE_YEAR)[0].percent == 15.2


async def test_async_top_20_post_disclosure_return_chart(
    async_client: AsyncWallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/funds/vanguard-group/chart-bars/top-20-post-disclosure-return").mock(
        return_value=httpx.Response(
            200, json=load_fixture("fund-chart-bars/top-20-post-disclosure-return")
        )
    )
    result = await async_client.fund_chart_bars.top_20_post_disclosure_return("vanguard-group")
    assert result.timeframe(ChartTimeframe.ONE_YEAR)[0].percent == 16.9


async def test_async_top_15_post_disclosure_return_chart(
    async_client: AsyncWallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/funds/vanguard-group/chart-bars/top-15-post-disclosure-return").mock(
        return_value=httpx.Response(
            200, json=load_fixture("fund-chart-bars/top-15-post-disclosure-return")
        )
    )
    result = await async_client.fund_chart_bars.top_15_post_disclosure_return("vanguard-group")
    assert result.timeframe(ChartTimeframe.ONE_YEAR)[0].percent == 18.2


async def test_async_top_10_post_disclosure_return_chart(
    async_client: AsyncWallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/funds/vanguard-group/chart-bars/top-10-post-disclosure-return").mock(
        return_value=httpx.Response(
            200, json=load_fixture("fund-chart-bars/top-10-post-disclosure-return")
        )
    )
    result = await async_client.fund_chart_bars.top_10_post_disclosure_return("vanguard-group")
    assert result.timeframe(ChartTimeframe.ONE_YEAR)[0].percent == 19.7


# ---------------------------------------------------------------------------
# Feeds
# ---------------------------------------------------------------------------


async def test_async_feeds_funds_portfolios(
    async_client: AsyncWallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/feeds/funds-portfolios").mock(
        return_value=httpx.Response(200, json=load_fixture("feeds/funds-portfolios"))
    )
    result = await async_client.feeds.funds_portfolios(page=1, page_size=100)
    assert result.items[0].fund.id == "berkshire-hathaway"
