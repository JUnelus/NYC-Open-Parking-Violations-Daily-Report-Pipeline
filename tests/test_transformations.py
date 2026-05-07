from __future__ import annotations

import pandas as pd

from src.report import build_top_counties, build_top_violation_types, calculate_kpis, compare_snapshots
from src.transform import transform_violations



def test_transformations_deduplicate_and_cast_numeric(transformed_df) -> None:
    assert len(transformed_df) == 5
    assert transformed_df["fine_amount"].dtype.kind in {"f", "i"}
    assert transformed_df.loc[transformed_df["summons_number"] == "1000000004"].shape[0] == 1
    assert transformed_df["is_camera_violation"].sum() == 3



def test_report_aggregations(transformed_df) -> None:
    kpis = calculate_kpis(transformed_df)
    top_violations = build_top_violation_types(transformed_df)
    top_counties = build_top_counties(transformed_df)

    assert kpis["total_records_pulled"] == 5
    assert kpis["total_camera_violations"] == 3
    assert round(kpis["total_open_amount_due"], 2) == 420.0
    assert top_violations.iloc[0]["Violation Type"] in set(transformed_df["violation"])
    assert len(top_counties) <= 5



def test_compare_snapshots_identifies_new_and_resolved_records(transformed_df) -> None:
    previous_df = transformed_df[transformed_df["summons_number"] != "1000000005"].copy()
    previous_df = previous_df[previous_df["summons_number"] != "1000000001"].copy()
    previous_df = pd.concat(
        [
            previous_df,
            pd.DataFrame(
                [
                    {
                        "summons_number": "9999999999",
                        "issue_date": pd.Timestamp("2026-05-03"),
                        "violation": "EXPIRED METER",
                        "fine_amount": 35.0,
                        "penalty_amount": 0.0,
                        "interest_amount": 0.0,
                        "payment_amount": 0.0,
                        "amount_due": 35.0,
                        "county": "NY",
                        "issuing_agency": "NYPD",
                        "is_camera_violation": False,
                        "report_date": pd.Timestamp("2026-05-05"),
                    }
                ]
            ),
        ],
        ignore_index=True,
    )

    diff_summary, changes = compare_snapshots(transformed_df, previous_df)

    assert diff_summary["new_records_pulled"] == 2
    assert diff_summary["resolved_or_missing_since_yesterday"] == 1
    assert "Count Change" in changes.columns



def test_transform_adds_missing_required_columns() -> None:
    df = pd.DataFrame([
        {"summons_number": "1", "issue_date": "2026-05-05", "violation": "DOUBLE PARKING"}
    ])
    transformed = transform_violations(df)
    assert "amount_due" in transformed.columns
    assert transformed.iloc[0]["amount_due"] == 0.0


