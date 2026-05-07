from __future__ import annotations

from src.validate import all_checks_passed, run_data_quality_checks



def test_data_quality_detects_invalid_issue_date(transformed_df) -> None:
    checks = run_data_quality_checks(transformed_df)
    by_name = {check["check"]: check for check in checks}

    assert by_name["API returned data"]["result"] == "PASS"
    assert by_name["Required columns present"]["result"] == "PASS"
    assert by_name["Numeric fields converted successfully"]["result"] == "PASS"
    assert by_name["No negative amount_due values"]["result"] == "PASS"
    assert by_name["issue_date parsed successfully"]["result"] == "FAIL"
    assert by_name["summons_number not null"]["result"] == "PASS"
    assert all_checks_passed(checks) is False


