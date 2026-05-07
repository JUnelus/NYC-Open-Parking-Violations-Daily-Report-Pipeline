from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.extract import records_to_dataframe  # noqa: E402
from src.transform import transform_violations  # noqa: E402


@pytest.fixture()
def sample_records() -> list[dict]:
    fixture_path = REPO_ROOT / "tests" / "fixtures_sample_payload.json"
    return json.loads(fixture_path.read_text(encoding="utf-8"))


@pytest.fixture()
def raw_df(sample_records: list[dict]) -> pd.DataFrame:
    return records_to_dataframe(sample_records)


@pytest.fixture()
def transformed_df(raw_df: pd.DataFrame) -> pd.DataFrame:
    return transform_violations(raw_df)



