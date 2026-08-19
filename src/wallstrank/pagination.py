"""Auto-pagination helpers for Wall St. Rank list endpoints.

Every list endpoint on the Wall St. Rank API returns an object exposing a
``has_more_pages: bool`` field alongside a resource-named items list
(``portfolios``, ``holdings``, ``stocks``, ``holders``, ...).  These helpers
loop over pages until ``has_more_pages`` is ``False`` — with a hard cap to
avoid runaway iteration.

Example (sync)::

    from wallstrank import WallstrankClient
    from wallstrank.pagination import paginate

    with WallstrankClient(api_key="...") as client:
        for page in paginate(lambda p: client.funds.list_portfolios(page=p, page_size=100)):
            for portfolio in page.portfolios:
                ...

Example (async)::

    from wallstrank import AsyncWallstrankClient
    from wallstrank.pagination import apaginate

    async with AsyncWallstrankClient(api_key="...") as client:
        async for page in apaginate(
            lambda p: client.funds.list_portfolios(page=p, page_size=100)
        ):
            for portfolio in page.portfolios:
                ...
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Callable, Iterator
from typing import Protocol, runtime_checkable

__all__ = [
    "DEFAULT_MAX_PAGES",
    "HasMorePages",
    "PaginationLimitExceededError",
    "apaginate",
    "paginate",
]


DEFAULT_MAX_PAGES = 1000
"""Safety cap enforced by :func:`paginate` and :func:`apaginate` by default."""


@runtime_checkable
class HasMorePages(Protocol):
    """Structural protocol satisfied by every paginated Wall St. Rank response."""

    has_more_pages: bool


class PaginationLimitExceededError(RuntimeError):
    """Raised when :func:`paginate` / :func:`apaginate` reach ``max_pages``.

    The API returned ``has_more_pages=True`` on the final allowed page, which
    typically means the caller should either narrow the query or raise the cap.
    """


def paginate[PageT: HasMorePages](
    fetch_page: Callable[[int], PageT],
    *,
    start_page: int = 1,
    max_pages: int = DEFAULT_MAX_PAGES,
) -> Iterator[PageT]:
    """Iterate synchronous pages until the API reports ``has_more_pages=False``.

    ``fetch_page`` receives a 1-indexed page number and returns any object
    exposing ``has_more_pages: bool`` (every Wall St. Rank list response
    qualifies).  Raises :class:`PaginationLimitExceededError` if ``max_pages``
    is exhausted while the server still reports more data.
    """

    if start_page < 1:
        raise ValueError(f"start_page must be >= 1, got {start_page}")
    if max_pages < 1:
        raise ValueError(f"max_pages must be >= 1, got {max_pages}")
    for offset in range(max_pages):
        page_number = start_page + offset
        page = fetch_page(page_number)
        yield page
        if not page.has_more_pages:
            return
    raise PaginationLimitExceededError(
        f"Exceeded max_pages={max_pages} starting from page {start_page}"
    )


async def apaginate[PageT: HasMorePages](
    fetch_page: Callable[[int], Awaitable[PageT]],
    *,
    start_page: int = 1,
    max_pages: int = DEFAULT_MAX_PAGES,
) -> AsyncIterator[PageT]:
    """Async counterpart to :func:`paginate`.

    ``fetch_page`` must be an awaitable factory returning a paginated response.
    """

    if start_page < 1:
        raise ValueError(f"start_page must be >= 1, got {start_page}")
    if max_pages < 1:
        raise ValueError(f"max_pages must be >= 1, got {max_pages}")
    for offset in range(max_pages):
        page_number = start_page + offset
        page = await fetch_page(page_number)
        yield page
        if not page.has_more_pages:
            return
    raise PaginationLimitExceededError(
        f"Exceeded max_pages={max_pages} starting from page {start_page}"
    )
