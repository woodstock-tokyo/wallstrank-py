"""Tests for :mod:`wallstrank.tickers`."""

from __future__ import annotations

import pytest

from wallstrank.tickers import (
    TICKER_PATTERN,
    normalize_ticker,
    parse_tickers,
    validate_ticker,
)


class TestNormalizeTicker:
    def test_strips_and_uppercases(self) -> None:
        assert normalize_ticker("  aapl  ") == "AAPL"

    def test_preserves_dot_and_dash(self) -> None:
        assert normalize_ticker("brk.b") == "BRK.B"
        assert normalize_ticker("rds-a") == "RDS-A"

    @pytest.mark.parametrize("value", [None, 123, 12.5, [], {}, object()])
    def test_non_string_becomes_empty(self, value: object) -> None:
        assert normalize_ticker(value) == ""


class TestValidateTicker:
    @pytest.mark.parametrize("value", ["aapl", "AAPL", " msft ", "brk.b", "rds-a", "9988"])
    def test_valid_inputs(self, value: str) -> None:
        assert validate_ticker(value) == value.strip().upper()

    @pytest.mark.parametrize(
        "value",
        [
            "",
            " ",
            "-BAD",
            ".BAD",
            "TOOLONGTICKER1234567890",
            "AA BB",
            "AA/BB",
            None,
            42,
        ],
    )
    def test_invalid_inputs_raise(self, value: object) -> None:
        with pytest.raises(ValueError, match="Invalid ticker"):
            validate_ticker(value)


class TestParseTickers:
    def test_splits_on_comma_and_newline(self) -> None:
        assert parse_tickers("aapl, msft\ngoogl") == ["AAPL", "MSFT", "GOOGL"]

    def test_deduplicates_preserving_first_occurrence(self) -> None:
        assert parse_tickers("aapl, AAPL, msft, aapl") == ["AAPL", "MSFT"]

    def test_drops_invalid(self) -> None:
        assert parse_tickers("aapl, ,-bad, msft") == ["AAPL", "MSFT"]

    def test_empty_input(self) -> None:
        assert parse_tickers("") == []


class TestPattern:
    def test_pattern_is_compiled(self) -> None:
        assert TICKER_PATTERN.fullmatch("AAPL")
        assert not TICKER_PATTERN.fullmatch("aapl")
