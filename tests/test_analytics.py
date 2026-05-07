from __future__ import annotations

from datetime import date

import pandas as pd

from src.analytics import (
    build_agency_daily_trend,
    build_daily_issue_trend,
    build_daily_run_metrics,
    build_hourly_issue_trend,
    build_monthly_trend,
    build_rolling_daily_metrics,
    build_violation_time_series,
    build_weekday_trend,
    detect_daily_metric_anomalies,
)


def test_granular_time_series_outputs(transformed_df) -> None:
    daily = build_daily_issue_trend(transformed_df)
    weekday = build_weekday_trend(transformed_df)
    monthly = build_monthly_trend(transformed_df)
    hourly = build_hourly_issue_trend(transformed_df)
    rolling = build_rolling_daily_metrics(transformed_df)
    violation_series = build_violation_time_series(transformed_df, top_n=3)
    agency_series = build_agency_daily_trend(transformed_df, top_n=3)
    run_metrics = build_daily_run_metrics(transformed_df, date(2026, 5, 6))

    assert not daily.empty
    assert set(["issue_day", "violations_count", "amount_due", "payments"]).issubset(daily.columns)
    assert not weekday.empty
    assert set(["weekday", "violations_count", "amount_due"]).issubset(weekday.columns)
    assert not monthly.empty
    assert set(["issue_month", "violations_count", "amount_due"]).issubset(monthly.columns)
    assert set(["issue_hour", "violations_count", "amount_due"]).issubset(hourly.columns)
    assert not rolling.empty
    assert "rolling_7d_count" in rolling.columns
    assert not violation_series.empty
    assert set(["issue_day", "violation", "violations_count", "amount_due"]).issubset(violation_series.columns)
    assert set(["issue_day", "issuing_agency", "violations_count", "amount_due"]).issubset(agency_series.columns)
    assert run_metrics.iloc[0]["report_date"] == "2026-05-06"


def test_detect_daily_metric_anomalies_flags_outlier_run() -> None:
    history = pd.DataFrame(
        [
            {"report_date": f"2026-05-{day:02d}", "records": 1000, "total_amount_due": 10000.0, "camera_records": 300}
            for day in range(1, 13)
        ]
        + [{"report_date": "2026-05-13", "records": 2200, "total_amount_due": 26000.0, "camera_records": 900}]
    )

    anomalies = detect_daily_metric_anomalies(history, z_threshold=2.0, pct_change_threshold=40.0, window=10, min_history=5)

    assert not anomalies.empty
    latest = anomalies[anomalies["report_date"] == "2026-05-13"]
    assert not latest.empty
    assert set(latest["metric"].tolist()).intersection({"records", "total_amount_due", "camera_records"})


