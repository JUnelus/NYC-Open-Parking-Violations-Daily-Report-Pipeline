from __future__ import annotations

from datetime import date

import pandas as pd

try:
    from .config import CAMERA_VIOLATIONS
except ImportError:  # pragma: no cover
    from config import CAMERA_VIOLATIONS

REQUIRED_COLUMNS = [
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
]

NUMERIC_COLUMNS = [
    "fine_amount",
    "penalty_amount",
    "interest_amount",
    "payment_amount",
    "amount_due",
]

TEXT_COLUMNS = [
    "violation",
    "county",
    "issuing_agency",
]



def transform_violations(df: pd.DataFrame, report_date: date | None = None) -> pd.DataFrame:
    cleaned = df.copy()

    for column in REQUIRED_COLUMNS:
        if column not in cleaned.columns:
            cleaned[column] = pd.NA

    cleaned = cleaned[REQUIRED_COLUMNS].copy()

    cleaned["summons_number"] = cleaned["summons_number"].astype("string").str.strip()
    cleaned.loc[cleaned["summons_number"] == "", "summons_number"] = pd.NA

    for column in TEXT_COLUMNS:
        cleaned[column] = cleaned[column].astype("string").str.strip()
        cleaned.loc[cleaned[column].isna() | (cleaned[column] == ""), column] = "Unknown"

    for column in NUMERIC_COLUMNS:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce").fillna(0.0)

    cleaned["issue_date"] = pd.to_datetime(cleaned["issue_date"], format="mixed", errors="coerce")
    cleaned["is_camera_violation"] = cleaned["violation"].isin(CAMERA_VIOLATIONS)
    cleaned["report_date"] = pd.Timestamp(report_date or date.today())

    cleaned = cleaned.drop_duplicates(subset=["summons_number"], keep="first")
    cleaned = cleaned.sort_values(
        by=["issue_date", "summons_number"],
        ascending=[False, True],
        na_position="last",
    ).reset_index(drop=True)

    return cleaned


