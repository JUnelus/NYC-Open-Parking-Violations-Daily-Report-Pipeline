from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def generate_violation_types_chart(df: pd.DataFrame, output_path: Path) -> None:
    """Generate a bar chart for top violation types."""
    if df.empty:
        return

    top_violations = (
        df.groupby("violation", dropna=False)
        .size()
        .sort_values(ascending=True)
        .tail(10)
    )

    fig, ax = plt.subplots(figsize=(12, 6))
    top_violations.plot(kind="barh", ax=ax, color="steelblue")
    ax.set_xlabel("Count")
    ax.set_ylabel("Violation Type")
    ax.set_title("Top 10 Violation Types")
    plt.tight_layout()
    fig.savefig(output_path, dpi=100, bbox_inches="tight")
    plt.close(fig)


def generate_counties_chart(df: pd.DataFrame, output_path: Path) -> None:
    """Generate a bar chart for top counties by amount due."""
    if df.empty:
        return

    top_counties = (
        df.groupby("county", dropna=False)["amount_due"]
        .sum()
        .sort_values(ascending=True)
        .tail(5)
    )

    fig, ax = plt.subplots(figsize=(10, 6))
    top_counties.plot(kind="barh", ax=ax, color="coral")
    ax.set_xlabel("Amount Due ($)")
    ax.set_ylabel("County")
    ax.set_title("Top 5 Counties by Amount Due")
    plt.tight_layout()
    fig.savefig(output_path, dpi=100, bbox_inches="tight")
    plt.close(fig)


def generate_agencies_chart(df: pd.DataFrame, output_path: Path) -> None:
    """Generate a bar chart for top agencies by violation count."""
    if df.empty:
        return

    top_agencies = (
        df.groupby("issuing_agency", dropna=False)
        .size()
        .sort_values(ascending=True)
        .tail(8)
    )

    fig, ax = plt.subplots(figsize=(10, 6))
    top_agencies.plot(kind="barh", ax=ax, color="mediumseagreen")
    ax.set_xlabel("Violation Count")
    ax.set_ylabel("Issuing Agency")
    ax.set_title("Top Issuing Agencies by Violation Count")
    plt.tight_layout()
    fig.savefig(output_path, dpi=100, bbox_inches="tight")
    plt.close(fig)


def generate_camera_vs_parking_chart(df: pd.DataFrame, output_path: Path) -> None:
    """Generate a pie chart for camera vs non-camera violations."""
    if df.empty:
        return

    if "is_camera_violation" not in df.columns:
        return

    counts = df["is_camera_violation"].value_counts()

    # Handle different cases
    if len(counts) == 2:
        # Both camera and non-camera violations exist
        sizes = [counts.get(False, 0), counts.get(True, 0)]
        labels = ["Non-Camera Parking", "Camera"]
    elif len(counts) == 1:
        # Only one type exists
        if counts.index[0] is False or counts.index[0] == False:
            sizes = [counts.iloc[0], 0]
        else:
            sizes = [0, counts.iloc[0]]
        labels = ["Non-Camera Parking", "Camera"]
    else:
        # No data
        return

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90, colors=["#ff9999", "#66b3ff"])
    ax.set_title("Camera vs Non-Camera Violations")
    plt.tight_layout()
    fig.savefig(output_path, dpi=100, bbox_inches="tight")
    plt.close(fig)


def generate_all_charts(df: pd.DataFrame, charts_dir: Path) -> None:
    """Generate all charts for the daily report."""
    charts_dir.mkdir(parents=True, exist_ok=True)

    generate_violation_types_chart(df, charts_dir / "top_violations.png")
    generate_counties_chart(df, charts_dir / "top_counties.png")
    generate_agencies_chart(df, charts_dir / "top_agencies.png")
    generate_camera_vs_parking_chart(df, charts_dir / "camera_vs_parking.png")


