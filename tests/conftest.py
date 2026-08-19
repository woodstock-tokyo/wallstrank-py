"""Shared fixtures and helpers for the wallstrank-py test suite."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator, Iterator
from pathlib import Path
from typing import Any

import httpx
import pytest
import respx

from wallstrank import AsyncWallstrankClient, WallstrankClient

TEST_BASE_URL = "https://api.test.wallstrank.com"
TEST_API_KEY = "test-api-key"

_FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> dict[str, Any]:
    """Load a JSON fixture from ``tests/fixtures/<name>.json``.

    ``name`` may include forward-slash subdirectories,
    e.g. ``load_fixture("stocks/fund-holders")``.
    """
    return json.loads((_FIXTURES_DIR / f"{name}.json").read_text())


@pytest.fixture
def api_mock() -> Iterator[respx.MockRouter]:
    """Provide a respx router mounted on the test base URL."""

    with respx.mock(base_url=TEST_BASE_URL, assert_all_called=False) as router:
        yield router


@pytest.fixture
def client() -> Iterator[WallstrankClient]:
    with WallstrankClient(
        api_key=TEST_API_KEY,
        base_url=TEST_BASE_URL,
        max_retries=0,
        http_client=httpx.Client(),
    ) as instance:
        yield instance


@pytest.fixture
async def async_client() -> AsyncIterator[AsyncWallstrankClient]:
    async with AsyncWallstrankClient(
        api_key=TEST_API_KEY,
        base_url=TEST_BASE_URL,
        max_retries=0,
        http_client=httpx.AsyncClient(),
    ) as instance:
        yield instance
