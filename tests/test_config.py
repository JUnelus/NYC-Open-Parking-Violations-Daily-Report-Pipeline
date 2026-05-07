from __future__ import annotations

from src.config import _get_float, _get_int


def test_blank_numeric_env_uses_default(monkeypatch) -> None:
    monkeypatch.setenv("NYC311_ALERT_PCT_CHANGE_THRESHOLD", "")
    monkeypatch.setenv("NYC311_API_LIMIT", "")

    assert _get_float("NYC311_ALERT_PCT_CHANGE_THRESHOLD", 50.0) == 50.0
    assert _get_int("NYC311_API_LIMIT", 50000) == 50000

