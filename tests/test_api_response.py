from __future__ import annotations

from src.extract import build_query_params, records_to_dataframe


REQUIRED_COLUMNS = {
    "summons_number",
    "issue_date",
    "violation",
    "fine_amount",
    "penalty_amount",
    "interest_amount",
    "payment_amount",
    "amount_due",
    "county",
    "issuing_agency",
}


def test_sample_payload_contains_required_columns(sample_records: list[dict]) -> None:
    df = records_to_dataframe(sample_records)
    assert REQUIRED_COLUMNS.issubset(set(df.columns))



def test_build_query_params_for_open_camera_request() -> None:
    params = build_query_params(limit=1000, camera_only=True, open_only=True)
    assert params["$limit"] == 1000
    assert params["$order"] == "issue_date DESC"
    assert "amount_due > 0" in params["$where"]
    assert "violation in(" in params["$where"]


