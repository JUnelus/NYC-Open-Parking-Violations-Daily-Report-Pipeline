from __future__ import annotations

from pathlib import Path

import pandas as pd

LATEST_MARKER_START = "<!-- LATEST_RUN_START -->"
LATEST_MARKER_END = "<!-- LATEST_RUN_END -->"



def build_latest_run_section(summary_df: pd.DataFrame, report_path: Path, charts_relative_dir: str = "reports/charts") -> str:
    if summary_df.empty:
        body = "_No latest run data available._"
    else:
        row = summary_df.iloc[0]
        body = "\n".join(
            [
                f"- Report Date: {row.get('report_date', 'Unknown')}",
                f"- Total Records Pulled: {int(row.get('total_records_pulled', 0)):,}",
                f"- Open Amount Due: ${float(row.get('total_open_amount_due', 0.0)):,.2f}",
                f"- New Records Pulled: {int(row.get('new_records_pulled', 0)):,}",
                f"- Net Record Change: {int(row.get('net_record_change', 0)):,}",
                f"- Quality Checks Passed: {int(row.get('checks_passed', 0))}",
                f"- Quality Checks Failed: {int(row.get('checks_failed', 0))}",
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



def upsert_latest_run_section(readme_path: Path, summary_df: pd.DataFrame, report_path: Path) -> None:
    section = build_latest_run_section(summary_df, report_path)
    original = readme_path.read_text(encoding="utf-8")

    if LATEST_MARKER_START in original and LATEST_MARKER_END in original:
        start_index = original.index(LATEST_MARKER_START)
        end_index = original.index(LATEST_MARKER_END) + len(LATEST_MARKER_END)
        updated = original[:start_index] + section + original[end_index:]
    else:
        updated = section + "\n\n" + original

    readme_path.write_text(updated, encoding="utf-8")

