"""Tests for the resource clients.

Covers every endpoint documented at
https://www.wallstrank.com/docs/api/v1 — parameter encoding, path building,
and response parsing — using JSON fixtures under ``tests/fixtures/``.
"""

from __future__ import annotations

import httpx
import pytest
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
    WallstrankClient,
)

# ---------------------------------------------------------------------------
# Reference
# ---------------------------------------------------------------------------


def test_list_sectors(client: WallstrankClient, api_mock: respx.MockRouter) -> None:
    api_mock.get("/v1/sectors").mock(
        return_value=httpx.Response(200, json=load_fixture("reference/sectors"))
    )
    sectors = client.reference.list_sectors()
    assert [s.id for s in sectors] == [
        "communication-services",
        "consumer-discretionary",
        "consumer-staples",
    ]


def test_list_industries(client: WallstrankClient, api_mock: respx.MockRouter) -> None:
    api_mock.get("/v1/industries").mock(
        return_value=httpx.Response(200, json=load_fixture("reference/industries"))
    )
    industries = client.reference.list_industries()
    assert industries[0].sector_id == "communication-services"
    assert {i.id for i in industries} == {
        "advertising-agencies",
        "aerospace-defense",
        "agricultural-inputs",
    }


def test_list_sectors_accepts_bare_list(
    client: WallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/sectors").mock(
        return_value=httpx.Response(200, json=[{"id": "energy", "name": "Energy"}])
    )
    sectors = client.reference.list_sectors()
    assert [s.id for s in sectors] == ["energy"]


def test_list_industries_accepts_bare_list(
    client: WallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/industries").mock(
        return_value=httpx.Response(
            200,
            json=[{"id": "airlines", "name": "Airlines", "sector_id": "industrials"}],
        )
    )
    industries = client.reference.list_industries()
    assert industries[0].sector_id == "industrials"


# ---------------------------------------------------------------------------
# Stocks
# ---------------------------------------------------------------------------


def test_fund_holders_encodes_params(client: WallstrankClient, api_mock: respx.MockRouter) -> None:
    route = api_mock.get("/v1/stocks/AAPL/fund-holders").mock(
        return_value=httpx.Response(200, json=load_fixture("stocks/fund-holders"))
    )
    result = client.stocks.fund_holders(
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
    assert query == {
        "year": "2025",
        "quarter": "1",
        "status": "new,increased",
        "security_type": "equity",
        "sort_by": "market_value",
        "sort_dir": "desc",
        "page": "1",
        "page_size": "10",
    }
    assert result.reporting_year == 2025
    assert result.holders[0].fund.id == "vanguard-group"
    assert result.holders[0].security_type is SecurityType.EQUITY
    assert result.holders[-1].security_type is SecurityType.CALL


def test_fund_stats(client: WallstrankClient, api_mock: respx.MockRouter) -> None:
    api_mock.get("/v1/stocks/AAPL/fund-stats").mock(
        return_value=httpx.Response(200, json=load_fixture("stocks/fund-stats"))
    )
    stats = client.stocks.fund_stats("AAPL", include_ongoing=True)
    assert stats.holders.total_positions == 4159
    assert stats.holders.new_positions == 451
    assert stats.holders.closed_positions == 191


def test_fund_confidence(client: WallstrankClient, api_mock: respx.MockRouter) -> None:
    api_mock.get("/v1/stocks/AAPL/fund-confidence").mock(
        return_value=httpx.Response(200, json=load_fixture("stocks/fund-confidence"))
    )
    confidence = client.stocks.fund_confidence("AAPL")
    ids = [insight.id for insight in confidence.insights]
    assert "funds-holding" in ids
    assert "net-calls" in ids
    assert len(confidence.insights) == 7


# ---------------------------------------------------------------------------
# Funds
# ---------------------------------------------------------------------------


def test_funds_list(client: WallstrankClient, api_mock: respx.MockRouter) -> None:
    api_mock.get("/v1/funds").mock(
        return_value=httpx.Response(200, json=load_fixture("funds/funds"))
    )
    funds = client.funds.list()
    assert funds.funds[0].id == "vanguard-group"
    assert funds.has_more_pages is False


def test_list_managers(client: WallstrankClient, api_mock: respx.MockRouter) -> None:
    api_mock.get("/v1/fund-managers").mock(
        return_value=httpx.Response(200, json=load_fixture("funds/fund-managers"))
    )
    managers = client.funds.list_managers()
    assert managers.managers[0].id == "warren-buffett"
    assert managers.managers[0].fund is not None
    assert managers.managers[0].fund.id == "berkshire-hathaway"


def test_list_portfolios(client: WallstrankClient, api_mock: respx.MockRouter) -> None:
    api_mock.get("/v1/funds-portfolios").mock(
        return_value=httpx.Response(200, json=load_fixture("funds/portfolios"))
    )
    portfolios = client.funds.list_portfolios(year=2025, quarter=1)
    assert portfolios.reporting_year == 2025
    assert portfolios.portfolios[0].fund.id == "vanguard-group"
    assert portfolios.portfolios[1].aum == 258713622674


def test_portfolio_single(client: WallstrankClient, api_mock: respx.MockRouter) -> None:
    api_mock.get("/v1/funds/berkshire-hathaway/portfolio").mock(
        return_value=httpx.Response(200, json=load_fixture("funds/portfolio"))
    )
    portfolio = client.funds.portfolio("berkshire-hathaway")
    assert portfolio.fund.id == "berkshire-hathaway"
    assert portfolio.reporting_year == 2025
    assert portfolio.holdings == 36
    assert portfolio.fund_managers[0].id == "warren-buffett"


def test_funds_holdings(client: WallstrankClient, api_mock: respx.MockRouter) -> None:
    api_mock.get("/v1/funds-portfolios/berkshire-hathaway/holdings").mock(
        return_value=httpx.Response(200, json=load_fixture("funds/holdings"))
    )
    holdings = client.funds.holdings("berkshire-hathaway")
    assert holdings.holdings[0].stock.ticker == "AAPL"
    assert holdings.holdings[0].security_type is SecurityType.EQUITY


def test_top_buys_sells(client: WallstrankClient, api_mock: respx.MockRouter) -> None:
    api_mock.get("/v1/funds/berkshire-hathaway/top-buys-sells").mock(
        return_value=httpx.Response(200, json=load_fixture("funds/top-buys-sells"))
    )
    result = client.funds.top_buys_sells("berkshire-hathaway")
    assert result.buys[0].stock.ticker == "AAPL"
    assert result.sells[0].stock.ticker == "BAC"


def test_sector_composition(client: WallstrankClient, api_mock: respx.MockRouter) -> None:
    api_mock.get("/v1/funds/berkshire-hathaway/sector-composition").mock(
        return_value=httpx.Response(200, json=load_fixture("funds/sector-composition"))
    )
    result = client.funds.sector_composition("berkshire-hathaway")
    assert result.composition[0].sector.id == "technology"
    assert result.composition[0].percent == 42.35


# ---------------------------------------------------------------------------
# Fund trends
# ---------------------------------------------------------------------------


def test_fund_trends_holding_encodes_params(
    client: WallstrankClient, api_mock: respx.MockRouter
) -> None:
    route = api_mock.get("/v1/fund-trends/holding").mock(
        return_value=httpx.Response(200, json=load_fixture("fund-trends/holding"))
    )
    result = client.fund_trends.holding(
        market_cap=[MarketCap.MEGA_CAP, MarketCap.LARGE_CAP],
        sector="technology",
    )
    query = dict(route.calls.last.request.url.params)
    assert query["market_cap"] == "mega_cap,large_cap"
    assert query["sector"] == "technology"
    assert result.stocks[0].stock.ticker == "AAPL"


def test_fund_trends_holding_in_top_10(
    client: WallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/fund-trends/holding-in-top-10").mock(
        return_value=httpx.Response(200, json=load_fixture("fund-trends/holding-in-top-10"))
    )
    result = client.fund_trends.holding_in_top_10()
    assert result.stocks[0].change_percent == 40.94


def test_fund_trends_new_positions(client: WallstrankClient, api_mock: respx.MockRouter) -> None:
    api_mock.get("/v1/fund-trends/new-positions").mock(
        return_value=httpx.Response(200, json=load_fixture("fund-trends/new-positions"))
    )
    result = client.fund_trends.new_positions()
    assert result.stocks[0].current == 451


def test_fund_trends_closed_positions(client: WallstrankClient, api_mock: respx.MockRouter) -> None:
    api_mock.get("/v1/fund-trends/closed-positions").mock(
        return_value=httpx.Response(200, json=load_fixture("fund-trends/closed-positions"))
    )
    result = client.fund_trends.closed_positions()
    assert result.stocks[0].current == 191


def test_fund_trends_increased_positions(
    client: WallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/fund-trends/increased-positions").mock(
        return_value=httpx.Response(200, json=load_fixture("fund-trends/increased-positions"))
    )
    result = client.fund_trends.increased_positions()
    assert result.stocks[0].current == 1575


def test_fund_trends_reduced_positions(
    client: WallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/fund-trends/reduced-positions").mock(
        return_value=httpx.Response(200, json=load_fixture("fund-trends/reduced-positions"))
    )
    result = client.fund_trends.reduced_positions()
    assert result.stocks[0].current == 1918


def test_fund_trends_calls(client: WallstrankClient, api_mock: respx.MockRouter) -> None:
    api_mock.get("/v1/fund-trends/calls").mock(
        return_value=httpx.Response(200, json=load_fixture("fund-trends/calls"))
    )
    result = client.fund_trends.calls()
    assert result.stocks[0].current == 120124623000


def test_fund_trends_puts(client: WallstrankClient, api_mock: respx.MockRouter) -> None:
    api_mock.get("/v1/fund-trends/puts").mock(
        return_value=httpx.Response(200, json=load_fixture("fund-trends/puts"))
    )
    result = client.fund_trends.puts()
    assert result.stocks[0].current == 126155337000


def test_fund_trends_net_new_positions(
    client: WallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/fund-trends/net-new-positions").mock(
        return_value=httpx.Response(200, json=load_fixture("fund-trends/net-new-positions"))
    )
    result = client.fund_trends.net_new_positions()
    assert result.stocks[0].net_new_positions == 260


def test_fund_trends_net_closed_positions(
    client: WallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/fund-trends/net-closed-positions").mock(
        return_value=httpx.Response(200, json=load_fixture("fund-trends/net-closed-positions"))
    )
    result = client.fund_trends.net_closed_positions()
    assert result.stocks[0].net_closed_positions == -260


def test_fund_trends_net_increased_positions(
    client: WallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/fund-trends/net-increased-positions").mock(
        return_value=httpx.Response(200, json=load_fixture("fund-trends/net-increased-positions"))
    )
    result = client.fund_trends.net_increased_positions()
    assert result.stocks[0].net_increased_positions == -343


def test_fund_trends_net_reduced_positions(
    client: WallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/fund-trends/net-reduced-positions").mock(
        return_value=httpx.Response(200, json=load_fixture("fund-trends/net-reduced-positions"))
    )
    result = client.fund_trends.net_reduced_positions()
    assert result.stocks[0].net_reduced_positions == 343


def test_fund_trends_net_calls(client: WallstrankClient, api_mock: respx.MockRouter) -> None:
    api_mock.get("/v1/fund-trends/net-calls").mock(
        return_value=httpx.Response(200, json=load_fixture("fund-trends/net-calls"))
    )
    result = client.fund_trends.net_calls()
    assert result.stocks[0].net_calls == -6030714000


def test_fund_trends_net_puts(client: WallstrankClient, api_mock: respx.MockRouter) -> None:
    api_mock.get("/v1/fund-trends/net-puts").mock(
        return_value=httpx.Response(200, json=load_fixture("fund-trends/net-puts"))
    )
    result = client.fund_trends.net_puts()
    assert result.stocks[0].net_puts == 6030714000


# ---------------------------------------------------------------------------
# Fund chart bars
# ---------------------------------------------------------------------------


def test_aum_chart(client: WallstrankClient, api_mock: respx.MockRouter) -> None:
    api_mock.get("/v1/funds/berkshire-hathaway/chart-bars/aum").mock(
        return_value=httpx.Response(200, json=load_fixture("fund-chart-bars/aum"))
    )
    result = client.fund_chart_bars.aum("berkshire-hathaway")
    assert result.bars[0].aum == 5741207245727
    assert result.bars[-1].aum == 5531119721493


def test_aum_chart_accepts_bare_list(client: WallstrankClient, api_mock: respx.MockRouter) -> None:
    api_mock.get("/v1/funds/berkshire-hathaway/chart-bars/aum").mock(
        return_value=httpx.Response(
            200,
            json=[{"year": 2025, "quarter": 1, "end_date": "2025-03-31", "aum": 100}],
        )
    )
    result = client.fund_chart_bars.aum("berkshire-hathaway")
    assert result.bars[0].aum == 100


def test_return_chart_rejects_non_dict_payload(
    client: WallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/funds/vanguard-group/chart-bars/return").mock(
        return_value=httpx.Response(200, json=["oops"])
    )
    with pytest.raises(TypeError):
        client.fund_chart_bars.return_("vanguard-group")


def test_return_chart_parses_timeframes_and_skips_unknown(
    client: WallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/funds/vanguard-group/chart-bars/return").mock(
        return_value=httpx.Response(200, json=load_fixture("fund-chart-bars/return"))
    )
    result = client.fund_chart_bars.return_("vanguard-group")
    # All 9 known timeframes should parse.
    for tf in ChartTimeframe:
        assert tf in result.bars_by_timeframe
    # The unknown ``42-year`` timeframe should be silently dropped.
    assert len(result.bars_by_timeframe) == len(list(ChartTimeframe))
    assert result.timeframe("1-month")[-1].percent == -2.6


def test_top_20_return_chart(client: WallstrankClient, api_mock: respx.MockRouter) -> None:
    api_mock.get("/v1/funds/vanguard-group/chart-bars/top-20-return").mock(
        return_value=httpx.Response(200, json=load_fixture("fund-chart-bars/top-20-return"))
    )
    result = client.fund_chart_bars.top_20_return("vanguard-group")
    assert result.timeframe(ChartTimeframe.ONE_YEAR)[0].percent == 16.02


def test_top_15_return_chart(client: WallstrankClient, api_mock: respx.MockRouter) -> None:
    api_mock.get("/v1/funds/vanguard-group/chart-bars/top-15-return").mock(
        return_value=httpx.Response(200, json=load_fixture("fund-chart-bars/top-15-return"))
    )
    result = client.fund_chart_bars.top_15_return("vanguard-group")
    assert result.timeframe(ChartTimeframe.ONE_YEAR)[0].percent == 17.4


def test_top_10_return_chart(client: WallstrankClient, api_mock: respx.MockRouter) -> None:
    api_mock.get("/v1/funds/vanguard-group/chart-bars/top-10-return").mock(
        return_value=httpx.Response(200, json=load_fixture("fund-chart-bars/top-10-return"))
    )
    result = client.fund_chart_bars.top_10_return("vanguard-group")
    assert result.timeframe(ChartTimeframe.ONE_YEAR)[0].percent == 18.9


def test_post_disclosure_return_chart(client: WallstrankClient, api_mock: respx.MockRouter) -> None:
    api_mock.get("/v1/funds/vanguard-group/chart-bars/post-disclosure-return").mock(
        return_value=httpx.Response(
            200, json=load_fixture("fund-chart-bars/post-disclosure-return")
        )
    )
    result = client.fund_chart_bars.post_disclosure_return("vanguard-group")
    assert result.timeframe(ChartTimeframe.ONE_YEAR)[0].percent == 15.2


def test_top_20_post_disclosure_return_chart(
    client: WallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/funds/vanguard-group/chart-bars/top-20-post-disclosure-return").mock(
        return_value=httpx.Response(
            200, json=load_fixture("fund-chart-bars/top-20-post-disclosure-return")
        )
    )
    result = client.fund_chart_bars.top_20_post_disclosure_return("vanguard-group")
    assert result.timeframe(ChartTimeframe.ONE_YEAR)[0].percent == 16.9


def test_top_15_post_disclosure_return_chart(
    client: WallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/funds/vanguard-group/chart-bars/top-15-post-disclosure-return").mock(
        return_value=httpx.Response(
            200, json=load_fixture("fund-chart-bars/top-15-post-disclosure-return")
        )
    )
    result = client.fund_chart_bars.top_15_post_disclosure_return("vanguard-group")
    assert result.timeframe(ChartTimeframe.ONE_YEAR)[0].percent == 18.2


def test_top_10_post_disclosure_return_chart(
    client: WallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/funds/vanguard-group/chart-bars/top-10-post-disclosure-return").mock(
        return_value=httpx.Response(
            200, json=load_fixture("fund-chart-bars/top-10-post-disclosure-return")
        )
    )
    result = client.fund_chart_bars.top_10_post_disclosure_return("vanguard-group")
    assert result.timeframe(ChartTimeframe.ONE_YEAR)[0].percent == 19.7


# ---------------------------------------------------------------------------
# Feeds
# ---------------------------------------------------------------------------


def test_feeds_funds_portfolios(client: WallstrankClient, api_mock: respx.MockRouter) -> None:
    route = api_mock.get("/v1/feeds/funds-portfolios").mock(
        return_value=httpx.Response(200, json=load_fixture("feeds/funds-portfolios"))
    )
    result = client.feeds.funds_portfolios(page=1, page_size=100)
    query = dict(route.calls.last.request.url.params)
    assert query == {"page": "1", "page_size": "100"}
    assert result.items[0].fund.id == "berkshire-hathaway"
    assert result.items[1].fund.id == "vanguard-group"


# ---------------------------------------------------------------------------
# Async smoke test
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_async_client_hits_endpoint(
    async_client: AsyncWallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/sectors").mock(
        return_value=httpx.Response(200, json=load_fixture("reference/sectors"))
    )
    sectors = await async_client.reference.list_sectors()
    assert len(sectors) == 3
