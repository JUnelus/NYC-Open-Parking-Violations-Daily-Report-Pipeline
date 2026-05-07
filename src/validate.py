from __future__ import annotations

from typing import Any

import pandas as pd
from pandas.api.types import is_numeric_dtype

try:
    from .transform import NUMERIC_COLUMNS, REQUIRED_COLUMNS
except ImportError:  # pragma: no cover
    from transform import NUMERIC_COLUMNS, REQUIRED_COLUMNS



def _check(name: str, passed: bool, details: str) -> dict[str, Any]:
    return {"check": name, "result": "PASS" if passed else "FAIL", "details": details}



def run_data_quality_checks(df: pd.DataFrame) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []

    checks.append(
        _check(
            "API returned data",
            not df.empty,
            f"Rows available: {len(df):,}",
        )
    )

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    checks.append(
        _check(
            "Required columns present",
            not missing_columns,
            "All required columns are present." if not missing_columns else f"Missing columns: {missing_columns}",
        )
    )

    numeric_failures = [column for column in NUMERIC_COLUMNS if column in df.columns and not is_numeric_dtype(df[column])]
    checks.append(
        _check(
            "Numeric fields converted successfully",
            not numeric_failures,
            "Numeric columns are typed correctly." if not numeric_failures else f"Non-numeric columns: {numeric_failures}",
        )
    )

    negative_amount_due_count = 0
    if "amount_due" in df.columns:
        negative_amount_due_count = int((df["amount_due"] < 0).sum())
    checks.append(
        _check(
            "No negative amount_due values",
            negative_amount_due_count == 0,
            f"Negative amount_due rows: {negative_amount_due_count}",
        )
    )

    unparsed_issue_date_count = 0
    if "issue_date" in df.columns:
        unparsed_issue_date_count = int(df["issue_date"].isna().sum())
    checks.append(
        _check(
            "issue_date parsed successfully",
            unparsed_issue_date_count == 0,
            f"Rows with invalid issue_date: {unparsed_issue_date_count}",
        )
    )

    missing_summons_count = 0
    if "summons_number" in df.columns:
        missing_summons_count = int(df["summons_number"].isna().sum())
    checks.append(
        _check(
            "summons_number not null",
            missing_summons_count == 0,
            f"Rows with null summons_number: {missing_summons_count}",
        )
    )

    return checks



def all_checks_passed(checks: list[dict[str, Any]]) -> bool:
    return all(check["result"] == "PASS" for check in checks)


