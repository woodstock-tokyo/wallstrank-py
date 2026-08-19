"""Fund chart-bar endpoints under ``/v1/funds/:fund_or_mgr_id/chart-bars/*``."""

from __future__ import annotations

from pydantic import TypeAdapter

from .._http import AsyncBaseHTTPClient, BaseHTTPClient, encode_path_segment
from ..enums import ChartTimeframe
from ..models import ChartBar, FundReturnBar, WallstrankModel

__all__ = [
    "AsyncFundChartBarsResource",
    "AumChartResponse",
    "FundChartBarsResource",
    "ReturnChartResponse",
]

_AUM_BARS_ADAPTER = TypeAdapter(list[ChartBar])
_RETURN_BARS_ADAPTER = TypeAdapter(list[FundReturnBar])


class AumChartResponse(WallstrankModel):
    """Response body for ``/v1/funds/:fund_or_mgr_id/chart-bars/aum``."""

    bars: list[ChartBar]


class ReturnChartResponse(WallstrankModel):
    """Response body for the various return chart-bar endpoints.

    Each field maps a :class:`ChartTimeframe` to a list of :class:`FundReturnBar`.
    """

    bars_by_timeframe: dict[ChartTimeframe, list[FundReturnBar]]

    def timeframe(self, timeframe: ChartTimeframe | str) -> list[FundReturnBar]:
        """Convenience accessor for a specific timeframe."""

        key = ChartTimeframe(timeframe) if isinstance(timeframe, str) else timeframe
        return self.bars_by_timeframe.get(key, [])


def _parse_return_chart(payload: object) -> ReturnChartResponse:
    if not isinstance(payload, dict):
        raise TypeError(f"Expected dict payload, got {type(payload).__name__}")
    bars_by_timeframe: dict[ChartTimeframe, list[FundReturnBar]] = {}
    for raw_key, raw_value in payload.items():
        try:
            key = ChartTimeframe(raw_key)
        except ValueError:
            # Skip unrecognised timeframes so we stay forward-compatible.
            continue
        bars_by_timeframe[key] = _RETURN_BARS_ADAPTER.validate_python(raw_value)
    return ReturnChartResponse(bars_by_timeframe=bars_by_timeframe)


def _parse_aum(payload: object) -> AumChartResponse:
    if isinstance(payload, dict) and "bars" in payload:
        bars = _AUM_BARS_ADAPTER.validate_python(payload["bars"])
    else:
        bars = _AUM_BARS_ADAPTER.validate_python(payload)
    return AumChartResponse(bars=bars)


_FUND_CHART_BARS_ENDPOINTS = {
    "aum": "aum",
    "return_": "return",
    "top_20_return": "top-20-return",
    "top_15_return": "top-15-return",
    "top_10_return": "top-10-return",
    "post_disclosure_return": "post-disclosure-return",
    "top_20_post_disclosure_return": "top-20-post-disclosure-return",
    "top_15_post_disclosure_return": "top-15-post-disclosure-return",
    "top_10_post_disclosure_return": "top-10-post-disclosure-return",
}


def _endpoint_path(fund_or_mgr_id: str, endpoint: str) -> str:
    return f"/v1/funds/{encode_path_segment(fund_or_mgr_id)}/chart-bars/{endpoint}"


class FundChartBarsResource:
    """Synchronous fund chart-bar endpoints."""

    def __init__(self, client: BaseHTTPClient) -> None:
        self._client = client

    def aum(self, fund_or_mgr_id: str) -> AumChartResponse:
        """Historical AUM chart bars for a fund or fund manager."""

        payload = self._client.get(
            _endpoint_path(fund_or_mgr_id, _FUND_CHART_BARS_ENDPOINTS["aum"])
        )
        return _parse_aum(payload)

    def _fetch_return(self, fund_or_mgr_id: str, endpoint: str) -> ReturnChartResponse:
        payload = self._client.get(_endpoint_path(fund_or_mgr_id, endpoint))
        return _parse_return_chart(payload)

    def return_(self, fund_or_mgr_id: str) -> ReturnChartResponse:
        """Historical returns for the full disclosed portfolio."""

        return self._fetch_return(fund_or_mgr_id, _FUND_CHART_BARS_ENDPOINTS["return_"])

    def top_20_return(self, fund_or_mgr_id: str) -> ReturnChartResponse:
        return self._fetch_return(fund_or_mgr_id, _FUND_CHART_BARS_ENDPOINTS["top_20_return"])

    def top_15_return(self, fund_or_mgr_id: str) -> ReturnChartResponse:
        return self._fetch_return(fund_or_mgr_id, _FUND_CHART_BARS_ENDPOINTS["top_15_return"])

    def top_10_return(self, fund_or_mgr_id: str) -> ReturnChartResponse:
        return self._fetch_return(fund_or_mgr_id, _FUND_CHART_BARS_ENDPOINTS["top_10_return"])

    def post_disclosure_return(self, fund_or_mgr_id: str) -> ReturnChartResponse:
        return self._fetch_return(
            fund_or_mgr_id, _FUND_CHART_BARS_ENDPOINTS["post_disclosure_return"]
        )

    def top_20_post_disclosure_return(self, fund_or_mgr_id: str) -> ReturnChartResponse:
        return self._fetch_return(
            fund_or_mgr_id, _FUND_CHART_BARS_ENDPOINTS["top_20_post_disclosure_return"]
        )

    def top_15_post_disclosure_return(self, fund_or_mgr_id: str) -> ReturnChartResponse:
        return self._fetch_return(
            fund_or_mgr_id, _FUND_CHART_BARS_ENDPOINTS["top_15_post_disclosure_return"]
        )

    def top_10_post_disclosure_return(self, fund_or_mgr_id: str) -> ReturnChartResponse:
        return self._fetch_return(
            fund_or_mgr_id, _FUND_CHART_BARS_ENDPOINTS["top_10_post_disclosure_return"]
        )


class AsyncFundChartBarsResource:
    """Asynchronous fund chart-bar endpoints."""

    def __init__(self, client: AsyncBaseHTTPClient) -> None:
        self._client = client

    async def aum(self, fund_or_mgr_id: str) -> AumChartResponse:
        payload = await self._client.get(
            _endpoint_path(fund_or_mgr_id, _FUND_CHART_BARS_ENDPOINTS["aum"])
        )
        return _parse_aum(payload)

    async def _fetch_return(self, fund_or_mgr_id: str, endpoint: str) -> ReturnChartResponse:
        payload = await self._client.get(_endpoint_path(fund_or_mgr_id, endpoint))
        return _parse_return_chart(payload)

    async def return_(self, fund_or_mgr_id: str) -> ReturnChartResponse:
        return await self._fetch_return(fund_or_mgr_id, _FUND_CHART_BARS_ENDPOINTS["return_"])

    async def top_20_return(self, fund_or_mgr_id: str) -> ReturnChartResponse:
        return await self._fetch_return(fund_or_mgr_id, _FUND_CHART_BARS_ENDPOINTS["top_20_return"])

    async def top_15_return(self, fund_or_mgr_id: str) -> ReturnChartResponse:
        return await self._fetch_return(fund_or_mgr_id, _FUND_CHART_BARS_ENDPOINTS["top_15_return"])

    async def top_10_return(self, fund_or_mgr_id: str) -> ReturnChartResponse:
        return await self._fetch_return(fund_or_mgr_id, _FUND_CHART_BARS_ENDPOINTS["top_10_return"])

    async def post_disclosure_return(self, fund_or_mgr_id: str) -> ReturnChartResponse:
        return await self._fetch_return(
            fund_or_mgr_id, _FUND_CHART_BARS_ENDPOINTS["post_disclosure_return"]
        )

    async def top_20_post_disclosure_return(self, fund_or_mgr_id: str) -> ReturnChartResponse:
        return await self._fetch_return(
            fund_or_mgr_id, _FUND_CHART_BARS_ENDPOINTS["top_20_post_disclosure_return"]
        )

    async def top_15_post_disclosure_return(self, fund_or_mgr_id: str) -> ReturnChartResponse:
        return await self._fetch_return(
            fund_or_mgr_id, _FUND_CHART_BARS_ENDPOINTS["top_15_post_disclosure_return"]
        )

    async def top_10_post_disclosure_return(self, fund_or_mgr_id: str) -> ReturnChartResponse:
        return await self._fetch_return(
            fund_or_mgr_id, _FUND_CHART_BARS_ENDPOINTS["top_10_post_disclosure_return"]
        )
