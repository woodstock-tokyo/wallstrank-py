"""Tests for the low-level HTTP helpers and error mapping."""

from __future__ import annotations

import httpx
import pytest
import respx

from conftest import TEST_API_KEY, TEST_BASE_URL
from wallstrank import (
    APIError,
    AsyncWallstrankClient,
    AuthenticationError,
    BadRequestError,
    ForbiddenError,
    NotFoundError,
    ServerError,
    WallstrankClient,
    WallstrankError,
)
from wallstrank._http import (
    AsyncBaseHTTPClient,
    BaseHTTPClient,
    _extract_error_message,
    encode_params,
)


def test_encode_params_drops_none_and_stringifies():
    encoded = encode_params(
        {
            "year": 2025,
            "quarter": None,
            "include_ongoing": True,
            "page_size": 100,
            "empty": "",
        }
    )
    assert encoded == {"year": "2025", "include_ongoing": "true", "page_size": "100"}


def test_encode_params_joins_iterables():
    encoded = encode_params({"status": ["new", "increased"]})
    assert encoded == {"status": "new,increased"}


def test_encode_params_handles_enum_values():
    from wallstrank import SortDir

    encoded = encode_params({"sort_dir": SortDir.DESC})
    assert encoded == {"sort_dir": "desc"}


def test_missing_api_key_raises():
    with pytest.raises(WallstrankError):
        WallstrankClient(api_key="")


def test_authorization_header_and_user_agent(
    client: WallstrankClient, api_mock: respx.MockRouter
) -> None:
    route = api_mock.get("/v1/sectors").mock(return_value=httpx.Response(200, json={"sectors": []}))
    client.reference.list_sectors()
    request = route.calls.last.request
    assert request.headers["Authorization"] == f"Bearer {TEST_API_KEY}"
    assert request.headers["User-Agent"].startswith("wallstrank-py/")


@pytest.mark.parametrize(
    ("status", "exc_type"),
    [
        (400, BadRequestError),
        (401, AuthenticationError),
        (403, ForbiddenError),
        (404, NotFoundError),
        (500, ServerError),
        (502, ServerError),
        (418, APIError),
    ],
)
def test_error_mapping(
    client: WallstrankClient,
    api_mock: respx.MockRouter,
    status: int,
    exc_type: type[APIError],
) -> None:
    api_mock.get("/v1/sectors").mock(return_value=httpx.Response(status, json={"message": "boom"}))
    with pytest.raises(exc_type) as excinfo:
        client.reference.list_sectors()
    assert excinfo.value.status_code == status
    assert "boom" in str(excinfo.value)


def test_base_url_is_stripped_of_trailing_slash():
    c = WallstrankClient(api_key=TEST_API_KEY, base_url=f"{TEST_BASE_URL}/")
    assert c.base_url == TEST_BASE_URL
    c.close()


def test_encode_params_skips_none_inside_iterable():
    encoded = encode_params({"status": ["new", None, "closed"]})
    assert encoded == {"status": "new,closed"}


def test_encode_params_skips_iterable_of_only_nones():
    encoded = encode_params({"status": [None, None]})
    assert encoded == {}


def test_extract_error_message_variants():
    assert _extract_error_message({"message": "boom"}) == "boom"
    assert _extract_error_message({"error": "inline"}) == "inline"
    assert _extract_error_message({"detail": "detail msg"}) == "detail msg"
    # Nested ``error`` object with ``message`` key.
    assert _extract_error_message({"error": {"message": "nested"}}) == "nested"
    # Plain string body.
    assert _extract_error_message("plain string") == "plain string"
    # Empty string yields None.
    assert _extract_error_message("") is None
    # Unknown shapes yield None.
    assert _extract_error_message({"unrelated": 1}) is None
    assert _extract_error_message([1, 2, 3]) is None
    assert _extract_error_message(None) is None


def test_error_response_without_message_uses_reason_phrase(
    client: WallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/sectors").mock(return_value=httpx.Response(500, text="", headers={}))
    with pytest.raises(ServerError) as excinfo:
        client.reference.list_sectors()
    # Should fall back to a non-empty message even when body is empty.
    assert str(excinfo.value)


def test_retryable_status_eventually_succeeds(api_mock: respx.MockRouter) -> None:
    call_counter = {"n": 0}

    def responder(request: httpx.Request) -> httpx.Response:
        call_counter["n"] += 1
        if call_counter["n"] < 3:
            return httpx.Response(503, json={"message": "unavailable"})
        return httpx.Response(200, json={"sectors": []})

    api_mock.get("/v1/sectors").mock(side_effect=responder)
    with WallstrankClient(
        api_key=TEST_API_KEY,
        base_url=TEST_BASE_URL,
        max_retries=3,
        retry_backoff=0.0,
        http_client=httpx.Client(),
    ) as c:
        sectors = c.reference.list_sectors()
    assert sectors == []
    assert call_counter["n"] == 3


def test_retryable_status_exhausts_and_returns_last(api_mock: respx.MockRouter) -> None:
    api_mock.get("/v1/sectors").mock(
        return_value=httpx.Response(503, json={"message": "still down"})
    )
    with (
        WallstrankClient(
            api_key=TEST_API_KEY,
            base_url=TEST_BASE_URL,
            max_retries=2,
            retry_backoff=0.0,
            http_client=httpx.Client(),
        ) as c,
        pytest.raises(ServerError),
    ):
        c.reference.list_sectors()


def test_transport_error_retries_then_succeeds(api_mock: respx.MockRouter) -> None:
    call_counter = {"n": 0}

    def responder(request: httpx.Request) -> httpx.Response:
        call_counter["n"] += 1
        if call_counter["n"] < 2:
            raise httpx.ConnectError("boom")
        return httpx.Response(200, json={"sectors": []})

    api_mock.get("/v1/sectors").mock(side_effect=responder)
    with WallstrankClient(
        api_key=TEST_API_KEY,
        base_url=TEST_BASE_URL,
        max_retries=3,
        retry_backoff=0.0,
        http_client=httpx.Client(),
    ) as c:
        sectors = c.reference.list_sectors()
    assert sectors == []
    assert call_counter["n"] == 2


def test_transport_error_exhausts_and_raises(api_mock: respx.MockRouter) -> None:
    api_mock.get("/v1/sectors").mock(side_effect=httpx.ConnectError("no route"))
    with (
        WallstrankClient(
            api_key=TEST_API_KEY,
            base_url=TEST_BASE_URL,
            max_retries=2,
            retry_backoff=0.0,
            http_client=httpx.Client(),
        ) as c,
        pytest.raises(WallstrankError) as excinfo,
    ):
        c.reference.list_sectors()
    assert "Network error" in str(excinfo.value)


def test_client_context_manager_closes_owned_client() -> None:
    with WallstrankClient(api_key=TEST_API_KEY, base_url=TEST_BASE_URL) as c:
        assert c.base_url == TEST_BASE_URL


def test_base_http_client_context_manager_closes_owned() -> None:
    with BaseHTTPClient(api_key=TEST_API_KEY, base_url=TEST_BASE_URL, max_retries=0) as http:
        assert http.base_url == TEST_BASE_URL


def test_build_url_prepends_leading_slash() -> None:
    with BaseHTTPClient(api_key=TEST_API_KEY, base_url=TEST_BASE_URL, max_retries=0) as http:
        assert http._build_url("v1/sectors") == f"{TEST_BASE_URL}/v1/sectors"


def test_non_json_error_body_falls_back_to_text(
    client: WallstrankClient, api_mock: respx.MockRouter
) -> None:
    api_mock.get("/v1/sectors").mock(
        return_value=httpx.Response(
            500,
            content=b"not json at all",
            headers={"content-type": "text/plain"},
        )
    )
    with pytest.raises(ServerError) as excinfo:
        client.reference.list_sectors()
    assert "not json at all" in str(excinfo.value)


async def test_async_client_base_url_and_close() -> None:
    async with AsyncWallstrankClient(api_key=TEST_API_KEY, base_url=TEST_BASE_URL) as c:
        assert c.base_url == TEST_BASE_URL


async def test_async_base_http_client_context_manager_closes_owned() -> None:
    async with AsyncBaseHTTPClient(
        api_key=TEST_API_KEY, base_url=TEST_BASE_URL, max_retries=0
    ) as http:
        assert http.base_url == TEST_BASE_URL


async def test_async_missing_api_key_raises() -> None:
    with pytest.raises(WallstrankError):
        AsyncWallstrankClient(api_key="")


async def test_async_retryable_status_eventually_succeeds(
    api_mock: respx.MockRouter,
) -> None:
    call_counter = {"n": 0}

    def responder(request: httpx.Request) -> httpx.Response:
        call_counter["n"] += 1
        if call_counter["n"] < 2:
            return httpx.Response(429, json={"message": "slow down"})
        return httpx.Response(200, json={"sectors": []})

    api_mock.get("/v1/sectors").mock(side_effect=responder)
    async with AsyncWallstrankClient(
        api_key=TEST_API_KEY,
        base_url=TEST_BASE_URL,
        max_retries=3,
        retry_backoff=0.0,
        http_client=httpx.AsyncClient(),
    ) as c:
        sectors = await c.reference.list_sectors()
    assert sectors == []
    assert call_counter["n"] == 2


async def test_async_retryable_status_exhausts_and_raises(
    api_mock: respx.MockRouter,
) -> None:
    api_mock.get("/v1/sectors").mock(
        return_value=httpx.Response(502, json={"message": "still down"})
    )
    async with AsyncWallstrankClient(
        api_key=TEST_API_KEY,
        base_url=TEST_BASE_URL,
        max_retries=1,
        retry_backoff=0.0,
        http_client=httpx.AsyncClient(),
    ) as c:
        with pytest.raises(ServerError):
            await c.reference.list_sectors()


async def test_async_transport_error_retries_then_succeeds(
    api_mock: respx.MockRouter,
) -> None:
    call_counter = {"n": 0}

    def responder(request: httpx.Request) -> httpx.Response:
        call_counter["n"] += 1
        if call_counter["n"] < 2:
            raise httpx.ConnectError("boom")
        return httpx.Response(200, json={"sectors": []})

    api_mock.get("/v1/sectors").mock(side_effect=responder)
    async with AsyncWallstrankClient(
        api_key=TEST_API_KEY,
        base_url=TEST_BASE_URL,
        max_retries=3,
        retry_backoff=0.0,
        http_client=httpx.AsyncClient(),
    ) as c:
        sectors = await c.reference.list_sectors()
    assert sectors == []
    assert call_counter["n"] == 2


async def test_async_transport_error_exhausts_and_raises(
    api_mock: respx.MockRouter,
) -> None:
    api_mock.get("/v1/sectors").mock(side_effect=httpx.ConnectError("no route"))
    async with AsyncWallstrankClient(
        api_key=TEST_API_KEY,
        base_url=TEST_BASE_URL,
        max_retries=1,
        retry_backoff=0.0,
        http_client=httpx.AsyncClient(),
    ) as c:
        with pytest.raises(WallstrankError):
            await c.reference.list_sectors()
