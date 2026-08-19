"""Ticker string normalisation and validation helpers.

The Wall St. Rank API keys equity endpoints on uppercase symbols (for example
``/v1/stocks/AAPL/fund-stats``).  These helpers make it easy to canonicalise
user input before it is passed to the client and to raise a clear error when
input is obviously malformed.

Example::

    from wallstrank.tickers import normalize_ticker, validate_ticker, parse_tickers

    normalize_ticker("  aapl ")            # -> "AAPL"
    validate_ticker("BRK.B")               # -> "BRK.B"
    parse_tickers("aapl, msft\\ngoogl")    # -> ["AAPL", "MSFT", "GOOGL"]
"""

from __future__ import annotations

import re

__all__ = [
    "TICKER_PATTERN",
    "normalize_ticker",
    "parse_tickers",
    "validate_ticker",
]


TICKER_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9._-]{0,19}$")
"""Regex matched by :func:`validate_ticker`.

The pattern accepts 1-20 characters starting with a letter/digit and allowing
``. _ -`` in trailing positions.  It matches the surface area of tickers
returned by the Wall St. Rank API (e.g. ``AAPL``, ``BRK.B``, ``RDS-A``).
"""


def normalize_ticker(value: object) -> str:
    """Return a canonical uppercase ticker.

    Non-string values collapse to ``""``.  The result is *not* validated; use
    :func:`validate_ticker` when a malformed value should raise.
    """

    return value.strip().upper() if isinstance(value, str) else ""


def validate_ticker(value: object) -> str:
    """Return a canonical ticker or raise :class:`ValueError`.

    The value is first normalised (stripped + uppercased) and then matched
    against :data:`TICKER_PATTERN`.
    """

    ticker = normalize_ticker(value)
    if not TICKER_PATTERN.fullmatch(ticker):
        raise ValueError(f"Invalid ticker: {ticker!r}")
    return ticker


def parse_tickers(raw: str) -> list[str]:
    """Parse a comma/newline separated string into a deduplicated ticker list.

    Malformed entries are silently dropped.  Order is preserved from the input
    (first occurrence wins).
    """

    result: list[str] = []
    seen: set[str] = set()
    for value in raw.replace("\n", ",").split(","):
        ticker = normalize_ticker(value)
        if ticker and TICKER_PATTERN.fullmatch(ticker) and ticker not in seen:
            seen.add(ticker)
            result.append(ticker)
    return result
