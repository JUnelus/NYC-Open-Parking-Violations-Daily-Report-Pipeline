from __future__ import annotations

from typing import Any

import pandas as pd



def format_currency(value: float) -> str:
    return f"${value:,.2f}"



def build_top_violation_types(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["Rank", "Violation Type", "Count", "Amount Due"])

    summary = (
        df.groupby("violation", dropna=False)
        .agg(Count=("summons_number", "count"), Amount_Due=("amount_due", "sum"))
        .sort_values(["Count", "Amount_Due"], ascending=[False, False])
        .head(top_n)
        .reset_index()
    )
    summary.insert(0, "Rank", range(1, len(summary) + 1))
    summary = summary.rename(columns={"violation": "Violation Type", "Amount_Due": "Amount Due"})
    return summary



def build_top_counties(df: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["Rank", "County", "Count", "Amount Due"])

    summary = (
        df.groupby("county", dropna=False)
        .agg(Count=("summons_number", "count"), Amount_Due=("amount_due", "sum"))
        .sort_values(["Amount_Due", "Count"], ascending=[False, False])
        .head(top_n)
        .reset_index()
    )
    summary.insert(0, "Rank", range(1, len(summary) + 1))
    summary = summary.rename(columns={"county": "County", "Amount_Due": "Amount Due"})
    return summary



def calculate_kpis(df: pd.DataFrame) -> dict[str, Any]:
    total_records = len(df)
    total_camera = int(df["is_camera_violation"].sum()) if "is_camera_violation" in df.columns else 0

    return {
        "total_records_pulled": total_records,
        "total_open_amount_due": float(df["amount_due"].sum()) if "amount_due" in df.columns else 0.0,
        "total_fine_amount": float(df["fine_amount"].sum()) if "fine_amount" in df.columns else 0.0,
        "total_penalty_amount": float(df["penalty_amount"].sum()) if "penalty_amount" in df.columns else 0.0,
        "total_interest_amount": float(df["interest_amount"].sum()) if "interest_amount" in df.columns else 0.0,
        "total_payment_amount": float(df["payment_amount"].sum()) if "payment_amount" in df.columns else 0.0,
        "total_camera_violations": total_camera,
        "total_non_camera_parking_violations": total_records - total_camera,
    }



def compare_snapshots(current_df: pd.DataFrame, previous_df: pd.DataFrame | None) -> tuple[dict[str, Any], pd.DataFrame]:
    if previous_df is None or previous_df.empty:
        diff_summary = {
            "new_records_pulled": int(len(current_df)),
            "resolved_or_missing_since_yesterday": 0,
            "net_record_change": int(len(current_df)),
            "previous_record_count": 0,
        }
        changes = (
            current_df.groupby("violation", dropna=False)
            .agg(current_count=("summons_number", "count"), current_amount_due=("amount_due", "sum"))
            .reset_index()
        )
        changes["previous_count"] = 0
        changes["previous_amount_due"] = 0.0
    else:
        current_keys = set(current_df["summons_number"].dropna().astype(str))
        previous_keys = set(previous_df["summons_number"].dropna().astype(str))
        diff_summary = {
            "new_records_pulled": len(current_keys - previous_keys),
            "resolved_or_missing_since_yesterday": len(previous_keys - current_keys),
            "net_record_change": len(current_df) - len(previous_df),
            "previous_record_count": len(previous_df),
        }

        current_grouped = (
            current_df.groupby("violation", dropna=False)
            .agg(current_count=("summons_number", "count"), current_amount_due=("amount_due", "sum"))
        )
        previous_grouped = (
            previous_df.groupby("violation", dropna=False)
            .agg(previous_count=("summons_number", "count"), previous_amount_due=("amount_due", "sum"))
        )
        changes = current_grouped.join(previous_grouped, how="outer").fillna(0).reset_index()

    changes["count_change"] = changes["current_count"] - changes["previous_count"]
    changes["amount_due_change"] = changes["current_amount_due"] - changes["previous_amount_due"]
    changes["abs_count_change"] = changes["count_change"].abs()
    changes = changes.sort_values(
        ["abs_count_change", "count_change", "amount_due_change"],
        ascending=[False, False, False],
    ).head(10)
    changes = changes.rename(
        columns={
            "violation": "Violation Type",
            "current_count": "Current Count",
            "previous_count": "Previous Count",
            "count_change": "Count Change",
            "current_amount_due": "Current Amount Due",
            "previous_amount_due": "Previous Amount Due",
            "amount_due_change": "Amount Due Change",
        }
    )
    changes = changes.drop(columns=["abs_count_change"])

    return diff_summary, changes.reset_index(drop=True)



def build_summary_dataframe(kpis: dict[str, Any], diff_summary: dict[str, Any], checks: list[dict[str, Any]], report_date: str) -> pd.DataFrame:
    summary = {
        "report_date": report_date,
        **kpis,
        **diff_summary,
        "checks_passed": sum(check["result"] == "PASS" for check in checks),
        "checks_failed": sum(check["result"] == "FAIL" for check in checks),
    }
    return pd.DataFrame([summary])


def build_borough_breakdown(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["County", "Count", "Amount Due"])

    summary = (
        df.groupby("county", dropna=False)
        .agg(Count=("summons_number", "count"), Amount_Due=("amount_due", "sum"))
        .sort_values(["Amount_Due", "Count"], ascending=[False, False])
        .head(top_n)
        .reset_index()
    )
    summary = summary.rename(columns={"county": "County", "Amount_Due": "Amount Due"})
    return summary.reset_index(drop=True)


def build_agency_breakdown(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["Issuing Agency", "Count", "Amount Due"])

    summary = (
        df.groupby("issuing_agency", dropna=False)
        .agg(Count=("summons_number", "count"), Amount_Due=("amount_due", "sum"))
        .sort_values(["Count", "Amount_Due"], ascending=[False, False])
        .head(top_n)
        .reset_index()
    )
    summary = summary.rename(columns={"issuing_agency": "Issuing Agency", "Amount_Due": "Amount Due"})
    return summary.reset_index(drop=True)



def _stringify(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:,.2f}"
    return str(value)



def dataframe_to_markdown(df: pd.DataFrame) -> str:
    if df.empty:
        return "_No data available._"

    columns = list(df.columns)
    widths = []
    for column in columns:
        values = [_stringify(value) for value in df[column].tolist()]
        widths.append(max(len(str(column)), *(len(value) for value in values)))

    header = "| " + " | ".join(str(column).ljust(width) for column, width in zip(columns, widths)) + " |"
    separator = "| " + " | ".join("-" * width for width in widths) + " |"
    rows = []
    for _, row in df.iterrows():
        rows.append(
            "| "
            + " | ".join(_stringify(row[column]).ljust(width) for column, width in zip(columns, widths))
            + " |"
        )
    return "\n".join([header, separator, *rows])



def render_markdown_report(
    report_date: str,
    kpis: dict[str, Any],
    diff_summary: dict[str, Any],
    top_violation_types: pd.DataFrame,
    top_counties: pd.DataFrame,
    day_over_day_changes: pd.DataFrame,
    quality_checks: list[dict[str, Any]],
    transformed_df: pd.DataFrame | None = None,
    daily_trend_df: pd.DataFrame | None = None,
    weekday_trend_df: pd.DataFrame | None = None,
    monthly_trend_df: pd.DataFrame | None = None,
    significant_alerts: list[dict[str, Any]] | None = None,
) -> str:
    checks_df = pd.DataFrame(quality_checks)

    qa_note = (
        "The dataset refreshed successfully. No major data quality issues were detected in today's pull."
        if (checks_df["result"] == "PASS").all()
        else "One or more data quality checks failed. Review the details table below before publishing downstream outputs."
    )

    markdown = f"""# NYC Open Parking & Camera Violations Daily Report

Report Date: {report_date}

## Dashboard & Charts

![Top Violations](./charts/top_violations.png)
![Top Counties](./charts/top_counties.png)
![Top Agencies](./charts/top_agencies.png)
![Camera vs Parking](./charts/camera_vs_parking.png)

## Executive Summary

- Total Records Pulled: {kpis['total_records_pulled']:,}
- New Records Pulled Since Yesterday: {diff_summary['new_records_pulled']:,}
- Open Amount Due: {format_currency(kpis['total_open_amount_due'])}
- Total Fine Amount: {format_currency(kpis['total_fine_amount'])}
- Total Penalties: {format_currency(kpis['total_penalty_amount'])}
- Total Interest: {format_currency(kpis['total_interest_amount'])}
- Total Payments Recorded: {format_currency(kpis['total_payment_amount'])}
- Total Camera Violations: {kpis['total_camera_violations']:,}
- Total Non-Camera Parking Violations: {kpis['total_non_camera_parking_violations']:,}
- Previous Snapshot Record Count: {diff_summary['previous_record_count']:,}
- Resolved or Missing Since Yesterday: {diff_summary['resolved_or_missing_since_yesterday']:,}
- Net Record Change: {diff_summary['net_record_change']:,}

## Top Violation Types

{dataframe_to_markdown(top_violation_types)}

## Top 5 Counties by Amount Due

{dataframe_to_markdown(top_counties)}

## Borough & County Breakdown

{dataframe_to_markdown(build_borough_breakdown(transformed_df)) if transformed_df is not None and not transformed_df.empty else "_No data available._"}

## Issuing Agency Analysis

{dataframe_to_markdown(build_agency_breakdown(transformed_df)) if transformed_df is not None and not transformed_df.empty else "_No data available._"}

## Granular Time-Series Analysis

### Daily Trend (Most Recent 14 Days)

{dataframe_to_markdown(daily_trend_df.tail(14)) if daily_trend_df is not None and not daily_trend_df.empty else "_No data available._"}

### Weekday Pattern

{dataframe_to_markdown(weekday_trend_df) if weekday_trend_df is not None and not weekday_trend_df.empty else "_No data available._"}

### Monthly Trend

{dataframe_to_markdown(monthly_trend_df) if monthly_trend_df is not None and not monthly_trend_df.empty else "_No data available._"}

## Biggest Day-over-Day Changes

{dataframe_to_markdown(day_over_day_changes)}

## Data Quality Checks

{dataframe_to_markdown(checks_df[["check", "result", "details"]].rename(columns={"check": "Check", "result": "Result", "details": "Details"}))}

## Significant Change Alerts

{"\n".join(f"- [{alert['severity']}] {alert['message']}" for alert in significant_alerts) if significant_alerts else "_No significant alerts triggered for this run._"}

## QA Notes

{qa_note}
"""
    return markdown

