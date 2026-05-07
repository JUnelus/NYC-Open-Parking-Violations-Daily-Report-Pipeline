from __future__ import annotations

import pandas as pd

from src.alerts import build_alert_log_rows, evaluate_significant_changes


def test_alerts_trigger_on_large_change() -> None:
    summary_df = pd.DataFrame(
        [
            {
                "report_date": "2026-05-06",
                "total_records_pulled": 2000,
                "previous_record_count": 1000,
                "net_record_change": 1000,
                "total_open_amount_due": 900000,
                "previous_open_amount_due": 400000,
                "open_amount_due_change": 500000,
            }
        ]
    )

    alerts = evaluate_significant_changes(
        summary_df,
        pct_change_threshold=20.0,
        absolute_count_threshold=500,
        amount_pct_change_threshold=25.0,
        absolute_amount_threshold=250000.0,
    )
    assert len(alerts) >= 4

    log_df = build_alert_log_rows(alerts, "2026-05-06")
    assert not log_df.empty
    assert {"timestamp_utc", "report_date", "type", "severity", "message"}.issubset(log_df.columns)


def test_alerts_no_trigger_when_small_change() -> None:
    summary_df = pd.DataFrame(
        [
            {
                "report_date": "2026-05-06",
                "total_records_pulled": 1010,
                "previous_record_count": 1000,
                "net_record_change": 10,
                "total_open_amount_due": 1000500,
                "previous_open_amount_due": 1000000,
                "open_amount_due_change": 500,
            }
        ]
    )

    alerts = evaluate_significant_changes(
        summary_df,
        pct_change_threshold=50.0,
        absolute_count_threshold=5000,
        amount_pct_change_threshold=35.0,
        absolute_amount_threshold=250000.0,
    )
    assert alerts == []


