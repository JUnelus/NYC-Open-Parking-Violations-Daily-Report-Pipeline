from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import requests

try:
    from .config import AppConfig, CAMERA_VIOLATIONS
except ImportError:  # pragma: no cover
    from config import AppConfig, CAMERA_VIOLATIONS



def build_query_params(limit: int, camera_only: bool = False, open_only: bool = False) -> dict[str, Any]:
    params: dict[str, Any] = {
        "$limit": limit,
        "$order": "issue_date DESC",
    }

    where_clauses: list[str] = []
    if open_only:
        where_clauses.append("amount_due > 0")
    if camera_only:
        camera_list = ",".join(f"'{violation}'" for violation in sorted(CAMERA_VIOLATIONS))
        where_clauses.append(f"violation in({camera_list})")
    if where_clauses:
        params["$where"] = " AND ".join(where_clauses)

    return params



def paginate_records(
    config: AppConfig,
    camera_only: bool = False,
    open_only: bool = False,
    session: requests.Session | None = None,
) -> list[dict[str, Any]]:
    """Fetch all records across all pages, handling API pagination."""
    all_records: list[dict[str, Any]] = []
    active_session = session or requests.Session()
    offset = 0
    batch_size = config.limit
    headers = {"X-App-Token": config.app_token} if config.app_token else {}

    while True:
        params = build_query_params(batch_size, camera_only=camera_only, open_only=open_only)
        params["$offset"] = offset

        response = active_session.get(
            config.soda2_endpoint,
            params=params,
            headers=headers,
            timeout=config.timeout,
        )
        response.raise_for_status()
        payload = response.json()

        if not isinstance(payload, list):
            raise ValueError("Expected the SODA API to return a list of records.")

        if not payload:
            break

        all_records.extend(payload)
        if len(payload) < batch_size:
            break

        offset += batch_size

    return all_records


def fetch_records(
    config: AppConfig,
    limit: int | None = None,
    camera_only: bool = False,
    open_only: bool = False,
    session: requests.Session | None = None,
) -> list[dict[str, Any]]:
    query_limit = limit or config.limit
    headers = {"X-App-Token": config.app_token} if config.app_token else {}
    active_session = session or requests.Session()

    response = active_session.get(
        config.soda2_endpoint,
        params=build_query_params(query_limit, camera_only=camera_only, open_only=open_only),
        headers=headers,
        timeout=config.timeout,
    )
    response.raise_for_status()
    payload = response.json()

    if not isinstance(payload, list):
        raise ValueError("Expected the SODA API to return a list of records.")

    return payload



def load_records_from_file(file_path: str | Path) -> list[dict[str, Any]]:
    path = Path(file_path)
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if not isinstance(payload, list):
        raise ValueError(f"Expected a list of records in {path}.")

    return payload



def records_to_dataframe(records: list[dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame.from_records(records)



def save_raw_payload(records: list[dict[str, Any]], output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(records, handle, indent=2)


