"""Tests for :mod:`wallstrank.periods`."""

from __future__ import annotations

import pytest

from wallstrank.periods import iter_quarters, prior_quarter


class TestPriorQuarter:
    @pytest.mark.parametrize(
        ("year", "quarter", "expected"),
        [
            (2025, 4, (2025, 3)),
            (2025, 3, (2025, 2)),
            (2025, 2, (2025, 1)),
            (2025, 1, (2024, 4)),
            (2000, 1, (1999, 4)),
        ],
    )
    def test_walks_backwards(self, year: int, quarter: int, expected: tuple[int, int]) -> None:
        assert prior_quarter(year, quarter) == expected

    @pytest.mark.parametrize("quarter", [0, 5, -1, 100])
    def test_invalid_quarter_raises(self, quarter: int) -> None:
        with pytest.raises(ValueError, match=r"quarter must be in 1\.\.4"):
            prior_quarter(2025, quarter)


class TestIterQuarters:
    def test_yields_requested_count(self) -> None:
        assert list(iter_quarters(2025, 2, 4)) == [
            (2025, 2),
            (2025, 1),
            (2024, 4),
            (2024, 3),
        ]

    def test_count_zero_yields_empty(self) -> None:
        assert list(iter_quarters(2025, 2, 0)) == []

    def test_negative_count_raises(self) -> None:
        with pytest.raises(ValueError, match="count must be non-negative"):
            list(iter_quarters(2025, 2, -1))

    def test_invalid_quarter_raises(self) -> None:
        with pytest.raises(ValueError, match=r"quarter must be in 1\.\.4"):
            list(iter_quarters(2025, 5, 4))

    def test_crosses_year_boundary(self) -> None:
        assert list(iter_quarters(2025, 1, 3)) == [(2025, 1), (2024, 4), (2024, 3)]
