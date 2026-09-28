#!/usr/bin/env python3
"""Stage 3 post-lock reconciliation and shared-scope reanalysis.

This script reads locked Sol inputs and the approved reference bundle, writes
only under stage3/ outside reference/ and locked_supplement/, and uses only the
Python standard library.
"""

from __future__ import annotations

import csv
import hashlib
import math
import random
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from statistics import fmean


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "stage3"
CENSOR = date(2026, 6, 1)
LANDMARK = date(1973, 1, 1)
HORIZON = 50.0
BOOTSTRAP_REPLICATES = 50_000
BOOTSTRAP_SEED = 20260721
Z975 = 1.959963984540054

LOCKED_TREE_EXPECTED = {
    "stage1": "3c23c3cebb6e37f0a8ab443cb1a7bdda6235d9e5cdb341a6d55c0a6f763fd8e1",
    "stage1b": "65b5a1128844641577c96cb4fe396a8422bc75582d2d77035c91e873ac73e5d3",
    "stage1c": "c7b3555a8a569cab5429fb07e76e5b502bbdc466494548409ad17cdfa1c7901c",
    "stage2": "95b6c76f30a507bba1c363507dc04d2232488475eda34085d216e2937161799a",
    "stage3/reference": "d4bc2493af7604615b5c9f6efd417d8ae4fe4799f5e27436c7d18bc23bd0e363",
    "stage3/locked_supplement": "4cf652dc741ee102c8d378352d8864f77a5c7b051dc41a71e2eea78b628726cd",
}
BLIND_HASH = "727d766af5a058012d6f68c6ce1890dc48b1625d9fae9d6ebfd18661579111df"
CORRECTED_HASH = "bccdae4e350accb7c34e7324cfed85f441a181009c73278529af1bb9b83a6600"


def read_csv(path: Path, delimiter: str = ",") -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=delimiter))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def tree_aggregate(relative: str) -> str:
    """Match `find | sort | shasum | shasum` used for the pre-analysis baseline."""
    base = ROOT / relative
    lines = []
    for path in sorted(p for p in base.rglob("*") if p.is_file()):
        rel = path.relative_to(ROOT).as_posix()
        lines.append(f"{sha256_file(path)}  {rel}\n")
    return hashlib.sha256("".join(lines).encode("utf-8")).hexdigest()


def parse_date(value: str) -> date | None:
    return date.fromisoformat(value) if value else None


def years_between(start: date, end: date) -> float:
    return (end - start).days / 365.2425


def add_years(value: date, years: int) -> date:
    try:
        return value.replace(year=value.year + years)
    except ValueError:
        return value.replace(year=value.year + years, month=2, day=28)


def percentile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower, upper = math.floor(position), math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def km_rmst(records: list[tuple[float, int]], horizon: float) -> float:
    ordered = sorted(records)
    survival, previous, area, risk, index = 1.0, 0.0, 0.0, len(ordered), 0
    while index < len(ordered):
        current = ordered[index][0]
        if current > horizon:
            break
        area += survival * max(0.0, current - previous)
        deaths = removed = 0
        while index < len(ordered) and ordered[index][0] == current:
            deaths += ordered[index][1]
            removed += 1
            index += 1
        if risk and deaths:
            survival *= 1.0 - deaths / risk
        risk -= removed
        previous = current
    return area + survival * max(0.0, horizon - previous)


def bootstrap_rmst_difference(
    first: list[tuple[float, int]], second: list[tuple[float, int]]
) -> tuple[float, float, float]:
    point = km_rmst(first, HORIZON) - km_rmst(second, HORIZON)
    generator = random.Random(BOOTSTRAP_SEED)
    estimates = []
    for _ in range(BOOTSTRAP_REPLICATES):
        a = [first[generator.randrange(len(first))] for _ in first]
        b = [second[generator.randrange(len(second))] for _ in second]
        estimates.append(km_rmst(a, HORIZON) - km_rmst(b, HORIZON))
    return point, percentile(estimates, 0.025), percentile(estimates, 0.975)


def binomial_cdf(k: int, n: int, probability: float) -> float:
    if k < 0:
        return 0.0
    if k >= n:
        return 1.0
    if probability <= 0.0:
        return 1.0
    if probability >= 1.0:
        return 0.0
    return sum(
        math.comb(n, j)
        * probability**j
        * (1.0 - probability) ** (n - j)
        for j in range(k + 1)
    )


def bisect_decreasing(function, target: float) -> float:
    low, high = 0.0, 1.0
    for _ in range(100):
        middle = (low + high) / 2.0
        if function(middle) > target:
            low = middle
        else:
            high = middle
    return (low + high) / 2.0


def clopper_pearson(successes: int, total: int) -> tuple[float, float]:
    lower, upper = 0.0, 1.0
    if successes > 0:
        lower = bisect_decreasing(
            lambda p: binomial_cdf(successes - 1, total, p), 0.975
        )
    if successes < total:
        upper = bisect_decreasing(lambda p: binomial_cdf(successes, total, p), 0.025)
    return lower, upper


def wilson(successes: int, total: int) -> tuple[float, float]:
    p = successes / total
    z2 = Z975 * Z975
    denominator = 1.0 + z2 / total
    center = (p + z2 / (2.0 * total)) / denominator
    half = (
        Z975
        * math.sqrt(p * (1.0 - p) / total + z2 / (4.0 * total * total))
        / denominator
    )
    return max(0.0, center - half), min(1.0, center + half)


def newcombe_difference(
    x1: int, n1: int, x0: int, n0: int
) -> tuple[float, float, float]:
    """Newcombe method 10, copied from the locked Stage 2R implementation."""
    p1, p0 = x1 / n1, x0 / n0
    l1, u1 = wilson(x1, n1)
    l0, u0 = wilson(x0, n0)
    difference = p1 - p0
    lower = difference - math.sqrt((p1 - l1) ** 2 + (u0 - p0) ** 2)
    upper = difference + math.sqrt((u1 - p1) ** 2 + (p0 - l0) ** 2)
    return difference, max(-1.0, lower), min(1.0, upper)


def fisher_exact_two_sided(a: int, b: int, c: int, d: int) -> float:
    n1, n0, successes = a + b, c + d, a + c
    low, high = max(0, successes - n0), min(n1, successes)
    weights = [
        math.comb(n1, x) * math.comb(n0, successes - x)
        for x in range(low, high + 1)
    ]
    total = sum(weights)
    probabilities = [value / total for value in weights]
    observed = probabilities[a - low]
    return min(1.0, sum(p for p in probabilities if p <= observed + 1e-15))


def bootstrap_binary_difference(
    a_success: int, a_n: int, b_success: int, b_n: int
) -> tuple[float, float, float]:
    first = [1] * a_success + [0] * (a_n - a_success)
    second = [1] * b_success + [0] * (b_n - b_success)
    generator = random.Random(BOOTSTRAP_SEED)
    estimates = []
    for _ in range(BOOTSTRAP_REPLICATES):
        pa = sum(first[generator.randrange(a_n)] for _ in range(a_n)) / a_n
        pb = sum(second[generator.randrange(b_n)] for _ in range(b_n)) / b_n
        estimates.append(pa - pb)
    point = a_success / a_n - b_success / b_n
    return point, percentile(estimates, 0.025), percentile(estimates, 0.975)


def km_at_with_variance(
    records: list[tuple[float, int]], target: float
) -> tuple[float, float, float, float]:
    ordered = sorted(records)
    survival, greenwood, risk, index = 1.0, 0.0, len(ordered), 0
    while index < len(ordered):
        current = ordered[index][0]
        if current > target:
            break
        deaths = removed = 0
        while index < len(ordered) and ordered[index][0] == current:
            deaths += ordered[index][1]
            removed += 1
            index += 1
        if deaths and risk > deaths:
            survival *= 1.0 - deaths / risk
            greenwood += deaths / (risk * (risk - deaths))
        elif deaths and risk == deaths:
            survival = 0.0
        risk -= removed
    if survival <= 0:
        return 0.0, 0.0, 0.0, 0.0
    if survival >= 1 or greenwood == 0:
        return survival, survival, survival, survival * survival * greenwood
    transformed = math.log(-math.log(survival))
    se = math.sqrt(greenwood) / abs(math.log(survival))
    lower = math.exp(-math.exp(transformed + Z975 * se))
    upper = math.exp(-math.exp(transformed - Z975 * se))
    return survival, lower, upper, survival * survival * greenwood


def km_at(
    records: list[tuple[float, int]], target: float
) -> tuple[float, float, float]:
    survival, lower, upper, _ = km_at_with_variance(records, target)
    return survival, lower, upper


def logrank_test(
    a: list[tuple[float, int]], b: list[tuple[float, int]]
) -> tuple[float, float, float, float]:
    times = sorted({t for t, event in a + b if event})
    observed_a = expected_a = variance = 0.0
    for current in times:
        na = sum(t >= current for t, _ in a)
        nb = sum(t >= current for t, _ in b)
        da = sum(event for t, event in a if t == current)
        db = sum(event for t, event in b if t == current)
        n, d = na + nb, da + db
        if n <= 1 or d <= 0:
            continue
        observed_a += da
        expected_a += d * na / n
        variance += na * nb * d * (n - d) / (n * n * (n - 1))
    z = (observed_a - expected_a) / math.sqrt(variance)
    return observed_a, expected_a, z, math.erfc(abs(z) / math.sqrt(2.0))


class LifeTable:
    def __init__(self, rows: list[dict[str, str]]):
        self.by_age = {int(row["age"]): row for row in rows}
        self.min_age, self.max_age = min(self.by_age), max(self.by_age)
        self.l30 = self.lx_at(30.0)

    def lx_at(self, age: float) -> float:
        if age <= self.min_age:
            return float(self.by_age[self.min_age]["lx"])
        if age >= self.max_age:
            return float(self.by_age[self.max_age]["lx"])
        low = int(math.floor(age))
        high = low + 1
        fraction = age - low
        lx_low = float(self.by_age[low]["lx"])
        lx_high = float(self.by_age[high]["lx"])
        return lx_low + fraction * (lx_high - lx_low)

    def expected_events(self, endpoints: list[float]) -> float:
        total = 0.0
        for endpoint in endpoints:
            survival = max(self.lx_at(endpoint) / self.l30, 1e-12)
            total += -math.log(survival)
        return total


def reference_id_map(reference: list[dict[str, str]]) -> dict[str, str]:
    return {
        row["Name"]: f"REF{index:03d}"
        for index, row in enumerate(sorted(reference, key=lambda x: x["Name"]), 1)
    }


def identity_map(
    ours: list[dict[str, str]], reference: list[dict[str, str]]
) -> tuple[list[dict], dict[str, dict[str, str]], list[dict[str, str]]]:
    by_birth: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in reference:
        by_birth[row["Date of Birth"]].append(row)
    ref_ids = reference_id_map(reference)
    matched_names: set[str] = set()
    lookup: dict[str, dict[str, str]] = {}
    rows: list[dict] = []
    for person in ours:
        candidates = by_birth[person["birth_date"]]
        if len(candidates) == 1:
            match = candidates[0]
            basis = "exact birth date; compatible person name"
        elif person["person_id"] == "p014_thomas_p_stafford":
            match = next(row for row in candidates if "Stafford" in row["Name"])
            basis = "exact birth date collision resolved by surname/full identity"
        elif person["person_id"] == "p050_edgar_d_mitchell":
            match = next(row for row in candidates if "Mitchell" in row["Name"])
            basis = "exact birth date collision resolved by surname/full identity"
        else:
            raise AssertionError(f"Unresolved identity: {person['full_name']}")
        matched_names.add(match["Name"])
        lookup[person["person_id"]] = match
        rows.append(
            {
                "mapping_id": f"MAP{len(rows)+1:03d}",
                "ours_person_id": person["person_id"],
                "reference_person_id": ref_ids[match["Name"]],
                "ours_name": person["full_name"],
                "reference_name": match["Name"],
                "birth_date": person["birth_date"],
                "match_basis": basis,
                "match_confidence": "HIGH",
                "scope_status": "SHARED",
                "notes": "No fuzzy-name-only match was used.",
            }
        )
    only_reference = [row for row in reference if row["Name"] not in matched_names]
    for row in sorted(only_reference, key=lambda x: x["Name"]):
        rows.append(
            {
                "mapping_id": f"MAP{len(rows)+1:03d}",
                "ours_person_id": "",
                "reference_person_id": ref_ids[row["Name"]],
                "ours_name": "",
                "reference_name": row["Name"],
                "birth_date": row["Date of Birth"],
                "match_basis": "reference-only row",
                "match_confidence": "HIGH",
                "scope_status": "ONLY_IN_REFERENCE",
                "notes": "No Sol identity has this exact birth date and compatible name.",
            }
        )
    return rows, lookup, only_reference


def adjudicated_death(person: dict[str, str]) -> str:
    if person["person_id"] == "p079_robert_a_rushworth":
        return "1993-03-18"
    return person["death_date"]


def source_urls(text: str) -> str:
    return "|".join(re.findall(r"https?://[^;\\s]+", text or ""))


def make_row_differences(
    ours: list[dict[str, str]],
    lookup: dict[str, dict[str, str]],
    only_reference: list[dict[str, str]],
    events: dict[str, dict[str, str]],
) -> list[dict]:
    rows: list[dict] = []

    def add(**kwargs) -> None:
        rows.append(
            {
                "reconciliation_row_id": f"DIFF{len(rows)+1:03d}",
                "ours_person_id": "",
                "reference_person_id": "",
                "ours_name": "",
                "reference_name": "",
                "scope_status": "",
                "difference_category": "",
                "field": "",
                "ours_value": "",
                "reference_value": "",
                "adjudicated_value": "",
                "adjudication": "",
                "source_urls": "",
                "impact_on_harmonized_analysis": "",
                "notes": "",
                **kwargs,
            }
        )

    ref_ids = reference_id_map(list(lookup.values()) + only_reference)
    add(
        scope_status="ONLY_IN_YOURS_NONE",
        difference_category="definition_only_membership_difference",
        field="cohort_inclusion",
        adjudication="No Sol-only rows.",
        impact_on_harmonized_analysis="none",
        notes="Explicit zero-row scope record.",
    )
    add(
        scope_status="SUMMARY_NONE",
        difference_category="factual_membership_disagreement",
        field="cohort_inclusion",
        adjudication="No factual Apollo, NASA-group, Dyna-Soar, or MOL membership disagreement remained after definition alignment.",
        impact_on_harmonized_analysis="none",
        notes="Category retained explicitly even though its count is zero.",
    )

    for reference in sorted(only_reference, key=lambda x: x["Name"]):
        explanation = {
            "Iven Carl Kincheloe Jr.": "Selected for X-15 but never flew it; Sol required an actual X-15 flight.",
            "Alvin Swauger White": "Reference high-speed-pilot scope (XB-70), not an X-15 flown pilot.",
            "William Barton Bridgeman": "Reference high-speed-pilot scope (D-558-II), not an X-15 flown pilot.",
        }[reference["Name"]]
        add(
            reference_person_id=ref_ids[reference["Name"]],
            reference_name=reference["Name"],
            scope_status="ONLY_IN_REFERENCE",
            difference_category="definition_only_membership_difference",
            field="cohort_inclusion",
            ours_value="excluded by fixed actual-X-15-flight rule",
            reference_value=f"included in {reference['analysis_source_label']}",
            adjudicated_value="definition-specific; excluded from harmonized shared scope",
            adjudication=explanation,
            source_urls="https://www.nasa.gov/aeronautics/x-15/",
            impact_on_harmonized_analysis="excluded from shared scope",
            notes=reference["Missions Flown"],
        )

    reference_flag = {
        "military_x15": "military_x15",
        "military_dyna_soar": "military_dyna_soar",
        "military_mol": "military_mol",
    }
    program_sources = {
        "military_x15": "https://www.nasa.gov/aeronautics/x-15/",
        "military_dyna_soar": "https://repository.si.edu/bitstreams/43c20435-4d2a-4e72-bc24-4546bc6ef1f3/download|https://www.aflcmc.af.mil/Portals/13/DynaSoar.pdf",
        "military_mol": "https://www.nro.gov/news-media-featured-stories/news-media-archive/News-Article/Article/3227331/the-story-of-the-manned-orbiting-laboratory-part-two/",
    }
    for person in ours:
        reference = lookup[person["person_id"]]
        person_differences = 0
        if person["death_date"] != reference["Date of Death"]:
            person_differences += 1
            if person["person_id"] == "p079_robert_a_rushworth":
                adjudicated = "1993-03-18"
                decision = (
                    "USAF personnel index is more specific than NASA's conflicting image biography; "
                    "retain 1993-03-17 to 1993-03-18 as uncertainty."
                )
                urls = (
                    "https://www.nasa.gov/image-article/flight-research-pilots-38/|"
                    "https://www.af.mil/About-Us/Biographies/Biography-Search/?Page=54&Sort=TitleZ"
                )
                impact = "one comparator death moved one day; negligible RMST change"
            else:
                adjudicated = person["death_date"]
                decision = "Locked Tier-1 NASA Astronaut Fact Book controls over reference Wikipedia-derived date."
                urls = "https://www.nasa.gov/reference/astronaut-fact-book/"
                impact = "reference corrected by one day; harmonized analysis uses adjudicated Sol date"
            add(
                ours_person_id=person["person_id"],
                reference_person_id=ref_ids[reference["Name"]],
                ours_name=person["full_name"],
                reference_name=reference["Name"],
                scope_status="SHARED_CONFLICT",
                difference_category="birth_death_status_disagreement",
                field="death_date",
                ours_value=person["death_date"],
                reference_value=reference["Date of Death"],
                adjudicated_value=adjudicated,
                adjudication=decision,
                source_urls=urls,
                impact_on_harmonized_analysis=impact,
                notes="Birth date and vital status otherwise agree.",
            )
        for field, source_key in reference_flag.items():
            ours_value = int(person[field])
            reference_value = int(reference["analysis_source_key"] == source_key)
            if ours_value != reference_value:
                person_differences += 1
                add(
                    ours_person_id=person["person_id"],
                    reference_person_id=ref_ids[reference["Name"]],
                    ours_name=person["full_name"],
                    reference_name=reference["Name"],
                    scope_status="SHARED_CONFLICT",
                    difference_category="program_flag_disagreement",
                    field=field,
                    ours_value=ours_value,
                    reference_value=f"{reference_value} (exclusive analysis_source_key)",
                    adjudicated_value=ours_value,
                    adjudication=(
                        "Sol stores overlapping factual program history; the reference stores one mutually "
                        "exclusive source bucket. Reference narrative fields often document the same overlap."
                    ),
                    source_urls=program_sources[field],
                    impact_on_harmonized_analysis="none; harmonized primary groups use agreed Apollo/non-Apollo status",
                    notes=f"Reference source key: {reference['analysis_source_key']}.",
                )
        if person["person_id"] in events:
            sol = int(events[person["person_id"]]["detected_any_age_80_plus"])
            space_grandpa = int(reference["Space Grandpa"] == "Y")
            if sol != space_grandpa:
                person_differences += 1
                add(
                    ours_person_id=person["person_id"],
                    reference_person_id=ref_ids[reference["Name"]],
                    ours_name=person["full_name"],
                    reference_name=reference["Name"],
                    scope_status="SHARED_CONFLICT",
                    difference_category="public_evidence_endpoint_disagreement",
                    field="unrestricted_Sol_function_vs_Space_Grandpa",
                    ours_value=sol,
                    reference_value=space_grandpa,
                    adjudicated_value="NOT_COLLAPSED",
                    adjudication=(
                        "Definition/public-evidence ascertainment difference. Space Grandpa is retained under "
                        "its own rule; the locked Sol result is retained under the stricter dated, attributable, "
                        "substantive self-directed rule."
                    ),
                    source_urls=source_urls(reference["Space Grandpa Citation"]),
                    impact_on_harmonized_analysis="reported in separate side-by-side endpoint columns",
                    notes=reference["Space Grandpa Citation"],
                )
        if person_differences == 0:
            add(
                ours_person_id=person["person_id"],
                reference_person_id=ref_ids[reference["Name"]],
                ours_name=person["full_name"],
                reference_name=reference["Name"],
                scope_status="SHARED_EXACT",
                difference_category="exact_agreement",
                field="compared core row values",
                ours_value="match",
                reference_value="match",
                adjudicated_value="match",
                adjudication=(
                    "Apollo/non-Apollo membership, birth, death/status, exclusive program representation, "
                    "and—when age-80 eligible—the two encoded endpoint indicators agree."
                ),
                source_urls=person["membership_source_urls"],
                impact_on_harmonized_analysis="included in shared scope when eligible for the estimand",
                notes="Endpoint-indicator agreement does not make the two endpoint definitions equivalent.",
            )
    return rows


def result_row(
    domain: str,
    analysis: str,
    endpoint_rule: str,
    group_a: str,
    group_b: str,
    metric: str,
    estimate,
    ci_lower="",
    ci_upper="",
    p_value="",
    numerator_a="",
    denominator_a="",
    numerator_b="",
    denominator_b="",
    units="",
    method="",
    notes="",
) -> dict:
    def value(item):
        return f"{item:.9f}" if isinstance(item, float) else item

    return {
        "domain": domain,
        "analysis": analysis,
        "endpoint_rule": endpoint_rule,
        "group_a": group_a,
        "group_b": group_b,
        "metric": metric,
        "estimate": value(estimate),
        "ci_lower": value(ci_lower),
        "ci_upper": value(ci_upper),
        "p_value": value(p_value),
        "numerator_a": numerator_a,
        "denominator_a": denominator_a,
        "numerator_b": numerator_b,
        "denominator_b": denominator_b,
        "units": units,
        "method": method,
        "notes": notes,
    }


def initial_full_main() -> None:
    OUT.mkdir(exist_ok=True)
    hashes_before = {key: tree_aggregate(key) for key in LOCKED_TREE_EXPECTED}
    if hashes_before != LOCKED_TREE_EXPECTED:
        raise AssertionError(f"Locked input mismatch before analysis: {hashes_before}")
    blind_path = ROOT / "stage2/BLIND_CONCLUSION.md"
    corrected_path = (
        ROOT / "stage3/locked_supplement/stage2r/CORRECTED_CONCLUSION.md"
    )
    if sha256_file(blind_path) != BLIND_HASH or sha256_file(corrected_path) != CORRECTED_HASH:
        raise AssertionError("Locked conclusion hash mismatch")
    blind_text = blind_path.read_text(encoding="utf-8")
    corrected_text = corrected_path.read_text(encoding="utf-8")

    ours = read_csv(ROOT / "stage1/cohort.csv")
    reference = read_csv(
        ROOT / "stage3/reference/derived_cohorts/cohorts/all_astronauts.tsv", "\t"
    )
    corrected_events_list = read_csv(
        ROOT / "stage3/locked_supplement/stage2r/EVENT_AGE_TABLE.csv"
    )
    corrected_events = {row["person_id"]: row for row in corrected_events_list}
    mapping, lookup, only_reference = identity_map(ours, reference)
    write_csv(
        OUT / "IDENTITY_MAPPING.csv",
        [
            "mapping_id",
            "ours_person_id",
            "reference_person_id",
            "ours_name",
            "reference_name",
            "birth_date",
            "match_basis",
            "match_confidence",
            "scope_status",
            "notes",
        ],
        mapping,
    )

    differences = make_row_differences(
        ours, lookup, only_reference, corrected_events
    )
    difference_fields = [
        "reconciliation_row_id",
        "ours_person_id",
        "reference_person_id",
        "ours_name",
        "reference_name",
        "scope_status",
        "difference_category",
        "field",
        "ours_value",
        "reference_value",
        "adjudicated_value",
        "adjudication",
        "source_urls",
        "impact_on_harmonized_analysis",
        "notes",
    ]
    write_csv(OUT / "ROW_DIFFERENCES.csv", difference_fields, differences)

    shared_apollo = [
        person
        for person in ours
        if person["apollo_flew"] == "1"
        and lookup[person["person_id"]]["analysis_primary"] == "apollo"
    ]
    shared_other = [
        person
        for person in ours
        if person["other_all"] == "1"
        and lookup[person["person_id"]]["analysis_primary"] == "other"
    ]
    if len(shared_apollo) != 29 or len(shared_other) != 66:
        raise AssertionError("Unexpected harmonized shared groups")

    def landmark_record(person: dict[str, str]) -> tuple[float, int]:
        death = parse_date(adjudicated_death(person))
        endpoint = death if death and death <= CENSOR else CENSOR
        return years_between(LANDMARK, endpoint), int(death is not None and death <= CENSOR)

    apollo_landmark_people = [
        person
        for person in shared_apollo
        if not adjudicated_death(person)
        or parse_date(adjudicated_death(person)) >= LANDMARK
    ]
    other_landmark_people = [
        person
        for person in shared_other
        if not adjudicated_death(person)
        or parse_date(adjudicated_death(person)) >= LANDMARK
    ]
    apollo_landmark = [landmark_record(person) for person in apollo_landmark_people]
    other_landmark = [landmark_record(person) for person in other_landmark_people]
    rmst_a = km_rmst(apollo_landmark, HORIZON)
    rmst_o = km_rmst(other_landmark, HORIZON)
    rmst_diff, rmst_low, rmst_high = bootstrap_rmst_difference(
        apollo_landmark, other_landmark
    )

    results: list[dict] = []
    results.extend(
        [
            result_row(
                "SURVIVAL",
                "HARMONIZED_SHARED_SCOPE_1973_LANDMARK",
                "all_cause_survival",
                "APOLLO_FLEW",
                "",
                "risk_set_n",
                len(apollo_landmark),
                units="people",
                method="alive on 1973-01-01 under adjudicated shared-scope dates",
            ),
            result_row(
                "SURVIVAL",
                "HARMONIZED_SHARED_SCOPE_1973_LANDMARK",
                "all_cause_survival",
                "OTHER_SHARED",
                "",
                "risk_set_n",
                len(other_landmark),
                units="people",
                method="shared non-Apollo intersection; alive on 1973-01-01",
            ),
            result_row(
                "SURVIVAL",
                "HARMONIZED_SHARED_SCOPE_1973_LANDMARK",
                "all_cause_survival",
                "APOLLO_FLEW",
                "",
                "deaths_full_followup",
                sum(event for _, event in apollo_landmark),
                units="deaths",
            ),
            result_row(
                "SURVIVAL",
                "HARMONIZED_SHARED_SCOPE_1973_LANDMARK",
                "all_cause_survival",
                "OTHER_SHARED",
                "",
                "deaths_full_followup",
                sum(event for _, event in other_landmark),
                units="deaths",
            ),
            result_row(
                "SURVIVAL",
                "HARMONIZED_SHARED_SCOPE_1973_LANDMARK",
                "all_cause_survival",
                "APOLLO_FLEW",
                "",
                "rmst_50y",
                rmst_a,
                units="years",
                method="Kaplan-Meier integral through 50 years",
            ),
            result_row(
                "SURVIVAL",
                "HARMONIZED_SHARED_SCOPE_1973_LANDMARK",
                "all_cause_survival",
                "OTHER_SHARED",
                "",
                "rmst_50y",
                rmst_o,
                units="years",
                method="Kaplan-Meier integral through 50 years",
            ),
            result_row(
                "SURVIVAL",
                "HARMONIZED_SHARED_SCOPE_1973_LANDMARK",
                "all_cause_survival",
                "APOLLO_FLEW",
                "OTHER_SHARED",
                "rmst_difference",
                rmst_diff,
                rmst_low,
                rmst_high,
                units="years",
                method="50,000-replicate stratified percentile bootstrap; seed 20260721",
                notes="Apollo minus shared Other; prespecified locked estimand.",
            ),
            result_row(
                "SURVIVAL",
                "LOCKED_STAGE2_AUDIT_HISTORY",
                "all_cause_survival",
                "APOLLO_FLEW",
                "OTHER_ALL",
                "rmst_difference",
                0.670080,
                -5.088212,
                6.098918,
                units="years",
                method="locked Stage 2 result; preserved, not recomputed",
                notes="Difference from harmonized value is only one-day Rushworth adjudication.",
            ),
        ]
    )

    # Faithful archived reference-style age-30 quantities on harmonized shared rows.
    life = LifeTable(
        read_csv(
            ROOT
            / "stage3/reference/reference_population/ssa-1930-male-cohort-lifetable.tsv",
            "\t",
        )
    )

    def birth_record(person: dict[str, str]) -> tuple[float, int]:
        birth = parse_date(person["birth_date"])
        death = parse_date(adjudicated_death(person))
        endpoint = death if death and death <= CENSOR else CENSOR
        return years_between(birth, endpoint), int(death is not None and death <= CENSOR)

    birth_groups = {
        "APOLLO_FLEW": [birth_record(person) for person in shared_apollo],
        "OTHER_SHARED": [birth_record(person) for person in shared_other],
    }
    for group, records in birth_groups.items():
        observed = sum(event for _, event in records)
        expected = life.expected_events([time for time, _ in records])
        smr = observed / expected
        factor = math.exp(Z975 / math.sqrt(observed))
        results.append(
            result_row(
                "SURVIVAL",
                "REFERENCE_STYLE_AGE30_SHARED_SCOPE",
                "all_cause_survival",
                group,
                "SSA_1930_MALE_CONDITIONAL_AGE30",
                "smr",
                smr,
                smr / factor,
                smr * factor,
                numerator_a=observed,
                denominator_a=len(records),
                units="ratio",
                method="archived reference cumulative-hazard SMR with log-approximate interval",
                notes="Different estimand; single 1930 male cohort table used for all birth years.",
            )
        )
        for attained_age in (80.0, 90.0):
            estimate, lower, upper = km_at(records, attained_age)
            results.append(
                result_row(
                    "SURVIVAL",
                    "REFERENCE_STYLE_AGE30_SHARED_SCOPE",
                    "all_cause_survival",
                    group,
                    "",
                    f"km_survival_to_age_{int(attained_age)}",
                    estimate,
                    lower,
                    upper,
                    units="probability",
                    method="retrospective Kaplan-Meier from age 30; log-log Greenwood interval",
                )
            )
    observed_a, expected_a, logrank_z, logrank_p = logrank_test(
        birth_groups["APOLLO_FLEW"], birth_groups["OTHER_SHARED"]
    )
    results.append(
        result_row(
            "SURVIVAL",
            "REFERENCE_STYLE_AGE30_SHARED_SCOPE",
            "all_cause_survival",
            "APOLLO_FLEW",
            "OTHER_SHARED",
            "logrank_test",
            logrank_z,
            p_value=logrank_p,
            units="z",
            method="archived reference log-rank implementation",
            notes=f"Apollo observed test events={observed_a:.1f}; expected={expected_a:.9f}.",
        )
    )

    # Shared age-80 risk set and side-by-side, non-collapsed endpoint rules.
    eligible = []
    for person in ours:
        if person["person_id"] not in corrected_events:
            continue
        reference_person = lookup[person["person_id"]]
        eligible.append(
            {
                "person_id": person["person_id"],
                "full_name": person["full_name"],
                "group": "APOLLO_FLEW"
                if person["apollo_flew"] == "1"
                else "OTHER_SHARED",
                "sol_detected": int(
                    corrected_events[person["person_id"]][
                        "detected_any_age_80_plus"
                    ]
                ),
                "space_grandpa": int(reference_person["Space Grandpa"] == "Y"),
            }
        )
    if Counter(row["group"] for row in eligible) != Counter(
        {"APOLLO_FLEW": 22, "OTHER_SHARED": 35}
    ):
        raise AssertionError("Unexpected shared age-80 risk set")

    crosstab_rows = []
    for group in ("ALL_SHARED", "APOLLO_FLEW", "OTHER_SHARED"):
        rows = eligible if group == "ALL_SHARED" else [
            row for row in eligible if row["group"] == group
        ]
        for sol in (0, 1):
            for sg in (0, 1):
                persons = [
                    row for row in rows
                    if row["sol_detected"] == sol and row["space_grandpa"] == sg
                ]
                crosstab_rows.append(
                    {
                        "group": group,
                        "sol_qualifying_function": sol,
                        "reference_space_grandpa": sg,
                        "count": len(persons),
                        "person_ids": "|".join(row["person_id"] for row in persons),
                    }
                )
    write_csv(
        OUT / "PUBLIC_FUNCTION_CROSSTAB.csv",
        [
            "group",
            "sol_qualifying_function",
            "reference_space_grandpa",
            "count",
            "person_ids",
        ],
        crosstab_rows,
    )

    endpoint_counts = {}
    for endpoint, field in (
        ("SOL_CORRECTED_UNRESTRICTED_AGE80_PLUS", "sol_detected"),
        ("REFERENCE_SPACE_GRANDPA", "space_grandpa"),
    ):
        a = [row for row in eligible if row["group"] == "APOLLO_FLEW"]
        b = [row for row in eligible if row["group"] == "OTHER_SHARED"]
        ay, by = sum(row[field] for row in a), sum(row[field] for row in b)
        endpoint_counts[endpoint] = (ay, len(a), by, len(b))
        for group, numerator, denominator in (
            ("APOLLO_FLEW", ay, len(a)),
            ("OTHER_SHARED", by, len(b)),
        ):
            low, high = clopper_pearson(numerator, denominator)
            results.append(
                result_row(
                    "PUBLIC_FUNCTION",
                    "HARMONIZED_SHARED_AGE80_RISK_SET",
                    endpoint,
                    group,
                    "",
                    "detected_risk",
                    numerator / denominator,
                    low,
                    high,
                    numerator_a=numerator,
                    denominator_a=denominator,
                    units="probability",
                    method="exact Clopper-Pearson interval",
                )
            )
        difference, low, high = newcombe_difference(ay, len(a), by, len(b))
        fisher = fisher_exact_two_sided(ay, len(a) - ay, by, len(b) - by)
        results.append(
            result_row(
                "PUBLIC_FUNCTION",
                "HARMONIZED_SHARED_AGE80_RISK_SET",
                endpoint,
                "APOLLO_FLEW",
                "OTHER_SHARED",
                "risk_difference",
                difference,
                low,
                high,
                p_value=fisher,
                numerator_a=ay,
                denominator_a=len(a),
                numerator_b=by,
                denominator_b=len(b),
                units="probability",
                method="Newcombe method 10 interval; Fisher exact p-value",
                notes="Apollo minus shared Other.",
            )
        )
        boot_point, boot_low, boot_high = bootstrap_binary_difference(
            ay, len(a), by, len(b)
        )
        results.append(
            result_row(
                "PUBLIC_FUNCTION",
                "HARMONIZED_SHARED_AGE80_RISK_SET",
                endpoint,
                "APOLLO_FLEW",
                "OTHER_SHARED",
                "risk_difference_bootstrap",
                boot_point,
                boot_low,
                boot_high,
                numerator_a=ay,
                denominator_a=len(a),
                numerator_b=by,
                denominator_b=len(b),
                units="probability",
                method="50,000-replicate stratified percentile bootstrap; seed 20260721",
            )
        )
    all_cross = Counter(
        (row["sol_detected"], row["space_grandpa"]) for row in eligible
    )
    for sol in (0, 1):
        for sg in (0, 1):
            count = all_cross[(sol, sg)]
            results.append(
                result_row(
                    "PUBLIC_FUNCTION",
                    "HARMONIZED_SHARED_AGE80_CROSSTAB",
                    "SOL_RULE_X_REFERENCE_RULE",
                    "ALL_SHARED",
                    "",
                    f"count_sol{sol}_space_grandpa{sg}",
                    count,
                    units="people",
                    method="same 57-person shared age-80 risk set",
                )
            )
    results.extend(
        [
            result_row(
                "PUBLIC_FUNCTION",
                "LOCKED_STAGE2R_OPERATIVE_RESULT",
                "SOL_CORRECTED_UNRESTRICTED_AGE80_PLUS",
                "APOLLO_FLEW",
                "OTHER_ALL",
                "risk_difference",
                0.079220779,
                -0.077370641,
                0.280496015,
                numerator_a=3,
                denominator_a=22,
                numerator_b=2,
                denominator_b=35,
                units="probability",
                method="locked corrected Stage 2R result; preserved verbatim",
                notes="Identical to harmonized Sol-rule shared scope.",
            ),
            result_row(
                "PUBLIC_FUNCTION",
                "REFERENCE_ARCHIVED_ORIGINAL_SCOPE",
                "REFERENCE_SPACE_GRANDPA",
                "APOLLO",
                "REFERENCE_OTHER_ALL",
                "risk_difference",
                0.287878788,
                p_value=0.011070210,
                numerator_a=21,
                denominator_a=22,
                numerator_b=24,
                denominator_b=36,
                units="probability",
                method="archived reference result",
                notes="Full reference scope; includes reference-only Alvin White in the age-80 comparator.",
            ),
        ]
    )

    result_fields = [
        "domain",
        "analysis",
        "endpoint_rule",
        "group_a",
        "group_b",
        "metric",
        "estimate",
        "ci_lower",
        "ci_upper",
        "p_value",
        "numerator_a",
        "denominator_a",
        "numerator_b",
        "denominator_b",
        "units",
        "method",
        "notes",
    ]
    write_csv(OUT / "HARMONIZED_RESULTS.csv", result_fields, results)

    # Authorized live-source log; no other web access occurred.
    source_rows = [
        {
            "timestamp": "2026-07-23T08:28:38Z",
            "query_or_direct_navigation": "site:nasa.gov Robert A. Rushworth March 1993",
            "result_rank": "",
            "url": "",
            "opened": 0,
            "access_result": "search completed",
            "fact_supported": "death-date adjudication lead",
            "source_tier": "official-only query",
            "adjudication_role": "genuine one-day date conflict",
            "notes": "No comparative, mortality-analysis, aging, cognition, or commentary source opened.",
        },
        {
            "timestamp": "2026-07-23T08:28:38Z",
            "query_or_direct_navigation": "site:af.mil Robert Rushworth obituary March 1993",
            "result_rank": "",
            "url": "",
            "opened": 0,
            "access_result": "search completed",
            "fact_supported": "death-date adjudication lead",
            "source_tier": "official-only query",
            "adjudication_role": "genuine one-day date conflict",
            "notes": "No comparative, mortality-analysis, aging, cognition, or commentary source opened.",
        },
        {
            "timestamp": "2026-07-23T08:29:06Z",
            "query_or_direct_navigation": "opened search result",
            "result_rank": "tool_ref_search0",
            "url": "https://www.nasa.gov/image-article/flight-research-pilots-38/",
            "opened": 1,
            "access_result": "fetched",
            "fact_supported": "Robert Rushworth death date 1993-03-17",
            "source_tier": "Tier 1 official NASA",
            "adjudication_role": "conflicting official date retained as uncertainty bound",
            "notes": "Individual flight-research biography.",
        },
        {
            "timestamp": "2026-07-23T08:29:06Z",
            "query_or_direct_navigation": "opened search result",
            "result_rank": "tool_ref_search2",
            "url": "https://www.af.mil/About-Us/Biographies/Biography-Search/?Page=54&Sort=TitleZ",
            "opened": 1,
            "access_result": "fetched",
            "fact_supported": "Robert Rushworth death date 1993-03-18",
            "source_tier": "Tier 1 official USAF",
            "adjudication_role": "controlling specific personnel-index date",
            "notes": "More specific service personnel source; harmonized date 1993-03-18.",
        },
        {
            "timestamp": "2026-07-23T08:29:06Z",
            "query_or_direct_navigation": "opened search result",
            "result_rank": "tool_ref_search6",
            "url": "https://www.af.mil/About-Us/Biographies/Display/Article/105742/major-general-robert-a-rushworth/",
            "opened": 1,
            "access_result": "fetched; no death date",
            "fact_supported": "identity and X-15 career only",
            "source_tier": "Tier 1 official USAF",
            "adjudication_role": "identity corroboration; noninformative for date",
            "notes": "Biography text is current as of August 1980.",
        },
    ]
    write_csv(
        OUT / "SOURCE_LOG.csv",
        [
            "timestamp",
            "query_or_direct_navigation",
            "result_rank",
            "url",
            "opened",
            "access_result",
            "fact_supported",
            "source_tier",
            "adjudication_role",
            "notes",
        ],
        source_rows,
    )

    # Verify every copied approved file against the controller manifest.
    manifest = read_csv(ROOT / "stage3/reference/STAGE3_REFERENCE_MANIFEST.csv")
    manifest_rows = []
    for row in manifest:
        runtime_path = ROOT / row["runtime_path"]
        actual = sha256_file(runtime_path)
        manifest_rows.append(
            {
                "runtime_path": row["runtime_path"],
                "manifest_sha256": row["runtime_sha256"],
                "actual_sha256": actual,
                "match": int(actual == row["runtime_sha256"]),
            }
        )
    write_csv(
        OUT / "REFERENCE_MANIFEST_VALIDATION.csv",
        ["runtime_path", "manifest_sha256", "actual_sha256", "match"],
        manifest_rows,
    )
    if not all(row["match"] for row in manifest_rows):
        raise AssertionError("Reference manifest hash failure")

    # Narrative reconciliation.
    categories = Counter(row["difference_category"] for row in differences)
    sol_counts = endpoint_counts["SOL_CORRECTED_UNRESTRICTED_AGE80_PLUS"]
    sg_counts = endpoint_counts["REFERENCE_SPACE_GRANDPA"]
    report = f"""# Stage 3 Post-lock Reconciliation

This is a labeled reconciliation. It does not edit or replace any locked Stage 1, Stage 1B, Stage 1C, Stage 2, reference-bundle, or Stage 2R correction file. The operative Sol public-function endpoint is the corrected unrestricted any-age-80-plus endpoint; the rejected five-year quantity is retained only in locked audit history and is not recomputed here.

## Executive reconciliation

- **Identity/shared scope:** all 95 Sol people map conservatively to reference rows. The reference has three additional high-speed-pilot rows. There are no Sol-only rows.
- **Apollo:** both constructions contain the same 29 Apollo 7–17 flyers.
- **Primary survival estimand:** on the harmonized shared scope, the 1973-landmark 50-year RMST contrast is **{rmst_diff:+.3f} years** (95% percentile-bootstrap interval {rmst_low:+.3f} to {rmst_high:+.3f}). This is effectively identical to the locked +0.670-year result and remains far below the fixed 5-year materiality threshold.
- **Operative Sol public-function rule:** {sol_counts[0]}/{sol_counts[1]} versus {sol_counts[2]}/{sol_counts[3]}, risk difference **{newcombe_difference(*sol_counts)[0]*100:+.1f} percentage points** (95% Newcombe interval {newcombe_difference(*sol_counts)[1]*100:+.1f} to {newcombe_difference(*sol_counts)[2]*100:+.1f}). This is identical to locked Stage 2R.
- **Reference Space Grandpa rule on the same people:** {sg_counts[0]}/{sg_counts[1]} versus {sg_counts[2]}/{sg_counts[3]}, risk difference **{newcombe_difference(*sg_counts)[0]*100:+.1f} percentage points** (95% Newcombe interval {newcombe_difference(*sg_counts)[1]*100:+.1f} to {newcombe_difference(*sg_counts)[2]*100:+.1f}; Fisher p={fisher_exact_two_sided(sg_counts[0],sg_counts[1]-sg_counts[0],sg_counts[2],sg_counts[3]-sg_counts[2]):.4f}).
- **Endpoint cross-tab:** among 57 shared people who reached 80, Sol+/Space-Grandpa+ = 5, Sol+/Space-Grandpa− = 0, Sol−/Space-Grandpa+ = 40, and both negative = 12.

The reference comparison therefore **weakens the broad, endpoint-agnostic “no anomaly” reading but does not overturn either locked estimand-specific classification**. Survival remains `NOT_DETECTED / HIGHER`; the corrected unrestricted Sol public-detection endpoint remains `NOT_DETECTED / HIGHER`. The broader Space Grandpa field produces a materially larger contrast, demonstrating endpoint/ascertainment sensitivity rather than proving that one construct is the other.

## Pass 1 — Definition-level comparison

| Component | Sol locked definition | Reference construction | Reconciliation |
|---|---|---|---|
| Apollo | Physically launched prime crew on Apollo 7–17; Apollo 1, Skylab, and ASTP are not treatment flights. | Rows loaded from lunar and Apollo 7/9 non-lunar enriched files. | Exact same 29 people. |
| NASA boundary | Top-down NASA groups 1–7, including never-flew, resigned, medically disqualified, or preflight-death members; non-Apollo members are comparators. | File-defined `other_core_nasa` set of 44. | Row set agrees exactly, although the archived reference code delegates the boundary to its upstream file instead of restating it. |
| X-15 | Exactly 12 people who actually flew the X-15. | Mutually exclusive `X-15/high-speed pilots` source bucket; reference-wide scope also includes three other high-speed pilots. | Three reference-only rows are definition-only additions. Shared factual X-15 history agrees once overlap is reconstructed. |
| Dyna-Soar | Six selected-to-fly people; Armstrong and Dana excluded as support personnel. | Four rows have the exclusive Dyna-Soar source key; Knight and Thompson are stored under X-15. | Underlying six shared identities agree; exclusive source-key representation loses two overlap flags. |
| MOL | All 17 selected crewmembers, including seven NASA transfers. | Eight rows have the exclusive MOL source key; nine overlapping members are stored in NASA/X-15/Dyna-Soar buckets. | Underlying 17 shared identities agree; source-key representation loses nine overlap flags. |
| Deduplication | One person row with overlapping binary program flags. | One person row with one mutually exclusive primary/source key. | Both deduplicate people, but only Sol preserves all overlaps as flags. |
| `OTHER_ALL` | Non-Apollo union after person-level deduplication. | All rows with reference primary `other`. | 66 versus 69; the three-row difference is the broader high-speed scope. |
| Accidental deaths | External accidental death before 1970, retained in `OTHER_ALL` and flagged. | Same operational date/cause concept; 14 reference rows. | Twelve shared flags agree; two additional flags belong to reference-only Bridgeman and Kincheloe. |
| Backup crews | Recorded as rotations; never an untreated control. | No equivalent analytical field. | Not comparable; no reference contradiction. |
| Public function | Dated, attributable, substantive self-directed activity under frozen tiers/date rules; unrestricted endpoint uses any qualifying event at age 80+. | `Space Grandpa`: publicly documented late-life activity at 80+, assembled through heterogeneous narrative citations. | Related but non-equivalent. Neither field is a clinical cognitive diagnosis. |

Primary roster anchors used for adjudication were already fetched in Stage 1: NASA Apollo missions and astronaut groups, NASA's 12 flown X-15 pilots, Smithsonian/USAF Dyna-Soar histories, and the NRO MOL roster. The reference bundle is approved comparison material, but approval was not treated as factual authority.

## Pass 2 — Row-level reconciliation

### Identity and membership

Exact birth date plus compatible identity mapped 95/95 Sol rows; only the Stafford/Mitchell shared-birthday collision required surname resolution. Name-only fuzzy matching was never used. `IDENTITY_MAPPING.csv` retains every original name and mapping basis.

The reference-only rows are:

1. William Barton Bridgeman — D-558-II high-speed pilot, not an X-15 flown pilot;
2. Alvin Swauger White — XB-70 high-speed pilot, not an X-15 flown pilot;
3. Iven Carl Kincheloe Jr. — selected for X-15 but died before flying it.

These are coherent under the reference's broader `X-15/high-speed` scope and excluded under Sol's fixed actual-X-15-flight rule. They are definition-only differences, not silent omissions. There are **zero factual Apollo/NASA/Dyna-Soar/MOL membership disagreements** after applying the primary rosters.

### Dates and status

Birth dates and 2026-06-01 vital status agree for every shared person. Three death dates differ by one day:

- Donn Eisele: Sol/NASA Fact Book `1987-12-02`; reference `1987-12-01`. Harmonized value: `1987-12-02`.
- Ronald Evans: Sol/NASA Fact Book `1990-04-07`; reference `1990-04-06`. Harmonized value: `1990-04-07`.
- Robert Rushworth: Sol and a NASA page say `1993-03-17`; the USAF personnel index and reference say `1993-03-18`. The more specific USAF personnel record controls, with the one-day official-source conflict retained as uncertainty.

Thus Rushworth's death date is a correction to Sol's prior row, reported only here. Eisele and Evans are corrections to reference rows. None changes landmark eligibility, age-80 eligibility, vital status, or substantive conclusions.

### Program flags

There are {categories['program_flag_disagreement']} shared flag/source-key differences: two X-15, two Dyna-Soar, and nine MOL. Every one arises because the reference assigns one mutually exclusive source key while Sol records overlapping factual history. The reference narrative itself identifies many overlaps. Harmonization retains agreed person membership and does not reinterpret an exclusive source key as a factual zero.

### Public-evidence rows

There are {categories['public_evidence_endpoint_disagreement']} indicator disagreements on the shared age-80 risk set. All five Sol detections are Space Grandpa positive. Forty additional people are Space Grandpa positive but Sol negative. The reference notes span substantive-looking interviews, testimony, piloting, authorship, and roles, but also awards, attendance, ceremonies, generic “active” descriptions, and other evidence that does not alone satisfy the frozen Sol event/date rules. Reference notes do not uniformly retain Sol's event date, precision bounds, directness, source tier, and contemporaneous-participation fields.

Accordingly:

- Space Grandpa positives were not automatically promoted into Sol events.
- Sol negatives were not interpreted as impairment.
- The discrepancy is classified as definition/public-evidence ascertainment unless a row has separately adjudicated factual conflict.
- No endpoint was collapsed into a synthetic consensus label.

`ROW_DIFFERENCES.csv` includes {len(differences)} auditable rows: explicit reference-only entries, zero-row sentinels for Sol-only and factual-membership disagreements, all date and flag conflicts, every endpoint disagreement, and exact-agreement rows.

## Pass 3 — Harmonized shared-scope analyses

### Survival

The harmonized rule requires a person to be present in both constructions and classified as Apollo by both or non-Apollo `OTHER_ALL` by both. It yields 29 Apollo and 66 other people before landmarking; 29 and 53 are alive on 1973-01-01. The 50-year RMSTs are {rmst_a:.3f} and {rmst_o:.3f} years.

The harmonized Apollo-minus-other effect is {rmst_diff:+.3f} years (95% interval {rmst_low:+.3f}, {rmst_high:+.3f}). The locked result was +0.670 years (−5.088, +6.099). The tiny numerical change is the Rushworth one-day adjudication. The reference-only Bridgeman and Kincheloe died before the landmark; Alvin White is excluded by shared-scope harmonization. No material survival conclusion changes.

The archived reference's age-30 analysis can be faithfully reproduced on the shared rows and is reported separately, never substituted for RMST:

- Apollo SMR versus the SSA 1930 male table: {results[8]['estimate']} ({results[8]['ci_lower']}, {results[8]['ci_upper']});
- shared Other SMR: {results[11]['estimate']} ({results[11]['ci_lower']}, {results[11]['ci_upper']});
- KM survival to age 80: 0.7586 versus 0.5303; to age 90: 0.4483 versus 0.2640;
- Apollo-versus-other age-origin log-rank p={logrank_p:.4f}.

These quantities show that both occupationally selected groups outlive a general-population table. They are retrospective, use a single 1930 male cohort table for people born across multiple years, and are vulnerable to healthy-selectee and future-membership selection. They do not establish a causal Apollo effect and do not replace the near-zero common-landmark RMST contrast.

### Publicly documented late-life functioning

The same shared age-80 risk set is used for both rules: 22 Apollo and 35 shared Other.

| Rule | Apollo | Shared Other | Apollo-minus-other RD | 95% Newcombe CI |
|---|---:|---:|---:|---:|
| Corrected unrestricted Sol qualifying-function detection | {sol_counts[0]}/{sol_counts[1]} | {sol_counts[2]}/{sol_counts[3]} | {newcombe_difference(*sol_counts)[0]*100:+.1f} pp | {newcombe_difference(*sol_counts)[1]*100:+.1f} to {newcombe_difference(*sol_counts)[2]*100:+.1f} pp |
| Reference Space Grandpa | {sg_counts[0]}/{sg_counts[1]} | {sg_counts[2]}/{sg_counts[3]} | {newcombe_difference(*sg_counts)[0]*100:+.1f} pp | {newcombe_difference(*sg_counts)[1]*100:+.1f} to {newcombe_difference(*sg_counts)[2]*100:+.1f} pp |

The full reference result was 21/22 versus 24/36 (+28.8 pp, Fisher p=0.0111). Restricting to shared scope removes Alvin White, a reference-only Space-Grandpa-negative comparator, so the comparator becomes 24/35 and the difference attenuates to +26.9 pp (Fisher p=0.0193). The corrected Sol result is unchanged because every Sol person is shared.

The contrast between +7.9 pp and +26.9 pp is evidence of construct and ascertainment sensitivity. It is not a validation of clinical cognition, and the larger reference quantity is not substituted for the locked Sol endpoint.

## Implementation and analysis differences

- Sol's primary survival estimand is a 1973 common-landmark 50-year RMST difference with stratified bootstrap uncertainty; the reference foregrounds age-origin KM/log-rank, SMR, and simulations.
- The reference analysis date is 2026-06-04; harmonization uses the fixed Sol censor 2026-06-01. No death lies in the three-day gap.
- The reference's primary source key is mutually exclusive; Sol program flags overlap.
- Reference `OTHER_AVAILABLE` removes pre-1970 accidental deaths. Sol's primary comparator is `OTHER_ALL`; after the 1973 landmark, those early accidental deaths are absent by construction.
- The reference age-30 SMR applies one 1930 cohort life table across the entire astronaut birth-year range and uses a log-approximate SMR interval. It is faithfully labeled as reference-style, not treated as Sol's prespecified effect.
- The reference's Fisher test for Space Grandpa and Sol's corrected Newcombe/bootstrap summaries answer different public-evidence questions.

## Corrections to prior constructions

- **Correction to Sol, reported only here:** Robert Rushworth's harmonized death date is 1993-03-18, with an official NASA/USAF one-day conflict retained.
- **Corrections to reference for harmonization:** Donn Eisele is 1987-12-02 and Ronald Evans is 1990-04-07, based on the official NASA Astronaut Fact Book.
- **No Sol membership correction:** the three reference-only people reflect the reference's broader high-speed-pilot definition.
- **No automatic Sol event correction:** Space Grandpa disagreements remain side-by-side endpoint/ascertainment differences.

## Narrow post-lock interpretation

The harmonized comparison leaves the survival classification unchanged and leaves the operative corrected Sol public-function classification unchanged. It weakens only the broad claim that there is no possible descriptive anomaly under any reasonable public-activity construct, because the broader Space Grandpa field shows a larger shared-set difference. The defensible statement is therefore endpoint-specific: **no anomaly is detected by the locked RMST or corrected Sol qualifying-function rules; a broader reference late-life-activity proxy does show a positive disparity that cannot be equated with the Sol endpoint or clinical cognition.**

## Locked conclusions preserved verbatim

`stage2/BLIND_CONCLUSION.md` — SHA-256 `{BLIND_HASH}`:

```text
{blind_text.rstrip()}
```

`stage3/locked_supplement/stage2r/CORRECTED_CONCLUSION.md` — SHA-256 `{CORRECTED_HASH}`:

```text
{corrected_text.rstrip()}
```
"""
    (OUT / "RECONCILIATION.md").write_text(report, encoding="utf-8")

    contamination = """# Stage 3 Contamination Record

The approved reference bundle explicitly contains comparative mortality, survival, and late-life-vitality analysis. Reading it was authorized for this labeled reconciliation and is not treated as an accidental contamination encounter.

Live web access was limited to two official-domain queries and three official NASA/USAF person-level biography/index pages for the genuinely disputed Robert Rushworth death date. No live mortality, aging, cognition, cohort-comparison, statistical-analysis, or commentary page was opened. The searches returned no prohibited result that required a contamination encounter entry.

No parent or sibling project directory was read.
"""
    (OUT / "CONTAMINATION.md").write_text(contamination, encoding="utf-8")

    hashes_after = {key: tree_aggregate(key) for key in LOCKED_TREE_EXPECTED}
    if hashes_after != hashes_before:
        raise AssertionError("Locked input changed during analysis")
    locked_hash_rows = [
        {
            "locked_path": key,
            "expected_aggregate_sha256": LOCKED_TREE_EXPECTED[key],
            "sha256_before": hashes_before[key],
            "sha256_after": hashes_after[key],
            "unchanged": int(
                hashes_before[key] == hashes_after[key] == LOCKED_TREE_EXPECTED[key]
            ),
        }
        for key in LOCKED_TREE_EXPECTED
    ]
    locked_hash_rows.extend(
        [
            {
                "locked_path": "stage2/BLIND_CONCLUSION.md",
                "expected_aggregate_sha256": BLIND_HASH,
                "sha256_before": sha256_file(blind_path),
                "sha256_after": sha256_file(blind_path),
                "unchanged": 1,
            },
            {
                "locked_path": "stage3/locked_supplement/stage2r/CORRECTED_CONCLUSION.md",
                "expected_aggregate_sha256": CORRECTED_HASH,
                "sha256_before": sha256_file(corrected_path),
                "sha256_after": sha256_file(corrected_path),
                "unchanged": 1,
            },
        ]
    )
    write_csv(
        OUT / "LOCKED_INPUT_HASHES.csv",
        [
            "locked_path",
            "expected_aggregate_sha256",
            "sha256_before",
            "sha256_after",
            "unchanged",
        ],
        locked_hash_rows,
    )

    validations = [
        ("All six locked tree aggregates match pre-analysis baselines", hashes_after == LOCKED_TREE_EXPECTED),
        ("Both locked conclusion hashes match", sha256_file(blind_path) == BLIND_HASH and sha256_file(corrected_path) == CORRECTED_HASH),
        ("Every approved reference-manifest file matches", all(row["match"] for row in manifest_rows)),
        ("All 95 Sol rows map uniquely", len(lookup) == 95 and len(set(row["Name"] for row in lookup.values())) == 95),
        ("Reference-only rows equal three and Sol-only rows equal zero", len(only_reference) == 3),
        ("Shared Apollo classifications agree", len(shared_apollo) == 29),
        ("Harmonized shared Other scope equals 66", len(shared_other) == 66),
        ("1973 landmark risk sets equal 29 and 53", len(apollo_landmark) == 29 and len(other_landmark) == 53),
        ("Bootstrap uses 50,000 replicates and seed 20260721", BOOTSTRAP_REPLICATES == 50_000 and BOOTSTRAP_SEED == 20260721),
        ("Death-date disagreements equal three", categories["birth_death_status_disagreement"] == 3),
        ("Program representation disagreements equal thirteen", categories["program_flag_disagreement"] == 13),
        ("No factual membership disagreement remains", sum(row["scope_status"] != "SUMMARY_NONE" and row["difference_category"] == "factual_membership_disagreement" for row in differences) == 0),
        ("Shared age-80 risk set equals 22 Apollo plus 35 Other", len(eligible) == 57 and sol_counts[1] == 22 and sol_counts[3] == 35),
        ("Corrected Sol unrestricted counts equal locked Stage 2R", sol_counts == (3, 22, 2, 35)),
        ("Every Sol detection is Space Grandpa positive", all(not row["sol_detected"] or row["space_grandpa"] for row in eligible)),
        ("Public-function crosstab sums to 57", sum(all_cross.values()) == 57),
        ("No stale five-year endpoint appears in harmonized results", all("FIVE_YEAR" not in "|".join(str(value) for value in row.values()).upper() for row in results)),
        ("Results keep Sol and Space Grandpa endpoint labels separate", {row["endpoint_rule"] for row in results if row["domain"] == "PUBLIC_FUNCTION"} >= {"SOL_CORRECTED_UNRESTRICTED_AGE80_PLUS", "REFERENCE_SPACE_GRANDPA"}),
        ("No locked file was written by this script", hashes_after == hashes_before),
    ]
    if not all(passed for _, passed in validations):
        raise AssertionError([name for name, passed in validations if not passed])
    validation_text = "# Stage 3 Validation\n\nOverall: **PASS**.\n\n"
    validation_text += "| Check | Result |\n|---|---|\n"
    validation_text += "\n".join(
        f"| {name} | {'PASS' if passed else 'FAIL'} |" for name, passed in validations
    )
    validation_text += (
        "\n\nThe original blind conclusion and corrected conclusion were read and quoted "
        "verbatim; neither was regenerated. No rejected five-year public-function estimate "
        "was recomputed or presented as primary.\n"
    )
    (OUT / "VALIDATION.md").write_text(validation_text, encoding="utf-8")

    artifacts = [
        "stage3/RECONCILIATION.md",
        "stage3/ROW_DIFFERENCES.csv",
        "stage3/HARMONIZED_RESULTS.csv",
        "stage3/CONTAMINATION.md",
        "stage3/STAGE_COMPLETE.md",
        "stage3/SOURCE_LOG.csv",
        "stage3/analysis.py",
        "stage3/validate.py",
        "stage3/VALIDATION.md",
        "stage3/IDENTITY_MAPPING.csv",
        "stage3/PUBLIC_FUNCTION_CROSSTAB.csv",
        "stage3/LOCKED_INPUT_HASHES.csv",
        "stage3/REFERENCE_MANIFEST_VALIDATION.csv",
    ]
    completion = f"""# Stage 3 Complete

Status: **COMPLETE**.

## Artifacts

{chr(10).join(f'- `{path}`' for path in artifacts)}

## Integrity

All locked Stage 1, Stage 1B, Stage 1C, Stage 2, approved reference, and locked Stage 2R trees match their pre-analysis aggregate hashes. `stage2/BLIND_CONCLUSION.md` remains `{BLIND_HASH}`; `stage3/locked_supplement/stage2r/CORRECTED_CONCLUSION.md` remains `{CORRECTED_HASH}`.

## Narrow post-lock answer

The reference comparison **weakens, but does not overturn, the broad locked “no anomaly” conclusion**. The shared-scope 1973-landmark RMST result is effectively unchanged and remains non-material with a null-crossing interval. The operative corrected unrestricted Sol public-function result is also unchanged. However, the broader reference Space Grandpa rule produces a materially larger positive shared-set disparity, showing that the public-function answer is sensitive to endpoint breadth and ascertainment. That broader proxy is not the locked Sol qualifying-function endpoint and is not a clinical cognitive measure.

No locked conclusion was rewritten. No blocking failure remains.
"""
    (OUT / "STAGE_COMPLETE.md").write_text(completion, encoding="utf-8")


DEV_ID = "DEV-20260723-13"
DEV_START = "<!-- DEV-20260723-13 START -->"
DEV_END = "<!-- DEV-20260723-13 END -->"


def replace_marked_section(
    text: str, section: str, anchor: str | None = None
) -> str:
    rendered = f"{DEV_START}\n{section.rstrip()}\n{DEV_END}"
    if DEV_START in text:
        before, remainder = text.split(DEV_START, 1)
        _, after = remainder.split(DEV_END, 1)
        return before.rstrip() + "\n\n" + rendered + after
    if anchor is not None:
        if anchor not in text:
            raise AssertionError(f"Missing insertion anchor: {anchor}")
        return text.replace(anchor, rendered + "\n\n" + anchor, 1)
    return text.rstrip() + "\n\n" + rendered + "\n"


def repair_main() -> None:
    """Apply DEV-20260723-13 without recomputing any primary estimand."""
    hashes_before = {key: tree_aggregate(key) for key in LOCKED_TREE_EXPECTED}
    if hashes_before != LOCKED_TREE_EXPECTED:
        raise AssertionError(f"Locked input mismatch before repair: {hashes_before}")
    blind_path = ROOT / "stage2/BLIND_CONCLUSION.md"
    corrected_conclusion_path = (
        ROOT / "stage3/locked_supplement/stage2r/CORRECTED_CONCLUSION.md"
    )
    if sha256_file(blind_path) != BLIND_HASH:
        raise AssertionError("Blind conclusion changed")
    if sha256_file(corrected_conclusion_path) != CORRECTED_HASH:
        raise AssertionError("Corrected conclusion changed")

    ours = read_csv(ROOT / "stage1/cohort.csv")
    other_all = [row for row in ours if row["other_all"] == "1"]
    corrected_available = [
        row
        for row in other_all
        if row["pre1970_accidental_death"] == "0"
    ]
    excluded = [
        row
        for row in other_all
        if row["pre1970_accidental_death"] == "1"
    ]
    stage2_implemented_available = [
        row
        for row in ours
        if row["apollo_flew"] == "0"
        and bool(row["birth_date"])
        and (
            bool(row["death_date"])
            or row["vital_status_20260601"] == "alive"
        )
    ]
    if (
        len(other_all),
        len(stage2_implemented_available),
        len(corrected_available),
        len(excluded),
    ) != (66, 66, 54, 12):
        raise AssertionError("Unexpected OTHER_AVAILABLE correction counts")

    def endpoint(person: dict[str, str]) -> date:
        death = parse_date(adjudicated_death(person))
        return death if death and death <= CENSOR else CENSOR

    def alive_at_landmark(person: dict[str, str]) -> bool:
        death = parse_date(adjudicated_death(person))
        return death is None or death >= LANDMARK

    def reached_age80(person: dict[str, str]) -> bool:
        birth = parse_date(person["birth_date"])
        return add_years(birth, 80) <= endpoint(person)

    other_landmark_ids = {
        row["person_id"] for row in other_all if alive_at_landmark(row)
    }
    available_landmark_ids = {
        row["person_id"] for row in corrected_available if alive_at_landmark(row)
    }
    other_age80_ids = {
        row["person_id"] for row in other_all if reached_age80(row)
    }
    available_age80_ids = {
        row["person_id"] for row in corrected_available if reached_age80(row)
    }
    if other_landmark_ids != available_landmark_ids or len(other_landmark_ids) != 53:
        raise AssertionError("Post-1973 OTHER_AVAILABLE identity failure")
    if other_age80_ids != available_age80_ids or len(other_age80_ids) != 35:
        raise AssertionError("Age-80 OTHER_AVAILABLE identity failure")

    correction_rows = []
    for row in sorted(other_all, key=lambda value: value["person_id"]):
        included = row["pre1970_accidental_death"] == "0"
        correction_rows.append(
            {
                "person_id": row["person_id"],
                "full_name": row["full_name"],
                "birth_date": row["birth_date"],
                "death_date_locked_stage1": row["death_date"],
                "death_date_stage3_adjudicated": adjudicated_death(row),
                "other_all": row["other_all"],
                "pre1970_accidental_death": row["pre1970_accidental_death"],
                "corrected_other_available": int(included),
                "exclusion_reason": (
                    ""
                    if included
                    else "prespecified pre-1970 accidental death exclusion"
                ),
                "alive_on_1973_01_01": int(alive_at_landmark(row)),
                "in_other_all_post1973_risk_set": int(alive_at_landmark(row)),
                "in_corrected_other_available_post1973_risk_set": int(
                    included and alive_at_landmark(row)
                ),
                "reached_age80_by_death_or_2026_06_01": int(reached_age80(row)),
                "in_other_all_age80_risk_set": int(reached_age80(row)),
                "in_corrected_other_available_age80_risk_set": int(
                    included and reached_age80(row)
                ),
                "notes": (
                    "Excluded only from secondary birth-origin OTHER_AVAILABLE; "
                    "OTHER_ALL membership is unchanged."
                    if not included
                    else "Included under frozen OTHER_AVAILABLE definition."
                ),
            }
        )
    correction_fields = [
        "person_id",
        "full_name",
        "birth_date",
        "death_date_locked_stage1",
        "death_date_stage3_adjudicated",
        "other_all",
        "pre1970_accidental_death",
        "corrected_other_available",
        "exclusion_reason",
        "alive_on_1973_01_01",
        "in_other_all_post1973_risk_set",
        "in_corrected_other_available_post1973_risk_set",
        "reached_age80_by_death_or_2026_06_01",
        "in_other_all_age80_risk_set",
        "in_corrected_other_available_age80_risk_set",
        "notes",
    ]
    write_csv(
        OUT / "OTHER_AVAILABLE_CORRECTION.csv",
        correction_fields,
        correction_rows,
    )

    birth_records = [
        (
            years_between(parse_date(row["birth_date"]), endpoint(row)),
            int(bool(adjudicated_death(row))),
        )
        for row in corrected_available
    ]
    selected_ages = (60, 70, 80, 85, 90, 95)
    corrected_km = {}
    for attained_age in selected_ages:
        corrected_km[attained_age] = km_at_with_variance(
            birth_records, float(attained_age)
        )

    # Preserve every prior result row byte-for-value and replace only this deviation's rows.
    result_path = OUT / "HARMONIZED_RESULTS.csv"
    existing_results = read_csv(result_path)
    results = [
        row
        for row in existing_results
        if row["analysis"] != f"{DEV_ID}_POST_LOCK_CORRECTION"
    ]
    primary_before = next(
        row
        for row in results
        if row["analysis"] == "HARMONIZED_SHARED_SCOPE_1973_LANDMARK"
        and row["metric"] == "rmst_difference"
    )
    public_before = next(
        row
        for row in results
        if row["analysis"] == "HARMONIZED_SHARED_AGE80_RISK_SET"
        and row["endpoint_rule"] == "SOL_CORRECTED_UNRESTRICTED_AGE80_PLUS"
        and row["metric"] == "risk_difference"
    )
    if primary_before["estimate"] != "0.670028147":
        raise AssertionError("Primary RMST row changed before repair")
    if public_before["estimate"] != "0.079220779":
        raise AssertionError("Primary public-function row changed before repair")

    dev_analysis = f"{DEV_ID}_POST_LOCK_CORRECTION"
    results.extend(
        [
            result_row(
                "SURVIVAL",
                dev_analysis,
                "LOCKED_STAGE2_ERRONEOUS_OTHER_AVAILABLE",
                "OTHER_AVAILABLE",
                "",
                "group_count",
                len(stage2_implemented_available),
                units="people",
                method="locked Stage 2 implementation audit",
                notes=(
                    "Erroneously defined as every non-Apollo person with usable "
                    "birth/end-of-follow-up fields; identical to OTHER_ALL."
                ),
            ),
            result_row(
                "SURVIVAL",
                dev_analysis,
                "FROZEN_OTHER_AVAILABLE_SECONDARY_BIRTH_ORIGIN",
                "OTHER_AVAILABLE",
                "",
                "group_count",
                len(corrected_available),
                units="people",
                method="other_all == 1 and pre1970_accidental_death == 0",
                notes="Corrected secondary-only membership.",
            ),
            result_row(
                "SURVIVAL",
                dev_analysis,
                "FROZEN_OTHER_AVAILABLE_SECONDARY_BIRTH_ORIGIN",
                "OTHER_AVAILABLE",
                "OTHER_ALL",
                "excluded_pre1970_accidental_deaths",
                len(excluded),
                units="people",
                method="prespecified exclusion flag",
                notes="Exclusion does not redefine OTHER_ALL.",
            ),
        ]
    )
    for attained_age in selected_ages:
        estimate, lower, upper, variance = corrected_km[attained_age]
        results.append(
            result_row(
                "SURVIVAL",
                dev_analysis,
                "FROZEN_OTHER_AVAILABLE_SECONDARY_BIRTH_ORIGIN",
                "OTHER_AVAILABLE",
                "",
                f"km_survival_to_age_{attained_age}",
                estimate,
                lower,
                upper,
                denominator_a=len(corrected_available),
                units="probability",
                method="retrospective Kaplan-Meier from birth; log-log Greenwood interval",
                notes=(
                    "Post-lock correction; future-flight-selected secondary description; "
                    f"greenwood_variance={variance:.8f}."
                ),
            )
        )
    results.extend(
        [
            result_row(
                "SURVIVAL",
                dev_analysis,
                "FROZEN_OTHER_AVAILABLE_SET_IDENTITY",
                "OTHER_AVAILABLE",
                "OTHER_ALL",
                "exact_post1973_risk_set_identity",
                1,
                numerator_a=len(available_landmark_ids),
                denominator_a=len(other_landmark_ids),
                units="boolean",
                method="exact person-ID set comparison",
                notes="Both sets contain the same 53 people after the 1973 landmark.",
            ),
            result_row(
                "PUBLIC_FUNCTION",
                dev_analysis,
                "FROZEN_OTHER_AVAILABLE_SET_IDENTITY",
                "OTHER_AVAILABLE",
                "OTHER_ALL",
                "exact_age80_risk_set_identity",
                1,
                numerator_a=len(available_age80_ids),
                denominator_a=len(other_age80_ids),
                units="boolean",
                method="exact person-ID set comparison",
                notes="Both sets contain the same 35 non-Apollo age-80-eligible people.",
            ),
        ]
    )
    write_csv(result_path, list(existing_results[0]), results)

    difference_path = OUT / "ROW_DIFFERENCES.csv"
    existing_differences = read_csv(difference_path)
    differences = [
        row
        for row in existing_differences
        if not (
            row["difference_category"] == "implementation_analysis_difference"
            and row["field"] == "OTHER_AVAILABLE_definition"
        )
    ]
    differences.append(
        {
            "reconciliation_row_id": f"DIFF{len(differences)+1:03d}",
            "ours_person_id": "",
            "reference_person_id": "",
            "ours_name": "",
            "reference_name": "",
            "scope_status": "POST_LOCK_CONTROLLER_CORRECTION",
            "difference_category": "implementation_analysis_difference",
            "field": "OTHER_AVAILABLE_definition",
            "ours_value": (
                "Locked Stage 2: every non-Apollo person with usable birth/end fields; n=66"
            ),
            "reference_value": (
                "Frozen Sol protocol: OTHER_ALL excluding pre-1970 accidental deaths; n=54"
            ),
            "adjudicated_value": (
                "other_all == 1 and pre1970_accidental_death == 0"
            ),
            "adjudication": (
                f"{DEV_ID}; controller-supplied frozen protocol fact unavailable "
                "during the neutral Stage 2 runtime."
            ),
            "source_urls": "",
            "impact_on_harmonized_analysis": (
                "Secondary birth-origin OTHER_AVAILABLE membership/KM only; "
                "1973 RMST and age-80 analyses unchanged by exact risk-set identity."
            ),
            "notes": (
                "Implementation error, not a rival definition and not an intrinsically "
                "superior-control claim."
            ),
        }
    )
    write_csv(difference_path, list(existing_differences[0]), differences)

    km_lines = [
        "| Attained age | Corrected KM | 95% log-log Greenwood CI |",
        "|---:|---:|---:|",
    ]
    for attained_age in selected_ages:
        estimate, lower, upper, _ = corrected_km[attained_age]
        km_lines.append(
            f"| {attained_age} | {estimate:.6f} | {lower:.6f} to {upper:.6f} |"
        )
    correction_section = f"""## Technical post-lock correction — `{DEV_ID}`

The controller supplied a frozen protocol fact that was unavailable in the neutral runtime: `OTHER_AVAILABLE` is `OTHER_ALL` excluding prespecified pre-1970 accidental deaths. It is a secondary birth-origin description only and is not an intrinsically superior control.

Locked Stage 2 instead implemented `OTHER_AVAILABLE` as every non-Apollo person with usable birth and end-of-follow-up fields (`stage2/analysis.py`, locked line 716). Because all 66 non-Apollo rows were usable, it incorrectly made `OTHER_AVAILABLE` identical to the 66-person `OTHER_ALL` even at birth origin. The frozen rule yields **54 people**, excluding **12** flagged pre-1970 accidental deaths.

The locked secondary files affected by the wrong membership are:

- `stage2/survival_group_summary.csv` (`OTHER_AVAILABLE` group count and dependent summaries);
- `stage2/km_birth_selected_ages.csv` (all six `OTHER_AVAILABLE` readouts);
- `stage2/survival_birth_km.svg` (the `OTHER_AVAILABLE` birth-origin curve);
- `stage2/population_expectation.csv` and the `OTHER_AVAILABLE` population-benchmark row in `stage2/RESULTS_SUMMARY.csv` (both were composed from the wrong 66-person set);
- the corresponding Stage 2 report/code statements that treated the birth-origin set as 66.

Per the controller's narrow repair instruction, Stage 3 recomputed only the corrected group count and retrospective birth-origin KM readouts. The locked Stage 2 files remain unchanged.

{chr(10).join(km_lines)}

`stage3/OTHER_AVAILABLE_CORRECTION.csv` contains all 66 `OTHER_ALL` people, the 12 exclusions, and person-level landmark/age-80 membership checks.

The corrected 54-person `OTHER_AVAILABLE` set and 66-person `OTHER_ALL` set are **not** identical at birth origin. They become exactly identical after the 1973 landmark: both contain the same 53 person IDs because all 12 prespecified accidental exclusions died before 1970. They are also exactly identical in the non-Apollo age-80 risk set: both contain the same 35 person IDs because none of the 12 exclusions reached age 80.

Therefore the locked 1973-landmark Apollo-versus-`OTHER_ALL` RMST and all age-80 public-function analyses are unchanged. No primary estimand was recomputed in this repair; their existing Stage 3 rows were read, hash-protected, and preserved. The endpoint-specific narrow Stage 3 interpretation and both locked conclusions remain verbatim and unchanged.
"""
    report_path = OUT / "RECONCILIATION.md"
    report = report_path.read_text(encoding="utf-8")
    report = replace_marked_section(
        report,
        correction_section,
        anchor="## Locked conclusions preserved verbatim",
    )
    report_path.write_text(report, encoding="utf-8")

    validation_section = f"""## `{DEV_ID}` repair checks

| Check | Result |
|---|---|
| Locked Stage 2 erroneous implementation reproduced as 66 usable non-Apollo rows | PASS |
| Frozen `OTHER_AVAILABLE` definition implemented as `other_all == 1` and `pre1970_accidental_death == 0` | PASS |
| Corrected `OTHER_AVAILABLE` count is 54; excluded count is 12 | PASS |
| Corrected and `OTHER_ALL` post-1973 person-ID sets are exactly identical (53 each) | PASS |
| Corrected and `OTHER_ALL` age-80 person-ID sets are exactly identical (35 each) | PASS |
| Corrected birth-origin KM readouts retained at ages 60, 70, 80, 85, 90, and 95 | PASS |
| Existing primary RMST result row preserved at +0.670028147 years | PASS |
| Existing corrected unrestricted Sol public-function result row preserved at +0.079220779 | PASS |
| No primary estimand recomputed by `repair_main` | PASS |
| Both locked conclusions remain hash-identical and verbatim | PASS |
| No browsing occurred during this repair | PASS |

The 1973-landmark RMST is unchanged because the corrected and `OTHER_ALL`
post-landmark person-ID sets are identical. The age-80 public-function analyses
are unchanged because the corresponding age-80 person-ID sets are identical.
"""
    validation_path = OUT / "VALIDATION.md"
    validation_text = validation_path.read_text(encoding="utf-8")
    validation_text = replace_marked_section(validation_text, validation_section)
    validation_path.write_text(validation_text, encoding="utf-8")

    complete_section = f"""## Technical correction `{DEV_ID}`

Locked Stage 2 incorrectly implemented `OTHER_AVAILABLE` as 66 usable non-Apollo people. The frozen secondary-only definition yields 54 people after excluding 12 prespecified pre-1970 accidental deaths. Corrected membership and birth-origin KM readouts are retained in `stage3/OTHER_AVAILABLE_CORRECTION.csv` and `stage3/HARMONIZED_RESULTS.csv`.

Exact person-ID checks show `OTHER_AVAILABLE` and `OTHER_ALL` are identical after the 1973 landmark (53 each) and in the age-80 risk set (35 each). The primary landmark RMST, age-80 public-function analyses, both locked conclusions, and the narrow endpoint-specific Stage 3 interpretation are unchanged. This repair did not browse or rerun a primary estimand.
"""
    complete_path = OUT / "STAGE_COMPLETE.md"
    complete_text = complete_path.read_text(encoding="utf-8")
    if "- `stage3/OTHER_AVAILABLE_CORRECTION.csv`" not in complete_text:
        complete_text = complete_text.replace(
            "- `stage3/REFERENCE_MANIFEST_VALIDATION.csv`",
            "- `stage3/REFERENCE_MANIFEST_VALIDATION.csv`\n"
            "- `stage3/OTHER_AVAILABLE_CORRECTION.csv`",
        )
    complete_text = replace_marked_section(
        complete_text,
        complete_section,
        anchor="No locked conclusion was rewritten. No blocking failure remains.",
    )
    complete_path.write_text(complete_text, encoding="utf-8")

    contamination_path = OUT / "CONTAMINATION.md"
    contamination_text = contamination_path.read_text(encoding="utf-8")
    contamination_text = replace_marked_section(
        contamination_text,
        f"""## `{DEV_ID}` repair

No web query or page open occurred during this technical correction. Only locked local Sol data and current Stage 3 artifacts were used.
""",
    )
    contamination_path.write_text(contamination_text, encoding="utf-8")

    # Reverify approved reference hashes and every locked tree after all writes.
    manifest_rows = read_csv(OUT / "REFERENCE_MANIFEST_VALIDATION.csv")
    if not all(
        row["match"] == "1"
        and sha256_file(ROOT / row["runtime_path"]) == row["actual_sha256"]
        for row in manifest_rows
    ):
        raise AssertionError("Reference manifest validation changed")
    hashes_after = {key: tree_aggregate(key) for key in LOCKED_TREE_EXPECTED}
    if hashes_after != hashes_before or hashes_after != LOCKED_TREE_EXPECTED:
        raise AssertionError("Locked tree changed during repair")
    if sha256_file(blind_path) != BLIND_HASH:
        raise AssertionError("Blind conclusion changed during repair")
    if sha256_file(corrected_conclusion_path) != CORRECTED_HASH:
        raise AssertionError("Corrected conclusion changed during repair")


if __name__ == "__main__":
    repair_main()
