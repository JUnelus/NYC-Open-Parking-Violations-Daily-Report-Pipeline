from __future__ import annotations

from datetime import date

from src.analytics import (
    build_agency_daily_trend,
    build_daily_issue_trend,
    build_daily_run_metrics,
    build_hourly_issue_trend,
    build_monthly_trend,
    build_rolling_daily_metrics,
    build_violation_time_series,
    build_weekday_trend,
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

