#!/usr/bin/env python3
"""Extract numeric tables from the Cao et al. 2024 dementia supplement text.

Input is the `pdftotext -layout` output from the Springer supplementary PDF.
Outputs two tidy CSVs:
- forecast tables: eTables 3-6
- decomposition tables: eTables 1-2
"""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


TABLE_LABELS = {
    "1": ("decomposition_prevalence", "dementia_prevalence_change"),
    "2": ("decomposition_mortality", "dementia_mortality_change"),
    "3": ("predicted_prevalent_cases", "prevalent_cases"),
    "4": ("predicted_prevalence_rates", "prevalence_rate_per_100k"),
    "5": ("predicted_mortality_numbers", "mortality_count"),
    "6": ("predicted_mortality_rates", "mortality_rate_per_100k"),
}

FORECAST_RE = re.compile(
    r"^\s*(?P<age>(?:\d{2}-\d{2}|95\+)\s+years)\s+"
    r"(?P<sex>Both|Female|Male)\s+"
    r"(?P<year>\d{4})\s+"
    r"(?P<estimate>\d+)\s+\((?P<lower>\d+)-(?P<upper>\d+)\)\s*$"
)

DECOMP_RE = re.compile(
    r"^\s*(?P<sex>Male|Female)\s+"
    r"(?P<overall>-?\d+)\s+"
    r"(?P<aging>-?\d+)\s+\((?P<aging_pct>-?\d+(?:\.\d+)?)%\)\s+"
    r"(?P<growth>-?\d+)\s+\((?P<growth_pct>-?\d+(?:\.\d+)?)%\)\s+"
    r"(?P<epi>-?\d+)\s+\((?P<epi_pct>-?\d+(?:\.\d+)?)%\)\s*$"
)


def parse_tables(text_path: Path) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    forecast_rows: list[dict[str, str]] = []
    decomposition_rows: list[dict[str, str]] = []
    current_table: str | None = None

    for raw_line in text_path.read_text(encoding="utf-8").splitlines():
        table_match = re.search(r"eTable\s+([1-6])\.", raw_line)
        if table_match:
            current_table = table_match.group(1)
            continue

        if raw_line.startswith("Supplementary method"):
            current_table = None
            continue

        if current_table in {"3", "4", "5", "6"}:
            forecast_match = FORECAST_RE.match(raw_line)
            if forecast_match:
                table_name, metric = TABLE_LABELS[current_table]
                row = forecast_match.groupdict()
                row["age_group"] = " ".join(row.pop("age").split())
                row["source_table"] = f"eTable {current_table}"
                row["table_name"] = table_name
                row["metric"] = metric
                row["estimate"] = str(int(row["estimate"]))
                row["lower_95ci"] = str(int(row.pop("lower")))
                row["upper_95ci"] = str(int(row.pop("upper")))
                forecast_rows.append(row)

        elif current_table in {"1", "2"}:
            decomp_match = DECOMP_RE.match(raw_line)
            if decomp_match:
                table_name, outcome = TABLE_LABELS[current_table]
                row = decomp_match.groupdict()
                row["source_table"] = f"eTable {current_table}"
                row["table_name"] = table_name
                row["outcome"] = outcome
                row["overall_change"] = row.pop("overall")
                row["aging_change"] = row.pop("aging")
                row["aging_pct"] = row.pop("aging_pct")
                row["population_growth_change"] = row.pop("growth")
                row["population_growth_pct"] = row.pop("growth_pct")
                row["epidemiological_change"] = row.pop("epi")
                row["epidemiological_pct"] = row.pop("epi_pct")
                decomposition_rows.append(row)

    return forecast_rows, decomposition_rows


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("text_path", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()

    forecast_rows, decomposition_rows = parse_tables(args.text_path)

    forecast_fields = [
        "source_table",
        "table_name",
        "metric",
        "age_group",
        "sex",
        "year",
        "estimate",
        "lower_95ci",
        "upper_95ci",
    ]
    decomp_fields = [
        "source_table",
        "table_name",
        "outcome",
        "sex",
        "overall_change",
        "aging_change",
        "aging_pct",
        "population_growth_change",
        "population_growth_pct",
        "epidemiological_change",
        "epidemiological_pct",
    ]

    forecast_path = args.output_dir / "pmc11336039_cao2024_supplement_forecast_tables.csv"
    decomp_path = args.output_dir / "pmc11336039_cao2024_supplement_decomposition_tables.csv"
    write_csv(forecast_path, forecast_rows, forecast_fields)
    write_csv(decomp_path, decomposition_rows, decomp_fields)

    print(f"Wrote {len(forecast_rows)} forecast rows to {forecast_path}")
    print(f"Wrote {len(decomposition_rows)} decomposition rows to {decomp_path}")


if __name__ == "__main__":
    main()
