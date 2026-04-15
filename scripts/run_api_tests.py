#!/usr/bin/env python3
"""
HTTP integration tests for the weather MCP server and agent backend.

Prerequisites (for full run):
  - MCP server on port 8000 (needs OPENWEATHER_API_KEY in .env)
  - Agent backend on port 8001 (needs GEMINI_API_KEY for /chat)

Examples (PowerShell; use `;` not `&&`):
  cd C:\\Users\\moham\\weather-agent-app
  python scripts/run_api_tests.py
  python scripts/run_api_tests.py --skip-chat
  python scripts/run_api_tests.py --mcp-url http://127.0.0.1:8000
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

try:
    import httpx
except ImportError:
    print("Install httpx: pip install httpx", file=sys.stderr)
    sys.exit(2)


@dataclass
class TestCase:
    id: str
    method: str
    url: str
    expected_status: int
    params: Optional[dict[str, Any]] = None
    json_body: Optional[dict[str, Any]] = None
    assert_keys: tuple[str, ...] = ()
    assert_fn: Optional[Callable[[httpx.Response], None]] = None


def _assert_json_keys(data: Any, keys: tuple[str, ...], case_id: str) -> None:
    if not isinstance(data, dict):
        raise AssertionError(f"{case_id}: expected JSON object, got {type(data).__name__}")
    missing = [k for k in keys if k not in data]
    if missing:
        raise AssertionError(f"{case_id}: missing keys {missing} in {list(data.keys())}")


def _mcp_cases(base: str) -> list[TestCase]:
    return [
        TestCase(
            id="mcp_health",
            method="GET",
            url=f"{base}/health",
            expected_status=200,
            assert_keys=("status", "service"),
        ),
        TestCase(
            id="mcp_current_london",
            method="GET",
            url=f"{base}/weather/current",
            params={"city": "London"},
            expected_status=200,
            assert_keys=("city", "temperature_celsius", "description"),
        ),
        TestCase(
            id="mcp_current_tokyo",
            method="GET",
            url=f"{base}/weather/current",
            params={"city": "Tokyo"},
            expected_status=200,
            assert_keys=("city", "country", "humidity_percent"),
        ),
        TestCase(
            id="mcp_current_new_york",
            method="GET",
            url=f"{base}/weather/current",
            params={"city": "New York,US"},
            expected_status=200,
            assert_keys=("city", "wind_speed_kmh"),
        ),
        TestCase(
            id="mcp_forecast_berlin",
            method="GET",
            url=f"{base}/weather/forecast",
            params={"city": "Berlin"},
            expected_status=200,
            assert_keys=("city", "forecast"),
        ),
        TestCase(
            id="mcp_air_quality_delhi",
            method="GET",
            url=f"{base}/weather/air-quality",
            params={"city": "Delhi"},
            expected_status=200,
            assert_keys=("city", "aqi", "aqi_label"),
        ),
        TestCase(
            id="mcp_current_missing_city_422",
            method="GET",
            url=f"{base}/weather/current",
            params=None,
            expected_status=422,
        ),
    ]


def _agent_cases(base: str) -> list[TestCase]:
    messages = [
        "What is the weather in Austin right now?",
        "Give me a 3-day outlook for Paris.",
        "How is air quality in Beijing today?",
        "Temperature in Cairo, please.",
        "Will it rain in Seattle this week?",
    ]

    cases: list[TestCase] = [
        TestCase(
            id="agent_health",
            method="GET",
            url=f"{base}/health",
            expected_status=200,
            assert_keys=("status", "service"),
        ),
        TestCase(
            id="agent_chat_empty_message_422",
            method="POST",
            url=f"{base}/chat",
            json_body={},
            expected_status=422,
        ),
    ]

    for i, msg in enumerate(messages):
        case_id = f"agent_chat_case_{i}"

        def _make_chat_assert(cid: str, user_msg: str) -> Callable[[httpx.Response], None]:
            def _check(r: httpx.Response) -> None:
                data = r.json()
                _assert_json_keys(data, ("response",), cid)
                text = data.get("response") or ""
                if not isinstance(text, str) or not text.strip():
                    raise AssertionError(f"{cid}: empty response for input: {user_msg[:60]!r}")

            return _check

        cases.append(
            TestCase(
                id=case_id,
                method="POST",
                url=f"{base}/chat",
                json_body={"message": msg},
                expected_status=200,
                assert_fn=_make_chat_assert(case_id, msg),
            )
        )

    return cases


def run_one(client: httpx.Client, tc: TestCase) -> None:
    kwargs: dict[str, Any] = {"method": tc.method, "url": tc.url, "timeout": 120.0}
    if tc.params is not None:
        kwargs["params"] = tc.params
    if tc.json_body is not None:
        kwargs["json"] = tc.json_body

    r = client.request(**kwargs)
    if r.status_code != tc.expected_status:
        body = r.text[:500]
        raise AssertionError(
            f"{tc.id}: expected status {tc.expected_status}, got {r.status_code}. Body: {body}"
        )

    if tc.expected_status >= 400:
        return

    try:
        data = r.json()
    except json.JSONDecodeError as e:
        raise AssertionError(f"{tc.id}: invalid JSON: {e}") from e

    if tc.assert_keys:
        _assert_json_keys(data, tc.assert_keys, tc.id)

    if tc.assert_fn is not None:
        tc.assert_fn(r)


def main() -> int:
    p = argparse.ArgumentParser(description="Run API integration tests against local services.")
    p.add_argument(
        "--mcp-url",
        default=os.environ.get("MCP_SERVER_URL", "http://127.0.0.1:8000"),
        help="MCP server base URL (default: env MCP_SERVER_URL or http://127.0.0.1:8000)",
    )
    p.add_argument(
        "--agent-url",
        default=os.environ.get("AGENT_BACKEND_URL", "http://127.0.0.1:8001"),
        help="Agent backend base URL (default: env AGENT_BACKEND_URL or http://127.0.0.1:8001)",
    )
    p.add_argument(
        "--skip-chat",
        action="store_true",
        help="Skip agent /chat tests (health + 422 only for agent)",
    )
    p.add_argument(
        "--mcp-only",
        action="store_true",
        help="Only run MCP server tests",
    )
    args = p.parse_args()

    mcp_base = args.mcp_url.rstrip("/")
    agent_base = args.agent_url.rstrip("/")

    cases = _mcp_cases(mcp_base)
    if not args.mcp_only:
        agent_part = _agent_cases(agent_base)
        if args.skip_chat:
            cases.extend([c for c in agent_part if c.id.startswith("agent_health") or "422" in c.id])
        else:
            cases.extend(agent_part)

    passed = 0
    failed: list[tuple[str, str]] = []

    with httpx.Client() as client:
        for tc in cases:
            try:
                run_one(client, tc)
                print(f"OK  {tc.id}")
                passed += 1
            except AssertionError as e:
                print(f"FAIL {tc.id}: {e}", file=sys.stderr)
                failed.append((tc.id, str(e)))
            except httpx.RequestError as e:
                print(f"FAIL {tc.id}: connection error: {e}", file=sys.stderr)
                failed.append((tc.id, str(e)))

    print(f"\n{passed}/{len(cases)} passed")
    if failed:
        print("Failures:", file=sys.stderr)
        for fid, msg in failed:
            print(f"  - {fid}: {msg}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
