from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import pandas as pd
import requests



def evaluate_significant_changes(
    summary_df: pd.DataFrame,
    pct_change_threshold: float,
    absolute_count_threshold: int,
    amount_pct_change_threshold: float,
    absolute_amount_threshold: float,
) -> list[dict[str, Any]]:
    alerts: list[dict[str, Any]] = []
    if summary_df.empty:
        return alerts

    row = summary_df.iloc[0]
    previous_count = float(row.get("previous_record_count", 0) or 0)
    net_change = float(row.get("net_record_change", 0) or 0)
    current_count = float(row.get("total_records_pulled", 0) or 0)
    previous_amount_due = float(row.get("previous_open_amount_due", 0.0) or 0.0)
    amount_due_change = float(row.get("open_amount_due_change", 0.0) or 0.0)
    current_amount_due = float(row.get("total_open_amount_due", 0.0) or 0.0)

    if previous_count > 0:
        pct_change = (net_change / previous_count) * 100.0
    else:
        pct_change = 100.0 if current_count > 0 else 0.0

    if abs(pct_change) >= pct_change_threshold:
        alerts.append(
            {
                "type": "record_count_pct_change",
                "severity": "HIGH" if abs(pct_change) >= max(2 * pct_change_threshold, 75.0) else "MEDIUM",
                "message": (
                    f"Record count changed by {pct_change:.2f}% "
                    f"(previous={int(previous_count):,}, current={int(current_count):,})."
                ),
            }
        )

    if abs(net_change) >= absolute_count_threshold:
        alerts.append(
            {
                "type": "record_count_absolute_change",
                "severity": "HIGH",
                "message": (
                    f"Absolute net record change is {int(net_change):,}, "
                    f"which exceeds threshold {absolute_count_threshold:,}."
                ),
            }
        )

    if previous_amount_due > 0:
        amount_pct_change = (amount_due_change / previous_amount_due) * 100.0
    else:
        amount_pct_change = 100.0 if current_amount_due > 0 else 0.0

    if abs(amount_pct_change) >= amount_pct_change_threshold:
        alerts.append(
            {
                "type": "amount_due_pct_change",
                "severity": "HIGH" if abs(amount_pct_change) >= max(2 * amount_pct_change_threshold, 50.0) else "MEDIUM",
                "message": (
                    f"Open amount due changed by {amount_pct_change:.2f}% "
                    f"(previous=${previous_amount_due:,.2f}, current=${current_amount_due:,.2f})."
                ),
            }
        )

    if abs(amount_due_change) >= absolute_amount_threshold:
        alerts.append(
            {
                "type": "amount_due_absolute_change",
                "severity": "HIGH",
                "message": (
                    f"Absolute open amount due change is ${amount_due_change:,.2f}, "
                    f"which exceeds threshold ${absolute_amount_threshold:,.2f}."
                ),
            }
        )

    return alerts



def build_alert_log_rows(alerts: list[dict[str, Any]], report_date: str) -> pd.DataFrame:
    if not alerts:
        return pd.DataFrame(columns=["timestamp_utc", "report_date", "type", "severity", "message"])

    timestamp = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    rows = [
        {
            "timestamp_utc": timestamp,
            "report_date": report_date,
            "type": alert["type"],
            "severity": alert["severity"],
            "message": alert["message"],
        }
        for alert in alerts
    ]
    return pd.DataFrame(rows)



def send_webhook_alerts(webhook_url: str, alerts: list[dict[str, Any]], report_date: str, timeout: int = 15) -> None:
    if not webhook_url or not alerts:
        return

    payload = {
        "text": (
            f"NYC parking violations alerts for {report_date}:\n"
            + "\n".join(f"- [{alert['severity']}] {alert['message']}" for alert in alerts)
        )
    }
    response = requests.post(webhook_url, json=payload, timeout=timeout)
    response.raise_for_status()


