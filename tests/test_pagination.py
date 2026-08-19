"""Tests for :mod:`wallstrank.pagination`."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from wallstrank.pagination import (
    HasMorePages,
    PaginationLimitExceededError,
    apaginate,
    paginate,
)


@dataclass
class FakePage:
    page: int
    has_more_pages: bool


def test_page_satisfies_protocol() -> None:
    page = FakePage(page=1, has_more_pages=False)
    assert isinstance(page, HasMorePages)


class TestPaginate:
    def test_iterates_until_has_more_pages_false(self) -> None:
        pages = [
            FakePage(page=1, has_more_pages=True),
            FakePage(page=2, has_more_pages=True),
            FakePage(page=3, has_more_pages=False),
        ]
        seen: list[int] = []

        def fetch(page_number: int) -> FakePage:
            seen.append(page_number)
            return pages[page_number - 1]

        result = list(paginate(fetch))
        assert result == pages
        assert seen == [1, 2, 3]

    def test_respects_start_page(self) -> None:
        seen: list[int] = []

        def fetch(page_number: int) -> FakePage:
            seen.append(page_number)
            return FakePage(page=page_number, has_more_pages=page_number < 5)

        list(paginate(fetch, start_page=3))
        assert seen == [3, 4, 5]

    def test_raises_when_max_pages_exceeded(self) -> None:
        def fetch(page_number: int) -> FakePage:
            return FakePage(page=page_number, has_more_pages=True)

        with pytest.raises(PaginationLimitExceededError, match="Exceeded max_pages=2"):
            list(paginate(fetch, max_pages=2))

    def test_single_page_response(self) -> None:
        def fetch(page_number: int) -> FakePage:
            return FakePage(page=page_number, has_more_pages=False)

        assert len(list(paginate(fetch))) == 1

    @pytest.mark.parametrize(("kwarg", "value"), [("start_page", 0), ("max_pages", 0)])
    def test_invalid_bounds_raise(self, kwarg: str, value: int) -> None:
        def fetch(page_number: int) -> FakePage:
            return FakePage(page=page_number, has_more_pages=False)

        with pytest.raises(ValueError):
            list(paginate(fetch, **{kwarg: value}))


class TestApaginate:
    async def test_iterates_until_has_more_pages_false(self) -> None:
        pages = [
            FakePage(page=1, has_more_pages=True),
            FakePage(page=2, has_more_pages=False),
        ]

        async def fetch(page_number: int) -> FakePage:
            return pages[page_number - 1]

        result = [page async for page in apaginate(fetch)]
        assert result == pages

    async def test_raises_when_max_pages_exceeded(self) -> None:
        async def fetch(page_number: int) -> FakePage:
            return FakePage(page=page_number, has_more_pages=True)

        with pytest.raises(PaginationLimitExceededError):
            [page async for page in apaginate(fetch, max_pages=1)]

    @pytest.mark.parametrize(("kwarg", "value"), [("start_page", 0), ("max_pages", 0)])
    async def test_invalid_bounds_raise(self, kwarg: str, value: int) -> None:
        async def fetch(page_number: int) -> FakePage:
            return FakePage(page=page_number, has_more_pages=False)

        with pytest.raises(ValueError):
            [page async for page in apaginate(fetch, **{kwarg: value})]
