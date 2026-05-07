from __future__ import annotations

import argparse
from datetime import date, datetime
from pathlib import Path

import pandas as pd

try:
    from .config import AppConfig, load_config
    from .extract import fetch_records, paginate_records, load_records_from_file, records_to_dataframe, save_raw_payload
    from .charts import generate_all_charts
    from .analytics import (
        build_agency_daily_trend,
        build_daily_issue_trend,
        build_daily_run_metrics,
        build_hourly_issue_trend,
        build_monthly_trend,
        build_rolling_daily_metrics,
        build_violation_time_series,
        build_weekday_trend,
    )
    from .alerts import build_alert_log_rows, evaluate_significant_changes, send_webhook_alerts
    from .readme_sync import upsert_latest_run_section
    from .report import (
        build_summary_dataframe,
        build_top_counties,
        build_top_violation_types,
        calculate_kpis,
        compare_snapshots,
        render_markdown_report,
    )
    from .transform import transform_violations
    from .validate import run_data_quality_checks
except ImportError:  # pragma: no cover
    from config import AppConfig, load_config
    from extract import fetch_records, paginate_records, load_records_from_file, records_to_dataframe, save_raw_payload
    from charts import generate_all_charts
    from analytics import (
        build_agency_daily_trend,
        build_daily_issue_trend,
        build_daily_run_metrics,
        build_hourly_issue_trend,
        build_monthly_trend,
        build_rolling_daily_metrics,
        build_violation_time_series,
        build_weekday_trend,
    )
    from alerts import build_alert_log_rows, evaluate_significant_changes, send_webhook_alerts
    from readme_sync import upsert_latest_run_section
    from report import (
        build_summary_dataframe,
        build_top_counties,
        build_top_violation_types,
        calculate_kpis,
        compare_snapshots,
        render_markdown_report,
    )
    from transform import transform_violations
    from validate import run_data_quality_checks



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate the daily NYC open parking violations report.")
    parser.add_argument("--limit", type=int, default=None, help="Override the number of API rows to request.")
    parser.add_argument("--open-only", action="store_true", help="Only include violations with open balances.")
    parser.add_argument("--camera-only", action="store_true", help="Only include camera violations.")
    parser.add_argument("--input-file", type=str, default=None, help="Optional local JSON payload for offline runs.")
    parser.add_argument(
        "--report-date",
        type=str,
        default=None,
        help="Optional report date override in YYYY-MM-DD format.",
    )
    parser.add_argument("--paginate", action="store_true", help="Paginate through all available records.")
    parser.add_argument(
        "--backfill-start-date",
        type=str,
        default=None,
        help="Optional issue_date lower bound in YYYY-MM-DD format.",
    )
    parser.add_argument(
        "--backfill-end-date",
        type=str,
        default=None,
        help="Optional issue_date upper bound in YYYY-MM-DD format.",
    )
    return parser.parse_args()



def resolve_report_date(value: str | None) -> date:
    if value is None:
        return date.today()
    return datetime.strptime(value, "%Y-%m-%d").date()


def resolve_optional_date(value: str | None) -> date | None:
    if value is None:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()



def load_previous_snapshot(snapshot_path: Path) -> pd.DataFrame | None:
    if not snapshot_path.exists():
        return None
    return pd.read_csv(snapshot_path, parse_dates=["issue_date", "report_date"])



def save_outputs(
    config: AppConfig,
    report_date: date,
    records: list[dict],
    transformed_df: pd.DataFrame,
    summary_df: pd.DataFrame,
    markdown_report: str,
    analytics_outputs: dict[str, pd.DataFrame],
    alert_log_df: pd.DataFrame,
    quality_checks: list[dict] | None = None,
) -> None:
    stamp = report_date.isoformat()

    raw_path = config.raw_dir / f"violations_{stamp}.json"
    processed_history_path = config.history_dir / f"violations_{stamp}.csv"
    processed_history_parquet_path = config.history_dir / f"violations_{stamp}.parquet"
    latest_snapshot_path = config.processed_dir / "latest_snapshot.csv"
    latest_snapshot_parquet_path = config.processed_dir / "latest_snapshot.parquet"
    latest_summary_path = config.data_dir / "latest_summary.csv"
    latest_summary_parquet_path = config.data_dir / "latest_summary.parquet"
    latest_report_path = config.reports_dir / "daily_report.md"
    dated_report_path = config.reports_dir / f"daily_report_{stamp}.md"
    analytics_dir = config.analytics_dir
    partitioned_dir = config.processed_dir / "partitioned"
    analytics_dir.mkdir(parents=True, exist_ok=True)
    partitioned_dir.mkdir(parents=True, exist_ok=True)

    save_raw_payload(records, raw_path)
    transformed_df.to_csv(processed_history_path, index=False)
    transformed_df.to_parquet(processed_history_parquet_path, index=False)
    transformed_df.to_csv(latest_snapshot_path, index=False)
    transformed_df.to_parquet(latest_snapshot_parquet_path, index=False)
    summary_df.to_csv(latest_summary_path, index=False)
    summary_df.to_parquet(latest_summary_parquet_path, index=False)

    report_partition_dir = partitioned_dir / f"report_date={stamp}"
    report_partition_dir.mkdir(parents=True, exist_ok=True)
    transformed_df.to_parquet(report_partition_dir / "violations.parquet", index=False)

    if "issue_date" in transformed_df.columns and transformed_df["issue_date"].notna().any():
        issue_partition_df = transformed_df.dropna(subset=["issue_date"]).copy()
        issue_partition_df["issue_day"] = issue_partition_df["issue_date"].dt.date.astype(str)
        for issue_day, day_df in issue_partition_df.groupby("issue_day", dropna=True):
            issue_partition_dir = partitioned_dir / f"issue_date={issue_day}"
            issue_partition_dir.mkdir(parents=True, exist_ok=True)
            day_df.drop(columns=["issue_day"]).to_parquet(issue_partition_dir / "violations.parquet", index=False)

    for name, analytics_df in analytics_outputs.items():
        csv_path = analytics_dir / f"{name}.csv"
        parquet_path = analytics_dir / f"{name}.parquet"
        analytics_df.to_csv(csv_path, index=False)
        analytics_df.to_parquet(parquet_path, index=False)

    if not alert_log_df.empty:
        latest_alerts_csv = analytics_dir / "alerts_log.csv"
        if latest_alerts_csv.exists():
            existing = pd.read_csv(latest_alerts_csv)
            alert_log_df = pd.concat([existing, alert_log_df], ignore_index=True)
        alert_log_df.to_csv(latest_alerts_csv, index=False)
        alert_log_df.to_parquet(analytics_dir / "alerts_log.parquet", index=False)

    latest_report_path.write_text(markdown_report, encoding="utf-8")
    dated_report_path.write_text(markdown_report, encoding="utf-8")

    readme_path = config.data_dir.parent / "README.md"
    upsert_latest_run_section(readme_path, summary_df, latest_report_path, quality_checks=quality_checks)



def main() -> None:
    args = parse_args()
    config = load_config()
    report_date = resolve_report_date(args.report_date)
    backfill_start_date = resolve_optional_date(args.backfill_start_date)
    backfill_end_date = resolve_optional_date(args.backfill_end_date)
    if backfill_start_date and backfill_end_date and backfill_start_date > backfill_end_date:
        raise ValueError("--backfill-start-date cannot be after --backfill-end-date.")

    for directory in (
        config.raw_dir,
        config.processed_dir,
        config.history_dir,
        config.analytics_dir,
        config.reports_dir,
        config.charts_dir,
    ):
        directory.mkdir(parents=True, exist_ok=True)

    if args.input_file:
        records = load_records_from_file(args.input_file)
    else:
        if args.paginate:
            records = paginate_records(
                config=config,
                camera_only=args.camera_only,
                open_only=args.open_only,
                issue_start_date=backfill_start_date,
                issue_end_date=backfill_end_date,
            )
        else:
            records = fetch_records(
                config=config,
                limit=args.limit,
                camera_only=args.camera_only,
                open_only=args.open_only,
                issue_start_date=backfill_start_date,
                issue_end_date=backfill_end_date,
            )

    raw_df = records_to_dataframe(records)
    transformed_df = transform_violations(raw_df, report_date=report_date)
    quality_checks = run_data_quality_checks(transformed_df)

    generate_all_charts(transformed_df, config.charts_dir)

    previous_snapshot_path = config.processed_dir / "latest_snapshot.csv"
    previous_df = load_previous_snapshot(previous_snapshot_path)

    kpis = calculate_kpis(transformed_df)
    diff_summary, day_over_day_changes = compare_snapshots(transformed_df, previous_df)
    top_violation_types = build_top_violation_types(transformed_df)
    top_counties = build_top_counties(transformed_df)
    summary_df = build_summary_dataframe(kpis, diff_summary, quality_checks, report_date.isoformat())
    analytics_outputs = {
        "daily_issue_trend": build_daily_issue_trend(transformed_df),
        "weekday_trend": build_weekday_trend(transformed_df),
        "monthly_trend": build_monthly_trend(transformed_df),
        "hourly_issue_trend": build_hourly_issue_trend(transformed_df),
        "rolling_daily_metrics": build_rolling_daily_metrics(transformed_df),
        "violation_time_series": build_violation_time_series(transformed_df),
        "agency_daily_trend": build_agency_daily_trend(transformed_df),
        "daily_run_metrics": build_daily_run_metrics(transformed_df, report_date),
    }

    alerts = evaluate_significant_changes(
        summary_df,
        pct_change_threshold=config.alert_pct_change_threshold,
        absolute_count_threshold=config.alert_absolute_count_threshold,
        amount_pct_change_threshold=config.alert_amount_pct_change_threshold,
        absolute_amount_threshold=config.alert_absolute_amount_threshold,
    )
    alert_log_df = build_alert_log_rows(alerts, report_date.isoformat())
    if config.alerts_enabled and config.alert_webhook_url and alerts:
        try:
            send_webhook_alerts(config.alert_webhook_url, alerts, report_date.isoformat())
        except Exception as exc:  # pragma: no cover
            print(f"Alert webhook failed: {exc}")

    markdown_report = render_markdown_report(
        report_date=report_date.isoformat(),
        kpis=kpis,
        diff_summary=diff_summary,
        top_violation_types=top_violation_types,
        top_counties=top_counties,
        day_over_day_changes=day_over_day_changes,
        quality_checks=quality_checks,
        transformed_df=transformed_df,
        daily_trend_df=analytics_outputs["daily_issue_trend"],
        weekday_trend_df=analytics_outputs["weekday_trend"],
        monthly_trend_df=analytics_outputs["monthly_trend"],
        significant_alerts=alerts,
    )

    save_outputs(
        config,
        report_date,
        records,
        transformed_df,
        summary_df,
        markdown_report,
        analytics_outputs,
        alert_log_df,
        quality_checks,
    )

    print(f"Saved {len(transformed_df):,} transformed records.")
    print(f"Saved report to {config.reports_dir / 'daily_report.md'}")
    print(f"Saved summary to {config.data_dir / 'latest_summary.csv'}")
    print(f"Saved analytics outputs to {config.analytics_dir}")
    print(f"Generated charts in {config.charts_dir}")
    if alerts:
        print(f"Generated {len(alerts)} alert(s).")


if __name__ == "__main__":
    main()




