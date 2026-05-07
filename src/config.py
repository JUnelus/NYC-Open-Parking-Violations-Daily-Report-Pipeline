from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
HISTORY_DIR = PROCESSED_DIR / "history"
ANALYTICS_DIR = DATA_DIR / "analytics"
REPORTS_DIR = REPO_ROOT / "reports"
CHARTS_DIR = REPORTS_DIR / "charts"

DEFAULT_SODA2_ENDPOINT = "https://data.cityofnewyork.us/resource/nc67-uf89.json"
DEFAULT_SODA3_ENDPOINT = "https://data.cityofnewyork.us/api/v3/views/nc67-uf89/query.json"
DEFAULT_LIMIT = 50_000
DEFAULT_TIMEOUT = 60
DEFAULT_ALERT_PCT_CHANGE_THRESHOLD = 50.0
DEFAULT_ALERT_ABSOLUTE_COUNT_THRESHOLD = 5_000
DEFAULT_ALERT_AMOUNT_PCT_CHANGE_THRESHOLD = 35.0
DEFAULT_ALERT_ABSOLUTE_AMOUNT_THRESHOLD = 250_000.0

CAMERA_VIOLATIONS = {
    "PHTO SCHOOL ZN SPEED VIOLATION",
    "FAILURE TO STOP AT RED LIGHT",
    "BUS LANE VIOLATION",
}


@dataclass(frozen=True)
class AppConfig:
    app_token: str | None
    secret_token: str | None
    soda2_endpoint: str
    soda3_endpoint: str
    limit: int
    timeout: int
    data_dir: Path = DATA_DIR
    raw_dir: Path = RAW_DIR
    processed_dir: Path = PROCESSED_DIR
    history_dir: Path = HISTORY_DIR
    analytics_dir: Path = ANALYTICS_DIR
    reports_dir: Path = REPORTS_DIR
    charts_dir: Path = CHARTS_DIR
    alerts_enabled: bool = False
    alert_webhook_url: str | None = None
    alert_pct_change_threshold: float = DEFAULT_ALERT_PCT_CHANGE_THRESHOLD
    alert_absolute_count_threshold: int = DEFAULT_ALERT_ABSOLUTE_COUNT_THRESHOLD
    alert_amount_pct_change_threshold: float = DEFAULT_ALERT_AMOUNT_PCT_CHANGE_THRESHOLD
    alert_absolute_amount_threshold: float = DEFAULT_ALERT_ABSOLUTE_AMOUNT_THRESHOLD



def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    try:
        return int(value.strip())
    except ValueError as exc:
        raise ValueError(f"Environment variable {name} must be an integer.") from exc


def _get_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    try:
        return float(value.strip())
    except ValueError as exc:
        raise ValueError(f"Environment variable {name} must be a float.") from exc


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}



def load_config() -> AppConfig:
    load_dotenv(REPO_ROOT / ".env")

    return AppConfig(
        app_token=os.getenv("NYC311_APP_TOKEN") or os.getenv("NYC_OPEN_DATA_APP_TOKEN"),
        secret_token=os.getenv("NYC311_SECRET_TOKEN") or os.getenv("NYC_OPEN_DATA_SECRET_TOKEN"),
        soda2_endpoint=os.getenv("NYC311_SODA2_ENDPOINT", DEFAULT_SODA2_ENDPOINT),
        soda3_endpoint=os.getenv("NYC311_SODA3_ENDPOINT", DEFAULT_SODA3_ENDPOINT),
        limit=_get_int("NYC311_API_LIMIT", DEFAULT_LIMIT),
        timeout=_get_int("NYC311_API_TIMEOUT", DEFAULT_TIMEOUT),
        alerts_enabled=_get_bool("NYC311_ALERTS_ENABLED", False),
        alert_webhook_url=os.getenv("NYC311_ALERT_WEBHOOK_URL"),
        alert_pct_change_threshold=_get_float(
            "NYC311_ALERT_PCT_CHANGE_THRESHOLD",
            DEFAULT_ALERT_PCT_CHANGE_THRESHOLD,
        ),
        alert_absolute_count_threshold=_get_int(
            "NYC311_ALERT_ABSOLUTE_COUNT_THRESHOLD",
            DEFAULT_ALERT_ABSOLUTE_COUNT_THRESHOLD,
        ),
        alert_amount_pct_change_threshold=_get_float(
            "NYC311_ALERT_AMOUNT_PCT_CHANGE_THRESHOLD",
            DEFAULT_ALERT_AMOUNT_PCT_CHANGE_THRESHOLD,
        ),
        alert_absolute_amount_threshold=_get_float(
            "NYC311_ALERT_ABSOLUTE_AMOUNT_THRESHOLD",
            DEFAULT_ALERT_ABSOLUTE_AMOUNT_THRESHOLD,
        ),
    )


