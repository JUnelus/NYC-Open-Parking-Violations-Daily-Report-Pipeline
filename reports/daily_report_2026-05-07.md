# NYC Open Parking & Camera Violations Daily Report

Report Date: 2026-05-07

## Dashboard & Charts

![Top Violations](./charts/top_violations.png)
![Top Counties](./charts/top_counties.png)
![Top Agencies](./charts/top_agencies.png)
![Camera vs Parking](./charts/camera_vs_parking.png)

## Executive Summary

- Total Records Pulled: 5
- New Records Pulled Since Yesterday: 5
- Open Amount Due: $420.00
- Total Fine Amount: $375.00
- Total Penalties: $50.00
- Total Interest: $15.00
- Total Payments Recorded: $20.00
- Total Camera Violations: 3
- Total Non-Camera Parking Violations: 2
- Previous Snapshot Record Count: 5
- Resolved or Missing Since Yesterday: 5
- Net Record Change: 0

## Top Violation Types

| Rank | Violation Type                 | Count | Amount Due |
| ---- | ------------------------------ | ----- | ---------- |
| 1    | BUS LANE VIOLATION             | 1     | 150        |
| 2    | DOUBLE PARKING                 | 1     | 95         |
| 3    | FAILURE TO STOP AT RED LIGHT   | 1     | 65         |
| 4    | PHTO SCHOOL ZN SPEED VIOLATION | 1     | 60         |
| 5    | NO PARKING-STREET CLEANING     | 1     | 50         |

| ## Top 5 Counties by Amount Due

| Rank | County | Count | Amount Due |
| ---- | ------ | ----- | ---------- |
| 1    | BX     | 1     | 150        |
| 2    | R      | 1     | 95         |
| 3    | Q      | 1     | 65         |
| 4    | NY     | 1     | 60         |
| 5    | K      | 1     | 50         |

## Borough & County Breakdown

| County | Count | Amount Due |
| ------ | ----- | ---------- |
| BX     | 1     | 150        |
| R      | 1     | 95         |
| Q      | 1     | 65         |
| NY     | 1     | 60         |
| K      | 1     | 50         |

## Issuing Agency Analysis

| Issuing Agency | Count | Amount Due |
| -------------- | ----- | ---------- |
| DOT            | 2     | 215        |
| NYPD           | 2     | 145        |
| DEP            | 1     | 60         |

## Biggest Day-over-Day Changes

| Violation Type                 | Current Count | Current Amount Due | Previous Count | Previous Amount Due | Count Change | Amount Due Change |
| ------------------------------ | ------------- | ------------------ | -------------- | ------------------- | ------------ | ----------------- |
| BUS LANE VIOLATION             | 1.00          | 150.00             | 0.00           | 0.00                | 1.00         | 150.00            |
| DOUBLE PARKING                 | 1.00          | 95.00              | 0.00           | 0.00                | 1.00         | 95.00             |
| FAILURE TO STOP AT RED LIGHT   | 1.00          | 65.00              | 0.00           | 0.00                | 1.00         | 65.00             |
| PHTO SCHOOL ZN SPEED VIOLATION | 1.00          | 60.00              | 0.00           | 0.00                | 1.00         | 60.00             |
| FIRE HYDRANT                   | 0.00          | 0.00               | 1.00           | 0.00                | -1.00        | 0.00              |
| INSP. STICKER-EXPIRED/MISSING  | 0.00          | 0.00               | 1.00           | 0.00                | -1.00        | 0.00              |
| MISCELLANEOUS                  | 0.00          | 0.00               | 1.00           | 0.00                | -1.00        | 0.00              |
| OBSTRUCTING DRIVEWAY           | 0.00          | 0.00               | 1.00           | 0.00                | -1.00        | 0.00              |
| NO PARKING-STREET CLEANING     | 1.00          | 50.00              | 1.00           | 0.00                | 0.00         | 50.00             |

## Data Quality Checks

| Check                                 | Result | Details                              |
| ------------------------------------- | ------ | ------------------------------------ |
| API returned data                     | PASS   | Rows available: 5                    |
| Required columns present              | PASS   | All required columns are present.    |
| Numeric fields converted successfully | PASS   | Numeric columns are typed correctly. |
| No negative amount_due values         | PASS   | Negative amount_due rows: 0          |
| issue_date parsed successfully        | FAIL   | Rows with invalid issue_date: 1      |
| summons_number not null               | PASS   | Rows with null summons_number: 0     |

## QA Notes

One or more data quality checks failed. Review the details table below before publishing downstream outputs.
