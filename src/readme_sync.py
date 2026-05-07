from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

LATEST_MARKER_START = "<!-- LATEST_RUN_START -->"
LATEST_MARKER_END = "<!-- LATEST_RUN_END -->"



def build_latest_run_section(
    summary_df: pd.DataFrame,
    report_path: Path,
    charts_relative_dir: str = "reports/charts",
    quality_checks: list[dict[str, Any]] | None = None,
    anomaly_df: pd.DataFrame | None = None,
) -> str:
    if summary_df.empty:
        body = "_No latest run data available._"
    else:
        row = summary_df.iloc[0]
        checks_failed = int(row.get("checks_failed", 0))

        failed_lines: list[str] = []
        if checks_failed > 0 and quality_checks:
            failed_checks = [c for c in quality_checks if c.get("result") == "FAIL"]
            if failed_checks:
                failed_lines = ["", "### Quality Check Failures", ""]
                for c in failed_checks:
                    failed_lines.append(f"- **{c['check']}**: {c['details']}")

        anomaly_lines: list[str] = []
        if anomaly_df is not None and not anomaly_df.empty:
            report_date = str(row.get("report_date", ""))
            current_anomalies = anomaly_df[anomaly_df["report_date"].astype(str) == report_date]
            if not current_anomalies.empty:
                anomaly_lines = ["", f"- Daily Metric Anomalies Detected: {len(current_anomalies)}", "", "### Top Anomaly Findings", ""]
                top_rows = current_anomalies.head(3)
                for _, anomaly in top_rows.iterrows():
                    anomaly_lines.append(f"- [{anomaly.get('severity', 'MEDIUM')}] {anomaly.get('reason', '')}")

        body = "\n".join(
            [
                f"- Report Date: {row.get('report_date', 'Unknown')}",
                f"- Total Records Pulled: {int(row.get('total_records_pulled', 0)):,}",
                f"- Open Amount Due: ${float(row.get('total_open_amount_due', 0.0)):,.2f}",
                f"- New Records Pulled: {int(row.get('new_records_pulled', 0)):,}",
                f"- Net Record Change: {int(row.get('net_record_change', 0)):,}",
                f"- Quality Checks Passed: {int(row.get('checks_passed', 0))}",
                f"- Quality Checks Failed: {checks_failed}",
                *anomaly_lines,
                *failed_lines,
                "",
                "### Latest Charts",
                "",
                f"![Top Violations]({charts_relative_dir}/top_violations.png)",
                f"![Top Counties]({charts_relative_dir}/top_counties.png)",
                f"![Top Agencies]({charts_relative_dir}/top_agencies.png)",
                f"![Camera vs Parking]({charts_relative_dir}/camera_vs_parking.png)",
                "",
                f"Latest report file: `{report_path.as_posix()}`",
            ]
        )

    return f"{LATEST_MARKER_START}\n## Latest Automated Run\n\n{body}\n{LATEST_MARKER_END}"



def upsert_latest_run_section(
    readme_path: Path,
    summary_df: pd.DataFrame,
    report_path: Path,
    quality_checks: list[dict[str, Any]] | None = None,
    anomaly_df: pd.DataFrame | None = None,
) -> None:
    section = build_latest_run_section(summary_df, report_path, quality_checks=quality_checks, anomaly_df=anomaly_df)
    original = readme_path.read_text(encoding="utf-8")

    if LATEST_MARKER_START in original and LATEST_MARKER_END in original:
        start_index = original.index(LATEST_MARKER_START)
        end_index = original.index(LATEST_MARKER_END) + len(LATEST_MARKER_END)
        updated = original[:start_index] + section + original[end_index:]
    else:
        updated = section + "\n\n" + original

    readme_path.write_text(updated, encoding="utf-8")

