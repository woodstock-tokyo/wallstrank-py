"""Reporting-period arithmetic for Wall St. Rank quarterly data.

The Wall St. Rank API models many endpoints (holdings, fund-stats, chart-bars,
fund-trends, ...) as quarterly snapshots keyed by ``(year, quarter)``.  These
helpers make it easy to step backwards through history without hand-rolling
edge cases at year boundaries.

Example::

    from wallstrank.periods import prior_quarter, iter_quarters

    prior_quarter(2025, 1)          # -> (2024, 4)
    list(iter_quarters(2025, 2, 4)) # -> [(2025, 2), (2025, 1), (2024, 4), (2024, 3)]
"""

from __future__ import annotations

from collections.abc import Iterator

__all__ = ["iter_quarters", "prior_quarter"]


def prior_quarter(year: int, quarter: int) -> tuple[int, int]:
    """Return the ``(year, quarter)`` immediately before ``(year, quarter)``.

    ``quarter`` must be in ``1..4``; otherwise :class:`ValueError` is raised.
    """

    if quarter not in range(1, 5):
        raise ValueError(f"quarter must be in 1..4, got {quarter}")
    return (year, quarter - 1) if quarter > 1 else (year - 1, 4)


def iter_quarters(year: int, quarter: int, count: int) -> Iterator[tuple[int, int]]:
    """Yield ``count`` ``(year, quarter)`` tuples counting backwards.

    The first tuple yielded is ``(year, quarter)`` itself.  ``count`` must be
    non-negative; ``count == 0`` yields nothing.
    """

    if quarter not in range(1, 5):
        raise ValueError(f"quarter must be in 1..4, got {quarter}")
    if count < 0:
        raise ValueError(f"count must be non-negative, got {count}")
    for _ in range(count):
        yield year, quarter
        year, quarter = prior_quarter(year, quarter)
