# wallstrank-py

[![PyPI version](https://img.shields.io/pypi/v/wallstrank-py.svg)](https://pypi.org/project/wallstrank-py/)
[![Python versions](https://img.shields.io/pypi/pyversions/wallstrank-py.svg)](https://pypi.org/project/wallstrank-py/)
[![CI](https://github.com/woodstock-tokyo/wallstrank-py/actions/workflows/ci.yml/badge.svg)](https://github.com/woodstock-tokyo/wallstrank-py/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/woodstock-tokyo/wallstrank-py/branch/master/graph/badge.svg)](https://codecov.io/gh/woodstock-tokyo/wallstrank-py)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)

Typed Python client for the [Wall St. Rank](https://www.wallstrank.com) API. Access fund
portfolios, holdings, trades and trends with a single dependency-light SDK.

- Sync **and** async clients (`WallstrankClient`, `AsyncWallstrankClient`)
- Full endpoint coverage of the [v1 REST API](https://www.wallstrank.com/docs/api/v1/introduction)
- Fully typed responses backed by [pydantic](https://docs.pydantic.dev/) v2
- Automatic retries for transient network / 5xx errors
- Typed exception hierarchy (`AuthenticationError`, `NotFoundError`, …)
- Built for Python 3.12+

## Installation

```bash
pip install wallstrank-py
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add wallstrank-py
```

## Quickstart

```python
from wallstrank import WallstrankClient

client = WallstrankClient(api_key="YOUR_API_KEY")

# Top 10 funds holding AAPL this quarter
holders = client.stocks.fund_holders("AAPL", page_size=10)
for holder in holders.holders:
    print(holder.fund.name, holder.market_value, holder.status)

# Berkshire's latest sector composition
composition = client.funds.sector_composition("berkshire-hathaway")
for row in composition.composition:
    print(row.sector.name, f"{row.percent}%")

client.close()
```

The client also works as a context manager:

```python
with WallstrankClient(api_key="...") as client:
    funds = client.funds.list(page_size=25)
```

### Async usage

```python
import asyncio
from wallstrank import AsyncWallstrankClient


async def main() -> None:
    async with AsyncWallstrankClient(api_key="...") as client:
        buys = await client.funds.top_buys_sells("warren-buffett")
        for trade in buys.buys:
            print(trade.stock.ticker, trade.capital_flow)


asyncio.run(main())
```

## Configuration

`WallstrankClient` / `AsyncWallstrankClient` accept the following keyword arguments:

| Parameter        | Default                             | Description                                            |
|------------------|-------------------------------------|--------------------------------------------------------|
| `api_key`        | (required)                          | Your Wall St. Rank API key.                            |
| `base_url`       | `https://api.wallstrank.com`        | Override for testing / staging.                        |
| `timeout`        | `30.0`                              | Per-request timeout (seconds).                         |
| `max_retries`    | `3`                                 | Retry attempts for network + 5xx / 429 / 408 errors.   |
| `retry_backoff`  | `0.5`                               | Base backoff for exponential retries (seconds).        |
| `user_agent`     | `wallstrank-py/<version>`           | Custom User-Agent header.                              |
| `http_client`    | `None`                              | Bring your own `httpx.Client` / `httpx.AsyncClient`.   |

## Resources

The client is organised into resource namespaces that mirror the API:

| Namespace                    | Endpoints                                                                                             |
|------------------------------|-------------------------------------------------------------------------------------------------------|
| `client.stocks`              | `fund_holders`, `fund_stats`, `fund_confidence`                                                       |
| `client.reference`           | `list_sectors`, `list_industries`                                                                     |
| `client.funds`               | `list`, `list_managers`, `list_portfolios`, `portfolio`, `holdings`, `top_buys_sells`, `sector_composition` |
| `client.fund_trends`         | `holding`, `holding_in_top_10`, `new_positions`, `closed_positions`, `increased_positions`, `reduced_positions`, `calls`, `puts`, `net_new_positions`, `net_closed_positions`, `net_increased_positions`, `net_reduced_positions`, `net_calls`, `net_puts` |
| `client.fund_chart_bars`     | `aum`, `return_`, `top_10_return`, `top_15_return`, `top_20_return`, `post_disclosure_return`, `top_10_post_disclosure_return`, `top_15_post_disclosure_return`, `top_20_post_disclosure_return` |
| `client.feeds`               | `funds_portfolios`                                                                                    |

Every method returns a strongly typed pydantic model.

## Enums

Common parameter enums are re-exported from the package root:

```python
from wallstrank import (
    HolderStatus,
    SecurityType,
    SortDir,
    MarketCap,
    FundSortBy,
    PortfolioSortBy,
    FundHolderSortBy,
    StockTrendSortBy,
    NetPositionSortBy,
    NetTradeSortBy,
    ChartTimeframe,
)
```

You can also pass raw strings — both are accepted.

## Utilities

The SDK ships a handful of stateless helpers for common client-side chores.

### Ticker normalisation

```python
from wallstrank import normalize_ticker, parse_tickers, validate_ticker

normalize_ticker("  aapl ")            # "AAPL"
validate_ticker("BRK.B")               # "BRK.B" (raises ValueError on garbage)
parse_tickers("aapl, msft\ngoogl")    # ["AAPL", "MSFT", "GOOGL"]
```

### Quarter arithmetic

```python
from wallstrank import iter_quarters, prior_quarter

prior_quarter(2025, 1)               # (2024, 4)
list(iter_quarters(2025, 2, 4))      # [(2025, 2), (2025, 1), (2024, 4), (2024, 3)]
```

### Auto-pagination

Both list endpoints on the API return `has_more_pages`. `paginate` /
`apaginate` walk pages transparently and abort if a safety cap is exceeded.

```python
from wallstrank import WallstrankClient, paginate

with WallstrankClient(api_key="...") as client:
    for page in paginate(lambda p: client.funds.list_portfolios(page=p, page_size=100)):
        for portfolio in page.portfolios:
            ...
```

```python
from wallstrank import AsyncWallstrankClient, apaginate

async with AsyncWallstrankClient(api_key="...") as client:
    async for page in apaginate(lambda p: client.stocks.fund_holders("AAPL", page=p, page_size=50)):
        for holder in page.holders:
            ...
```

`paginate` / `apaginate` raise `PaginationLimitExceededError` if `max_pages`
(default `1000`) is hit while the server still reports more pages.

## Error handling

All non-2xx responses raise a subclass of `APIError`:

```python
from wallstrank import (
    WallstrankError,  # base
    APIError,  # any non-2xx
    BadRequestError,  # 400
    AuthenticationError,  # 401
    RequestFailedError,  # 402
    ForbiddenError,  # 403
    NotFoundError,  # 404
    ServerError,  # 5xx
)

try:
    client.stocks.fund_holders("NOPE")
except NotFoundError as exc:
    print(exc.status_code, exc.message)
```

Network / transport errors are wrapped in `WallstrankError` after retries are exhausted.

## Development

This project uses [uv](https://docs.astral.sh/uv/), [ruff](https://docs.astral.sh/ruff/), and
[ty](https://github.com/astral-sh/ty).

```bash
uv sync --all-groups        # install dependencies
uv run ruff format          # format
uv run ruff check           # lint
uv run ty check             # type check
uv run pytest               # run tests
```

## License

[MIT](./LICENSE)
