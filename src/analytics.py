from __future__ import annotations

from datetime import date

import pandas as pd


ANOMALY_METRICS = ["records", "total_amount_due", "camera_records"]


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


def build_hourly_issue_trend(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["issue_hour", "violations_count", "amount_due"])

    valid_dates = df[df["issue_date"].notna()].copy()
    if valid_dates.empty:
        return pd.DataFrame(columns=["issue_hour", "violations_count", "amount_due"])

    trend = (
        valid_dates.assign(issue_hour=valid_dates["issue_date"].dt.hour)
        .groupby("issue_hour", dropna=True)
        .agg(violations_count=("summons_number", "count"), amount_due=("amount_due", "sum"))
        .reset_index()
        .sort_values("issue_hour")
    )
    return trend


def build_agency_daily_trend(df: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["issue_day", "issuing_agency", "violations_count", "amount_due"])

    top_agencies = (
        df.groupby("issuing_agency", dropna=False)
        .size()
        .sort_values(ascending=False)
        .head(top_n)
        .index
        .tolist()
    )
    filtered = df[df["issuing_agency"].isin(top_agencies)].copy()
    if filtered.empty:
        return pd.DataFrame(columns=["issue_day", "issuing_agency", "violations_count", "amount_due"])

    trend = (
        filtered.assign(issue_day=filtered["issue_date"].dt.date)
        .groupby(["issue_day", "issuing_agency"], dropna=False)
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


def detect_daily_metric_anomalies(
    run_metrics_df: pd.DataFrame,
    z_threshold: float = 3.0,
    pct_change_threshold: float = 50.0,
    window: int = 14,
    min_history: int = 7,
) -> pd.DataFrame:
    columns = [
        "report_date",
        "metric",
        "value",
        "baseline_mean",
        "baseline_std",
        "z_score",
        "pct_change",
        "severity",
        "reason",
    ]
    if run_metrics_df.empty:
        return pd.DataFrame(columns=columns)

    metrics = run_metrics_df.copy()
    if "report_date" not in metrics.columns:
        return pd.DataFrame(columns=columns)

    metrics["report_date"] = pd.to_datetime(metrics["report_date"], errors="coerce")
    metrics = metrics.dropna(subset=["report_date"]).sort_values("report_date").reset_index(drop=True)
    if metrics.empty:
        return pd.DataFrame(columns=columns)

    anomaly_rows: list[dict[str, object]] = []
    for metric in ANOMALY_METRICS:
        if metric not in metrics.columns:
            continue

        values = pd.to_numeric(metrics[metric], errors="coerce").fillna(0.0)
        baseline_mean = values.shift(1).rolling(window=window, min_periods=min_history).mean()
        baseline_std = values.shift(1).rolling(window=window, min_periods=min_history).std(ddof=0)
        pct_change = ((values - baseline_mean) / baseline_mean.replace(0, pd.NA) * 100.0).fillna(0.0)

        std_nonzero = baseline_std.where(baseline_std > 0)
        z_score = ((values - baseline_mean) / std_nonzero).fillna(0.0)

        for idx in range(len(metrics)):
            if pd.isna(baseline_mean.iloc[idx]):
                continue

            is_z_anomaly = abs(float(z_score.iloc[idx])) >= z_threshold
            is_pct_anomaly = abs(float(pct_change.iloc[idx])) >= pct_change_threshold
            if not (is_z_anomaly or is_pct_anomaly):
                continue

            severity = "HIGH" if (abs(float(z_score.iloc[idx])) >= z_threshold * 1.5 or abs(float(pct_change.iloc[idx])) >= pct_change_threshold * 1.5) else "MEDIUM"
            reason = (
                f"{metric} moved to {float(values.iloc[idx]):,.2f} "
                f"(baseline={float(baseline_mean.iloc[idx]):,.2f}, z={float(z_score.iloc[idx]):.2f}, "
                f"pct_change={float(pct_change.iloc[idx]):.2f}%)."
            )
            anomaly_rows.append(
                {
                    "report_date": metrics.iloc[idx]["report_date"].date().isoformat(),
                    "metric": metric,
                    "value": float(values.iloc[idx]),
                    "baseline_mean": float(baseline_mean.iloc[idx]),
                    "baseline_std": float(baseline_std.iloc[idx]) if not pd.isna(baseline_std.iloc[idx]) else 0.0,
                    "z_score": float(z_score.iloc[idx]),
                    "pct_change": float(pct_change.iloc[idx]),
                    "severity": severity,
                    "reason": reason,
                }
            )

    if not anomaly_rows:
        return pd.DataFrame(columns=columns)

    return pd.DataFrame(anomaly_rows).sort_values(["report_date", "severity", "metric"], ascending=[True, False, True]).reset_index(drop=True)


