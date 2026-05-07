from __future__ import annotations

from pathlib import Path
from typing import cast

import pandas as pd
import streamlit as st

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"
ANALYTICS_DIR = DATA_DIR / "analytics"


@st.cache_data
def load_latest_snapshot() -> pd.DataFrame:
    path = PROCESSED_DIR / "latest_snapshot.csv"
    if not path.exists():
        return pd.DataFrame()
    return cast(pd.DataFrame, pd.read_csv(path, parse_dates=["issue_date", "report_date"]))


@st.cache_data
def load_daily_trend() -> pd.DataFrame:
    path = ANALYTICS_DIR / "daily_issue_trend.csv"
    if not path.exists():
        return pd.DataFrame()
    return cast(pd.DataFrame, pd.read_csv(path))


@st.cache_data
def load_weekday_trend() -> pd.DataFrame:
    path = ANALYTICS_DIR / "weekday_trend.csv"
    if not path.exists():
        return pd.DataFrame()
    return cast(pd.DataFrame, pd.read_csv(path))


@st.cache_data
def load_violation_timeseries() -> pd.DataFrame:
    path = ANALYTICS_DIR / "violation_time_series.csv"
    if not path.exists():
        return pd.DataFrame()
    return cast(pd.DataFrame, pd.read_csv(path))


@st.cache_data
def load_hourly_trend() -> pd.DataFrame:
    path = ANALYTICS_DIR / "hourly_issue_trend.csv"
    if not path.exists():
        return pd.DataFrame()
    return cast(pd.DataFrame, pd.read_csv(path))


@st.cache_data
def load_agency_daily_trend() -> pd.DataFrame:
    path = ANALYTICS_DIR / "agency_daily_trend.csv"
    if not path.exists():
        return pd.DataFrame()
    return cast(pd.DataFrame, pd.read_csv(path))



def render_overview(df: pd.DataFrame) -> None:
    st.subheader("Overview")
    if df.empty:
        st.warning("No snapshot found. Run `python src/main.py` first.")
        return

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Records", f"{len(df):,}")
    col2.metric("Open Amount Due", f"${df['amount_due'].sum():,.2f}")
    col3.metric("Camera Violations", f"{int(df['is_camera_violation'].sum()):,}")



def render_filters(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filters")

    violations = sorted(df["violation"].dropna().astype(str).unique().tolist()) if not df.empty else []
    counties = sorted(df["county"].dropna().astype(str).unique().tolist()) if not df.empty else []

    selected_violations = st.sidebar.multiselect("Violation Types", violations, default=[])
    selected_counties = st.sidebar.multiselect("Counties", counties, default=[])

    filtered = df.copy()
    if selected_violations:
        filtered = filtered[filtered["violation"].isin(selected_violations)]
    if selected_counties:
        filtered = filtered[filtered["county"].isin(selected_counties)]

    return filtered



def render_top_tables(df: pd.DataFrame) -> None:
    st.subheader("Top Violations and Counties")
    if df.empty:
        st.info("No data available for selected filters.")
        return

    left, right = st.columns(2)

    top_violations = (
        df.groupby("violation", dropna=False)
        .agg(Count=("summons_number", "count"), Amount_Due=("amount_due", "sum"))
        .sort_values(["Count", "Amount_Due"], ascending=[False, False])
        .head(10)
        .reset_index()
    )

    top_counties = (
        df.groupby("county", dropna=False)
        .agg(Count=("summons_number", "count"), Amount_Due=("amount_due", "sum"))
        .sort_values(["Amount_Due", "Count"], ascending=[False, False])
        .head(10)
        .reset_index()
    )

    left.dataframe(top_violations, use_container_width=True)
    right.dataframe(top_counties, use_container_width=True)



def render_time_series() -> None:
    st.subheader("Time-Series Analysis")

    daily = load_daily_trend()
    weekday = load_weekday_trend()
    violation_trend = load_violation_timeseries()
    hourly = load_hourly_trend()
    agency_daily = load_agency_daily_trend()

    if daily.empty:
        st.info("No analytics files found yet. Run the pipeline to generate them.")
        return

    st.markdown("**Daily Violations Trend**")
    st.line_chart(daily.set_index("issue_day")["violations_count"])

    st.markdown("**Daily Amount Due Trend**")
    st.line_chart(daily.set_index("issue_day")["amount_due"])

    if not weekday.empty:
        st.markdown("**Weekday Pattern**")
        st.bar_chart(weekday.set_index("weekday")["violations_count"])

    if not hourly.empty:
        st.markdown("**Hourly Pattern**")
        st.bar_chart(hourly.set_index("issue_hour")["violations_count"])

    if not violation_trend.empty:
        st.markdown("**Top Violation Types Over Time**")
        pivoted = violation_trend.pivot(index="issue_day", columns="violation", values="violations_count").fillna(0)
        st.line_chart(pivoted)

    if not agency_daily.empty:
        st.markdown("**Top Agencies Over Time**")
        pivoted_agencies = agency_daily.pivot(
            index="issue_day",
            columns="issuing_agency",
            values="violations_count",
        ).fillna(0)
        st.line_chart(pivoted_agencies)



def main() -> None:
    st.set_page_config(page_title="NYC Open Parking Violations Dashboard", layout="wide")
    st.title("NYC Open Parking Violations Dashboard")
    st.caption("Interactive dashboard generated from daily pipeline outputs.")

    snapshot = load_latest_snapshot()
    filtered = render_filters(snapshot) if not snapshot.empty else snapshot

    render_overview(filtered)
    render_top_tables(filtered)
    render_time_series()

    st.subheader("Filtered Snapshot")
    if filtered.empty:
        st.info("No rows to display for selected filters.")
    else:
        st.dataframe(filtered.head(500), use_container_width=True)


if __name__ == "__main__":
    main()



