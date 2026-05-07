from __future__ import annotations

from datetime import date

import pandas as pd


def build_daily_issue_trend(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["issue_day", "violations_count", "amount_due", "payments"])

    trend = (
        df.assign(issue_day=df["issue_date"].dt.date)
        .groupby("issue_day", dropna=True)
        .agg(
            violations_count=("summons_number", "count"),
            amount_due=("amount_due", "sum"),
            payments=("payment_amount", "sum"),
        )
        .reset_index()
        .sort_values("issue_day")
    )
    return trend


def build_weekday_trend(df: pd.DataFrame) -> pd.DataFrame:
    columns = ["weekday", "violations_count", "amount_due"]
    if df.empty:
        return pd.DataFrame(columns=columns)

    valid_dates = df[df["issue_date"].notna()].copy()
    if valid_dates.empty:
        return pd.DataFrame(columns=columns)

    valid_dates["weekday"] = valid_dates["issue_date"].dt.day_name()
    trend = (
        valid_dates.groupby("weekday", dropna=False)
        .agg(violations_count=("summons_number", "count"), amount_due=("amount_due", "sum"))
        .reset_index()
    )

    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    trend["weekday"] = pd.Categorical(trend["weekday"], categories=order, ordered=True)
    trend = trend.sort_values("weekday").reset_index(drop=True)
    trend["weekday"] = trend["weekday"].astype(str)
    return trend


def build_monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["issue_month", "violations_count", "amount_due"])

    valid_dates = df[df["issue_date"].notna()].copy()
    if valid_dates.empty:
        return pd.DataFrame(columns=["issue_month", "violations_count", "amount_due"])

    trend = (
        valid_dates.assign(issue_month=valid_dates["issue_date"].dt.to_period("M").astype(str))
        .groupby("issue_month", dropna=False)
        .agg(violations_count=("summons_number", "count"), amount_due=("amount_due", "sum"))
        .reset_index()
        .sort_values("issue_month")
    )
    return trend


def build_rolling_daily_metrics(df: pd.DataFrame) -> pd.DataFrame:
    trend = build_daily_issue_trend(df)
    if trend.empty:
        return pd.DataFrame(columns=["issue_day", "violations_count", "amount_due", "payments", "rolling_7d_count", "rolling_7d_amount_due"])

    trend = trend.copy()
    trend["rolling_7d_count"] = trend["violations_count"].rolling(window=7, min_periods=1).mean()
    trend["rolling_7d_amount_due"] = trend["amount_due"].rolling(window=7, min_periods=1).mean()
    return trend


def build_violation_time_series(df: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["issue_day", "violation", "violations_count", "amount_due"])

    top_violations = (
        df.groupby("violation", dropna=False)
        .size()
        .sort_values(ascending=False)
        .head(top_n)
        .index
        .tolist()
    )

    filtered = df[df["violation"].isin(top_violations)].copy()
    if filtered.empty:
        return pd.DataFrame(columns=["issue_day", "violation", "violations_count", "amount_due"])

    trend = (
        filtered.assign(issue_day=filtered["issue_date"].dt.date)
        .groupby(["issue_day", "violation"], dropna=False)
        .agg(violations_count=("summons_number", "count"), amount_due=("amount_due", "sum"))
        .reset_index()
        .sort_values(["issue_day", "violations_count"], ascending=[True, False])
    )
    return trend


def build_daily_run_metrics(current_df: pd.DataFrame, report_date: date) -> pd.DataFrame:
    row = {
        "report_date": report_date.isoformat(),
        "records": int(len(current_df)),
        "total_amount_due": float(current_df["amount_due"].sum()) if "amount_due" in current_df.columns else 0.0,
        "camera_records": int(current_df["is_camera_violation"].sum()) if "is_camera_violation" in current_df.columns else 0,
    }
    return pd.DataFrame([row])

