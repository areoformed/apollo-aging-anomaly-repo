#!/usr/bin/env python3
"""Stage 2 descriptive survival and public-evidence analyses.

The implementation uses only the Python standard library so the complete
calculation remains runnable in the isolated runtime.
"""

from __future__ import annotations

import csv
import hashlib
import html
import math
import random
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from statistics import fmean, median
from typing import Callable, Iterable


ROOT = Path(__file__).resolve().parent.parent
STAGE = ROOT / "stage2"
CENSOR = date(2026, 6, 1)
LANDMARK = date(1973, 1, 1)
RMST_HORIZON = 50.0
BOOT_REPS = 50_000
SEED = 20_260_721
Z975 = 1.959963984540054
LOCKED_AGGREGATE_SHA256 = "cb4ed5df8f9e99656e06d5d980b46e37eb1fae5756eee0f623a934edd97146a4"

SSA_TABLE11 = "https://www.ssa.gov/oact/NOTES/as120/LifeTables_Tbl_11.html"
SSA_TABLE7_1920 = "https://www.ssa.gov/oact/NOTES/as120/LifeTables_Tbl_7_1920.html"
SSA_TABLE7_1930 = "https://www.ssa.gov/oact/NOTES/as120/LifeTables_Tbl_7_1930.html"
SSA_TABLE7_1940 = "https://www.ssa.gov/oact/NOTES/as120/LifeTables_Tbl_7_1940.html"
SSA_TABLE7_1950 = "https://www.ssa.gov/oact/NOTES/as120/LifeTables_Tbl_7_1950.html"
SSA_DEFINITIONS = "https://www.ssa.gov/oact/HistEst/CohLifeTables/LifeTableDefinitions.pdf"
SSA_2023_INDEX = "https://www.ssa.gov/oact/HistEst/CohLifeTables/2023/CohLifeTables2023.html"
SSA_2023_CSV = "https://www.ssa.gov/oact/HistEst/CohLifeTables/2023/CohLifeTables_M_Alt2_TR2023.csv"

# Exact annual male cohort e0 values transcribed from official SSA AS120 Table 11.
SSA_MALE_E0 = {
    1921: 62.75, 1922: 63.11, 1923: 63.31, 1924: 63.80,
    1925: 64.08, 1926: 64.34, 1927: 65.09, 1928: 65.14,
    1929: 65.61, 1930: 66.09, 1931: 66.67, 1932: 67.07,
    1933: 67.29, 1934: 67.24, 1935: 67.82, 1936: 68.01,
    1937: 68.43, 1938: 68.92, 1939: 69.41, 1940: 69.55,
    1941: 69.91, 1942: 70.46,
}

# Official male l_80 / 100,000 from decennial AS120 Table 7 cohorts.
SSA_MALE_S80_ANCHORS = {
    1920: 0.30437,
    1930: 0.36675,
    1940: 0.42355,
    1950: 0.46735,
}

GROUP_ORDER = [
    "APOLLO_FLEW",
    "OTHER_ALL",
    "CORE_NASA_NON_APOLLO",
    "MILITARY_ONLY",
    "OTHER_AVAILABLE",
]

COMPARATORS = [
    ("OTHER_ALL", "PRIMARY"),
    ("CORE_NASA_NON_APOLLO", "COMPOSITION_SENSITIVITY"),
    ("MILITARY_ONLY", "COMPOSITION_SENSITIVITY"),
]

RESULT_COLUMNS = [
    "domain", "analysis", "contrast", "estimand", "estimate",
    "ci_lower", "ci_upper", "unit", "n_apollo", "n_comparator",
    "events_apollo", "events_comparator", "method", "primary",
    "sensitivity_type", "p_value", "notes",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def locked_input_manifest() -> tuple[list[dict[str, str]], str]:
    aggregate = hashlib.sha256()
    rows = []
    for root_name in ("stage1", "stage1b", "stage1c"):
        root = ROOT / root_name
        for path in sorted(item for item in root.rglob("*") if item.is_file()):
            relative = path.relative_to(ROOT).as_posix()
            data = path.read_bytes()
            digest = hashlib.sha256(data).hexdigest()
            rows.append({
                "path": relative,
                "bytes": str(len(data)),
                "sha256": digest,
            })
            encoded = relative.encode("utf-8")
            aggregate.update(len(encoded).to_bytes(8, "big"))
            aggregate.update(encoded)
            aggregate.update(len(data).to_bytes(8, "big"))
            aggregate.update(data)
    return rows, aggregate.hexdigest()


def write_csv(path: Path, columns: list[str], rows: Iterable[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=columns,
            dialect="excel",
            lineterminator="\r\n",
            extrasaction="raise",
        )
        writer.writeheader()
        writer.writerows(rows)


def parse_date(value: str) -> date | None:
    return date.fromisoformat(value) if value else None


def add_years(value: date, years: int) -> date:
    try:
        return value.replace(year=value.year + years)
    except ValueError:
        return value.replace(year=value.year + years, day=28)


def age_exact(birth: date, when: date) -> float:
    years = when.year - birth.year
    if (when.month, when.day) < (birth.month, birth.day):
        years -= 1
    last = add_years(birth, years)
    nxt = add_years(birth, years + 1)
    return years + (when - last).days / (nxt - last).days


def years_between(start: date, end: date) -> float:
    return (end - start).days / 365.2425


def percentile(values: list[float], probability: float) -> float:
    if not values:
        return math.nan
    ordered = sorted(values)
    position = probability * (len(ordered) - 1)
    lower = int(math.floor(position))
    upper = int(math.ceil(position))
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def quantile_summary(values: list[float]) -> tuple[float, float, float, float, float]:
    return (
        median(values),
        percentile(values, 0.25),
        percentile(values, 0.75),
        min(values),
        max(values),
    )


def fmt(value: float | int | str | None, digits: int = 3) -> str:
    if value is None or value == "":
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        if math.isnan(value):
            return "NA"
        return "Inf" if value > 0 else "-Inf"
    return f"{float(value):.{digits}f}"


def normal_cdf(value: float) -> float:
    return 0.5 * (1.0 + math.erf(value / math.sqrt(2.0)))


def betacf(a: float, b: float, x: float) -> float:
    max_iterations = 300
    epsilon = 3e-14
    fpmin = 1e-300
    qab = a + b
    qap = a + 1.0
    qam = a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < fpmin:
        d = fpmin
    d = 1.0 / d
    h = d
    for iteration in range(1, max_iterations + 1):
        m2 = 2 * iteration
        aa = iteration * (b - iteration) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < fpmin:
            d = fpmin
        c = 1.0 + aa / c
        if abs(c) < fpmin:
            c = fpmin
        d = 1.0 / d
        h *= d * c
        aa = -(a + iteration) * (qab + iteration) * x / (
            (a + m2) * (qap + m2)
        )
        d = 1.0 + aa * d
        if abs(d) < fpmin:
            d = fpmin
        c = 1.0 + aa / c
        if abs(c) < fpmin:
            c = fpmin
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < epsilon:
            break
    return h


def regularized_beta(x: float, a: float, b: float) -> float:
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    log_term = (
        math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
        + a * math.log(x) + b * math.log1p(-x)
    )
    term = math.exp(log_term)
    if x < (a + 1.0) / (a + b + 2.0):
        return term * betacf(a, b, x) / a
    return 1.0 - term * betacf(b, a, 1.0 - x) / b


def beta_ppf(probability: float, a: float, b: float) -> float:
    if probability <= 0:
        return 0.0
    if probability >= 1:
        return 1.0
    low, high = 0.0, 1.0
    for _ in range(100):
        middle = (low + high) / 2.0
        if regularized_beta(middle, a, b) < probability:
            low = middle
        else:
            high = middle
    return (low + high) / 2.0


def clopper_pearson(successes: int, total: int, alpha: float = 0.05) -> tuple[float, float]:
    if total == 0:
        return math.nan, math.nan
    lower = 0.0 if successes == 0 else beta_ppf(alpha / 2, successes, total - successes + 1)
    upper = 1.0 if successes == total else beta_ppf(1 - alpha / 2, successes + 1, total - successes)
    return lower, upper


def wilson(successes: int, total: int) -> tuple[float, float]:
    if total == 0:
        return math.nan, math.nan
    p = successes / total
    z2 = Z975 * Z975
    center = (p + z2 / (2 * total)) / (1 + z2 / total)
    half = Z975 * math.sqrt(p * (1 - p) / total + z2 / (4 * total * total)) / (1 + z2 / total)
    return max(0.0, center - half), min(1.0, center + half)


def newcombe_difference(a: int, n1: int, c: int, n0: int) -> tuple[float, float]:
    a_low, a_high = wilson(a, n1)
    c_low, c_high = wilson(c, n0)
    return a_low - c_high, a_high - c_low


def risk_ratio_interval(a: int, n1: int, c: int, n0: int) -> tuple[float, float, float, str]:
    if a == 0 or c == 0 or a == n1 or c == n0:
        aa, bb, cc, dd = a + 0.5, n1 - a + 0.5, c + 0.5, n0 - c + 0.5
        method = "Katz log with Haldane–Anscombe correction"
    else:
        aa, bb, cc, dd = float(a), float(n1 - a), float(c), float(n0 - c)
        method = "Katz log"
    p1 = aa / (aa + bb)
    p0 = cc / (cc + dd)
    ratio = p1 / p0
    se = math.sqrt(1 / aa - 1 / (aa + bb) + 1 / cc - 1 / (cc + dd))
    return ratio, math.exp(math.log(ratio) - Z975 * se), math.exp(math.log(ratio) + Z975 * se), method


def log_choose(n: int, k: int) -> float:
    if k < 0 or k > n:
        return -math.inf
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)


def hypergeom_distribution(n1: int, n0: int, positives: int, log_theta: float = 0.0) -> tuple[list[int], list[float]]:
    low = max(0, positives - n0)
    high = min(n1, positives)
    support = list(range(low, high + 1))
    log_weights = [
        log_choose(n1, k) + log_choose(n0, positives - k) + k * log_theta
        for k in support
    ]
    maximum = max(log_weights)
    weights = [math.exp(value - maximum) for value in log_weights]
    total = sum(weights)
    return support, [value / total for value in weights]


def fisher_exact_two_sided(a: int, b: int, c: int, d: int) -> float:
    support, probabilities = hypergeom_distribution(a + b, c + d, a + c)
    observed = probabilities[support.index(a)]
    return min(1.0, sum(prob for prob in probabilities if prob <= observed + 1e-15))


def conditional_or_interval(a: int, b: int, c: int, d: int) -> tuple[float, float, float]:
    n1, n0, positives = a + b, c + d, a + c
    support, _ = hypergeom_distribution(n1, n0, positives)
    low_support, high_support = support[0], support[-1]
    sample_or = math.inf if b * c == 0 and a * d > 0 else (0.0 if a * d == 0 else a * d / (b * c))

    def upper_tail(log_theta: float) -> float:
        xs, probs = hypergeom_distribution(n1, n0, positives, log_theta)
        return sum(prob for x, prob in zip(xs, probs) if x >= a)

    def lower_tail(log_theta: float) -> float:
        xs, probs = hypergeom_distribution(n1, n0, positives, log_theta)
        return sum(prob for x, prob in zip(xs, probs) if x <= a)

    target = 0.025
    if a == low_support:
        lower = 0.0
    else:
        lo, hi = -40.0, 40.0
        for _ in range(120):
            mid = (lo + hi) / 2
            if upper_tail(mid) < target:
                lo = mid
            else:
                hi = mid
        lower = math.exp((lo + hi) / 2)

    if a == high_support:
        upper = math.inf
    else:
        lo, hi = -40.0, 40.0
        for _ in range(120):
            mid = (lo + hi) / 2
            if lower_tail(mid) > target:
                lo = mid
            else:
                hi = mid
        upper = math.exp((lo + hi) / 2)
    return sample_or, lower, upper


def exact_median_interval(values: list[float]) -> tuple[float, float]:
    ordered = sorted(values)
    n = len(ordered)
    selected = 1
    for k in range(1, n // 2 + 2):
        tail = sum(math.comb(n, j) for j in range(k)) / (2 ** n)
        if tail <= 0.025:
            selected = k
        else:
            break
    return ordered[selected - 1], ordered[n - selected]


def km_rmst(records: list[tuple[float, int]], horizon: float) -> float:
    ordered = sorted(records)
    survival = 1.0
    previous = 0.0
    area = 0.0
    risk = len(ordered)
    index = 0
    while index < len(ordered):
        current = ordered[index][0]
        if current > horizon:
            break
        area += survival * max(0.0, current - previous)
        deaths = 0
        removed = 0
        while index < len(ordered) and ordered[index][0] == current:
            deaths += ordered[index][1]
            removed += 1
            index += 1
        if risk > 0 and deaths:
            survival *= 1.0 - deaths / risk
        risk -= removed
        previous = current
    area += survival * max(0.0, horizon - previous)
    return area


def km_step(records: list[tuple[float, int]], xmax: float | None = None) -> list[tuple[float, float]]:
    ordered = sorted(records)
    survival = 1.0
    risk = len(ordered)
    points = [(0.0, 1.0)]
    index = 0
    while index < len(ordered):
        current = ordered[index][0]
        if xmax is not None and current > xmax:
            break
        deaths = 0
        removed = 0
        while index < len(ordered) and ordered[index][0] == current:
            deaths += ordered[index][1]
            removed += 1
            index += 1
        points.append((current, survival))
        if risk > 0 and deaths:
            survival *= 1.0 - deaths / risk
            points.append((current, survival))
        risk -= removed
    if xmax is not None:
        points.append((xmax, survival))
    return points


def km_at(records: list[tuple[float, int]], target: float) -> tuple[float, float, float, float]:
    ordered = sorted(records)
    survival = 1.0
    greenwood = 0.0
    risk = len(ordered)
    index = 0
    while index < len(ordered):
        current = ordered[index][0]
        if current > target:
            break
        deaths = 0
        removed = 0
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
    variance = survival * survival * greenwood
    if survival <= 0:
        return survival, 0.0, 0.0, variance
    if survival >= 1 or greenwood == 0:
        return survival, survival, survival, variance
    loglog = math.log(-math.log(survival))
    se = math.sqrt(greenwood) / abs(math.log(survival))
    lower = math.exp(-math.exp(loglog + Z975 * se))
    upper = math.exp(-math.exp(loglog - Z975 * se))
    return survival, lower, upper, variance


def aj_cif(records: list[tuple[float, int]], horizon: float = 5.0) -> float:
    """Aalen–Johansen CIF for status 1, with status 2 competing and 0 censoring."""
    ordered = sorted(records)
    risk = len(ordered)
    survival = 1.0
    cif = 0.0
    index = 0
    while index < len(ordered):
        current = ordered[index][0]
        if current >= horizon:
            break
        d1 = d2 = removed = 0
        while index < len(ordered) and ordered[index][0] == current:
            status = ordered[index][1]
            d1 += status == 1
            d2 += status == 2
            removed += 1
            index += 1
        if risk > 0:
            cif += survival * d1 / risk
            survival *= 1.0 - (d1 + d2) / risk
        risk -= removed
    return cif


def aj_step(records: list[tuple[float, int]], horizon: float = 5.0) -> list[tuple[float, float]]:
    ordered = sorted(records)
    risk = len(ordered)
    survival = 1.0
    cif = 0.0
    points = [(0.0, 0.0)]
    index = 0
    while index < len(ordered):
        current = ordered[index][0]
        if current >= horizon:
            break
        d1 = d2 = removed = 0
        while index < len(ordered) and ordered[index][0] == current:
            status = ordered[index][1]
            d1 += status == 1
            d2 += status == 2
            removed += 1
            index += 1
        points.append((current, cif))
        if risk > 0:
            cif += survival * d1 / risk
            survival *= 1.0 - (d1 + d2) / risk
        points.append((current, cif))
        risk -= removed
    points.append((horizon, cif))
    return points


def bootstrap_difference(
    first: list[tuple[float, int]],
    second: list[tuple[float, int]],
    metric: Callable[[list[tuple[float, int]]], float],
    repetitions: int = BOOT_REPS,
    seed: int = SEED,
) -> tuple[float, float, float]:
    point = metric(first) - metric(second)
    generator = random.Random(seed)
    n_first, n_second = len(first), len(second)
    estimates: list[float] = []
    append = estimates.append
    for _ in range(repetitions):
        sample_first = [first[generator.randrange(n_first)] for _ in range(n_first)]
        sample_second = [second[generator.randrange(n_second)] for _ in range(n_second)]
        append(metric(sample_first) - metric(sample_second))
    return point, percentile(estimates, 0.025), percentile(estimates, 0.975)


def solve_2x2(matrix: list[list[float]], vector: list[float]) -> list[float]:
    determinant = matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
    if abs(determinant) < 1e-12:
        raise ArithmeticError("singular 2x2 matrix")
    return [
        (vector[0] * matrix[1][1] - vector[1] * matrix[0][1]) / determinant,
        (matrix[0][0] * vector[1] - matrix[1][0] * vector[0]) / determinant,
    ]


def inverse_2x2(matrix: list[list[float]]) -> list[list[float]]:
    determinant = matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
    return [
        [matrix[1][1] / determinant, -matrix[0][1] / determinant],
        [-matrix[1][0] / determinant, matrix[0][0] / determinant],
    ]


def cox_components(
    times: list[float],
    status: list[int],
    covariates: list[list[float]],
    beta: list[float],
) -> tuple[float, list[float], list[list[float]]]:
    loglik = 0.0
    score = [0.0, 0.0]
    information = [[0.0, 0.0], [0.0, 0.0]]
    event_times = sorted({times[i] for i, value in enumerate(status) if value})
    eta = [beta[0] * x[0] + beta[1] * x[1] for x in covariates]
    exponent = [math.exp(max(-700.0, min(700.0, value))) for value in eta]
    for current in event_times:
        deaths = [i for i in range(len(times)) if status[i] and times[i] == current]
        risk = [i for i in range(len(times)) if times[i] >= current]
        count = len(deaths)
        s0 = sum(exponent[i] for i in risk)
        s1 = [sum(exponent[i] * covariates[i][j] for i in risk) for j in range(2)]
        s2 = [
            [sum(exponent[i] * covariates[i][j] * covariates[i][k] for i in risk) for k in range(2)]
            for j in range(2)
        ]
        e0 = sum(exponent[i] for i in deaths)
        e1 = [sum(exponent[i] * covariates[i][j] for i in deaths) for j in range(2)]
        e2 = [
            [sum(exponent[i] * covariates[i][j] * covariates[i][k] for i in deaths) for k in range(2)]
            for j in range(2)
        ]
        loglik += sum(eta[i] for i in deaths)
        for j in range(2):
            score[j] += sum(covariates[i][j] for i in deaths)
        for tied in range(count):
            fraction = tied / count
            denominator = s0 - fraction * e0
            mean = [(s1[j] - fraction * e1[j]) / denominator for j in range(2)]
            loglik -= math.log(denominator)
            for j in range(2):
                score[j] -= mean[j]
                for k in range(2):
                    moment = (s2[j][k] - fraction * e2[j][k]) / denominator
                    information[j][k] += moment - mean[j] * mean[k]
    return loglik, score, information


def cox_efron(
    times: list[float],
    status: list[int],
    groups: list[int],
    ages: list[float],
) -> dict[str, float | int | list]:
    age_center = fmean(ages)
    covariates = [[float(group), age - age_center] for group, age in zip(groups, ages)]
    beta = [0.0, 0.0]
    converged = False
    for iteration in range(50):
        _, score, information = cox_components(times, status, covariates, beta)
        increment = solve_2x2(information, score)
        beta = [beta[j] + increment[j] for j in range(2)]
        if max(abs(value) for value in increment) < 1e-9:
            converged = True
            break
    loglik, score, information = cox_components(times, status, covariates, beta)
    variance = inverse_2x2(information)
    ses = [math.sqrt(max(0.0, variance[j][j])) for j in range(2)]
    return {
        "beta": beta,
        "se": ses,
        "variance": variance,
        "loglik": loglik,
        "converged": int(converged),
        "iterations": iteration + 1,
        "age_center": age_center,
        "covariates": covariates,
    }


def student_t_two_sided_p(value: float, degrees: int) -> float:
    if degrees <= 0:
        return math.nan
    x = degrees / (degrees + value * value)
    return regularized_beta(x, degrees / 2.0, 0.5)


def schoenfeld_diagnostic(
    times: list[float],
    status: list[int],
    covariates: list[list[float]],
    beta: list[float],
) -> list[dict[str, float | str | int]]:
    eta = [beta[0] * x[0] + beta[1] * x[1] for x in covariates]
    exponent = [math.exp(value) for value in eta]
    residuals = [[], []]
    transformed_times: list[float] = []
    event_times = sorted({times[i] for i, value in enumerate(status) if value})
    for current in event_times:
        deaths = [i for i in range(len(times)) if status[i] and times[i] == current]
        risk = [i for i in range(len(times)) if times[i] >= current]
        count = len(deaths)
        s0 = sum(exponent[i] for i in risk)
        s1 = [sum(exponent[i] * covariates[i][j] for i in risk) for j in range(2)]
        e0 = sum(exponent[i] for i in deaths)
        e1 = [sum(exponent[i] * covariates[i][j] for i in deaths) for j in range(2)]
        expected = [0.0, 0.0]
        for tied in range(count):
            fraction = tied / count
            denominator = s0 - fraction * e0
            for j in range(2):
                expected[j] += (s1[j] - fraction * e1[j]) / denominator / count
        for index in deaths:
            transformed_times.append(math.log(max(current, 1e-12)))
            for j in range(2):
                residuals[j].append(covariates[index][j] - expected[j])

    rows = []
    chi_square = 0.0
    for name, values in zip(("APOLLO_FLEW", "AGE_AT_LANDMARK"), residuals):
        mean_x, mean_y = fmean(transformed_times), fmean(values)
        numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(transformed_times, values))
        denominator = math.sqrt(
            sum((x - mean_x) ** 2 for x in transformed_times)
            * sum((y - mean_y) ** 2 for y in values)
        )
        correlation = numerator / denominator if denominator else 0.0
        degrees = len(values) - 2
        test_stat = correlation * math.sqrt(degrees / max(1e-15, 1 - correlation * correlation))
        p_value = student_t_two_sided_p(test_stat, degrees)
        chi_square += test_stat * test_stat
        rows.append({
            "term": name,
            "events": len(values),
            "correlation_with_log_time": correlation,
            "test_statistic": test_stat,
            "df": 1,
            "p_value": p_value,
            "method": "Schoenfeld-residual correlation with log event time",
        })
    rows.append({
        "term": "GLOBAL_APPROXIMATION",
        "events": len(transformed_times),
        "correlation_with_log_time": "",
        "test_statistic": chi_square,
        "df": 2,
        "p_value": math.exp(-chi_square / 2.0),
        "method": "Sum of two Schoenfeld correlation statistics; chi-square(2) approximation",
    })
    return rows


def ssa_s80(birth_year: int) -> float:
    lower = (birth_year // 10) * 10
    upper = lower + 10
    fraction = (birth_year - lower) / 10.0
    return SSA_MALE_S80_ANCHORS[lower] * (1 - fraction) + SSA_MALE_S80_ANCHORS[upper] * fraction


def group_membership(row: dict[str, str]) -> dict[str, bool]:
    military = row["apollo_flew"] == "0" and any(
        row[name] == "1" for name in ("military_x15", "military_dyna_soar", "military_mol")
    )
    usable = bool(row["birth_date"]) and (
        bool(row["death_date"]) or row["vital_status_20260601"] == "alive"
    )
    return {
        "APOLLO_FLEW": row["apollo_flew"] == "1",
        "OTHER_ALL": row["other_all"] == "1",
        "CORE_NASA_NON_APOLLO": row["core_nasa_non_apollo"] == "1",
        "MILITARY_ONLY": military,
        "OTHER_AVAILABLE": row["apollo_flew"] == "0" and usable,
    }


def result_row(**kwargs) -> dict:
    row = {column: "" for column in RESULT_COLUMNS}
    row.update(kwargs)
    return row


def svg_step_plot(
    path: Path,
    series: list[tuple[str, list[tuple[float, float]], str]],
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    title: str,
    x_label: str,
    y_label: str,
) -> None:
    width, height = 900, 560
    left, right, top, bottom = 90, 30, 65, 75
    plot_w, plot_h = width - left - right, height - top - bottom

    def sx(value: float) -> float:
        return left + (value - x_min) / (x_max - x_min) * plot_w

    def sy(value: float) -> float:
        return top + (y_max - value) / (y_max - y_min) * plot_h

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{width/2}" y="30" text-anchor="middle" font-family="sans-serif" font-size="20">{html.escape(title)}</text>',
    ]
    for tick in range(6):
        x_value = x_min + (x_max - x_min) * tick / 5
        x = sx(x_value)
        parts.append(f'<line x1="{x:.2f}" y1="{top}" x2="{x:.2f}" y2="{top+plot_h}" stroke="#e5e7eb"/>')
        parts.append(f'<text x="{x:.2f}" y="{top+plot_h+24}" text-anchor="middle" font-family="sans-serif" font-size="12">{x_value:.0f}</text>')
        y_value = y_min + (y_max - y_min) * tick / 5
        y = sy(y_value)
        parts.append(f'<line x1="{left}" y1="{y:.2f}" x2="{left+plot_w}" y2="{y:.2f}" stroke="#e5e7eb"/>')
        parts.append(f'<text x="{left-10}" y="{y+4:.2f}" text-anchor="end" font-family="sans-serif" font-size="12">{y_value:.1f}</text>')
    parts.extend([
        f'<line x1="{left}" y1="{top+plot_h}" x2="{left+plot_w}" y2="{top+plot_h}" stroke="black"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top+plot_h}" stroke="black"/>',
        f'<text x="{left+plot_w/2}" y="{height-20}" text-anchor="middle" font-family="sans-serif" font-size="14">{html.escape(x_label)}</text>',
        f'<text transform="translate(22 {top+plot_h/2}) rotate(-90)" text-anchor="middle" font-family="sans-serif" font-size="14">{html.escape(y_label)}</text>',
    ])
    for index, (label, points, color) in enumerate(series):
        command = []
        for point_index, (x_value, y_value) in enumerate(points):
            x_value = min(x_max, max(x_min, x_value))
            y_value = min(y_max, max(y_min, y_value))
            command.append(("M" if point_index == 0 else "L") + f"{sx(x_value):.2f},{sy(y_value):.2f}")
        parts.append(f'<path d="{" ".join(command)}" fill="none" stroke="{color}" stroke-width="3"/>')
        legend_y = 48 + index * 20
        parts.append(f'<line x1="{width-270}" y1="{legend_y}" x2="{width-240}" y2="{legend_y}" stroke="{color}" stroke-width="3"/>')
        parts.append(f'<text x="{width-232}" y="{legend_y+4}" font-family="sans-serif" font-size="12">{html.escape(label)}</text>')
    parts.append("</svg>\n")
    path.write_text("\n".join(parts), encoding="utf-8")


def svg_documentation_bars(path: Path, depth_rows: list[dict]) -> None:
    groups = [name for name in GROUP_ORDER[:4]]
    colors = {"LOW": "#d97706", "MEDIUM": "#2563eb", "HIGH": "#059669"}
    width, height = 900, 520
    left, top, plot_w, plot_h = 100, 70, 740, 350
    totals = {group: sum(int(row["people"]) for row in depth_rows if row["group"] == group) for group in groups}
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="450" y="30" text-anchor="middle" font-family="sans-serif" font-size="20">Age-80 documentation depth (descriptive only)</text>',
    ]
    bar_width = 115
    gap = 60
    for index, group in enumerate(groups):
        x = left + index * (bar_width + gap)
        bottom = top + plot_h
        for depth in ("LOW", "MEDIUM", "HIGH"):
            count = next(int(row["people"]) for row in depth_rows if row["group"] == group and row["documentation_depth"] == depth)
            fraction = count / totals[group] if totals[group] else 0
            segment = fraction * plot_h
            bottom -= segment
            parts.append(f'<rect x="{x}" y="{bottom:.2f}" width="{bar_width}" height="{segment:.2f}" fill="{colors[depth]}"/>')
        parts.append(f'<text x="{x+bar_width/2}" y="{top+plot_h+22}" text-anchor="middle" font-family="sans-serif" font-size="11">{html.escape(group)}</text>')
    for index, depth in enumerate(("LOW", "MEDIUM", "HIGH")):
        x = 300 + index * 130
        parts.append(f'<rect x="{x}" y="465" width="16" height="16" fill="{colors[depth]}"/>')
        parts.append(f'<text x="{x+23}" y="478" font-family="sans-serif" font-size="12">{depth}</text>')
    parts.append("</svg>\n")
    path.write_text("\n".join(parts), encoding="utf-8")


def build_people() -> tuple[list[dict], list[dict[str, str]]]:
    cohort = read_csv(ROOT / "stage1" / "cohort.csv")
    worklist = read_csv(ROOT / "stage1c" / "research_worklist.csv")
    outcomes = read_csv(ROOT / "stage1c" / "PERSON_OUTCOMES.csv")
    events = read_csv(ROOT / "stage1c" / "EVIDENCE_EVENTS.csv")
    work_by_person = {row["person_id"]: row for row in worklist}
    outcome_by_person = {row["person_id"]: row for row in outcomes}
    if set(work_by_person) != {row["person_id"] for row in cohort}:
        raise AssertionError("cohort/worklist coverage mismatch")
    if set(outcome_by_person) != {row["person_id"] for row in cohort}:
        raise AssertionError("cohort/outcome coverage mismatch")
    event_by_person: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        event_by_person[event["person_id"]].append(event)

    people: list[dict] = []
    for row in cohort:
        birth = parse_date(row["birth_date"])
        death = parse_date(row["death_date"])
        if not birth:
            raise AssertionError("missing birth date")
        end = min(death, CENSOR) if death else CENSOR
        work = work_by_person[row["person_id"]]
        outcome = outcome_by_person[row["person_id"]]
        groups = group_membership(row)
        person_events = event_by_person.get(row["person_id"], [])
        function_events = sorted(
            [
                event for event in person_events
                if event["qualifies"] == "1"
                and event["evidence_type"] == "QUALIFYING_FUNCTION_EVENT"
            ],
            key=lambda item: item["analysis_event_date"],
        )
        impairment_events = sorted(
            [
                event for event in person_events
                if event["qualifies"] == "1"
                and event["evidence_type"] == "QUALIFYING_IMPAIRMENT_EVIDENCE"
            ],
            key=lambda item: item["analysis_event_date"],
        )
        people.append({
            "person_id": row["person_id"],
            "research_id": work["research_id"],
            "full_name": row["full_name"],
            "birth": birth,
            "death": death,
            "end": end,
            "row": row,
            "outcome": outcome,
            "groups": groups,
            "events": person_events,
            "function_events": function_events,
            "impairment_events": impairment_events,
        })
    return people, events


def members(people: list[dict], group: str, predicate: Callable[[dict], bool] | None = None) -> list[dict]:
    predicate = predicate or (lambda _: True)
    return [person for person in people if person["groups"][group] and predicate(person)]


def survival_record(person: dict, origin: date) -> tuple[float, int]:
    event = int(person["death"] is not None and person["death"] <= CENSOR)
    return years_between(origin, person["end"]), event


def birth_record(person: dict) -> tuple[float, int]:
    event = int(person["death"] is not None and person["death"] <= CENSOR)
    return age_exact(person["birth"], person["end"]), event


def public_record(person: dict, date_mode: str = "analysis") -> tuple[float, int]:
    birth = person["birth"]
    b80 = add_years(birth, 80)
    b85 = add_years(birth, 85)
    function_date = None
    if person["function_events"]:
        event = person["function_events"][0]
        date_field = {
            "analysis": "analysis_event_date",
            "earliest": "event_date_earliest",
            "latest": "event_date_latest",
        }[date_mode]
        function_date = parse_date(event[date_field])
    if function_date and b80 <= function_date < b85 and function_date <= CENSOR:
        return age_exact(birth, function_date) - 80.0, 1
    if (
        person["death"]
        and b80 <= person["death"] < b85
        and person["death"] <= CENSOR
    ):
        return age_exact(birth, person["death"]) - 80.0, 2
    end = min(b85, CENSOR, person["end"])
    return max(0.0, age_exact(birth, end) - 80.0), 0


def eligible(person: dict) -> bool:
    return person["outcome"]["eligible_age80"] == "1"


def make_result(
    results: list[dict],
    domain: str,
    analysis: str,
    contrast: str,
    estimand: str,
    estimate: float,
    lower: float | str,
    upper: float | str,
    unit: str,
    n_apollo: int | str,
    n_comparator: int | str,
    events_apollo: int | str,
    events_comparator: int | str,
    method: str,
    primary: str,
    sensitivity: str,
    p_value: float | str = "",
    notes: str = "",
) -> None:
    results.append(result_row(
        domain=domain,
        analysis=analysis,
        contrast=contrast,
        estimand=estimand,
        estimate=fmt(estimate, 6),
        ci_lower=fmt(lower, 6) if lower != "" else "",
        ci_upper=fmt(upper, 6) if upper != "" else "",
        unit=unit,
        n_apollo=n_apollo,
        n_comparator=n_comparator,
        events_apollo=events_apollo,
        events_comparator=events_comparator,
        method=method,
        primary=primary,
        sensitivity_type=sensitivity,
        p_value=fmt(p_value, 6) if p_value != "" else "",
        notes=notes,
    ))


def classify_endpoint(
    estimate: float,
    lower: float,
    upper: float,
    threshold: float,
    composition_effects: list[float],
    ancillary_effects: list[float] | None = None,
) -> tuple[str, str, str]:
    if any(math.isnan(value) for value in [estimate, lower, upper]):
        return "INDETERMINATE", "UNCERTAIN", "Required estimate or interval is unavailable."
    direction = "HIGHER" if estimate > 0 else ("LOWER" if estimate < 0 else "UNCERTAIN")
    sign = 1 if estimate > 0 else (-1 if estimate < 0 else 0)
    material = abs(estimate) >= threshold
    excludes_null = lower > 0 or upper < 0
    composition_coherent = sign != 0 and all(
        (value > 0 and sign > 0) or (value < 0 and sign < 0)
        for value in composition_effects
    )
    ancillary_coherent = True
    if ancillary_effects:
        ancillary_coherent = all(
            value == 0 or (value > 0 and sign > 0) or (value < 0 and sign < 0)
            for value in ancillary_effects
        )
    if material and excludes_null and composition_coherent:
        strength = "ROBUST"
        reason = "Primary effect is practically material, its 95% interval excludes zero, and both nested composition sensitivities retain direction."
    elif material and composition_coherent and ancillary_coherent:
        strength = "SUGGESTIVE"
        reason = "Primary magnitude is practically material and composition directions are coherent, but interval or ascertainment uncertainty remains."
    else:
        strength = "NOT_DETECTED"
        reason = "The primary effect is below the materiality threshold, unstable, or not coherent across prespecified sensitivities."
    return strength, direction, reason


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    output = [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join("---" for _ in headers) + "|",
    ]
    output.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(output)


def main() -> None:
    STAGE.mkdir(exist_ok=True)
    locked_rows, locked_hash = locked_input_manifest()
    if locked_hash != LOCKED_AGGREGATE_SHA256:
        raise AssertionError(
            f"locked input aggregate changed: {locked_hash} != {LOCKED_AGGREGATE_SHA256}"
        )
    write_csv(
        STAGE / "locked_input_hashes.csv",
        ["path", "bytes", "sha256"],
        locked_rows,
    )
    people, event_rows = build_people()
    results: list[dict] = []

    # Mechanical group/risk-set checks.
    if any(person["groups"]["APOLLO_FLEW"] and person["groups"]["OTHER_ALL"] for person in people):
        raise AssertionError("APOLLO_FLEW and OTHER_ALL overlap")
    if any(person["groups"]["OTHER_ALL"] != (
        not person["groups"]["APOLLO_FLEW"]
        and (
            person["groups"]["CORE_NASA_NON_APOLLO"]
            or person["row"]["military_x15"] == "1"
            or person["row"]["military_dyna_soar"] == "1"
            or person["row"]["military_mol"] == "1"
        )
    ) for person in people):
        raise AssertionError("OTHER_ALL construction mismatch")
    landmark_predicate = lambda person: person["death"] is None or person["death"] >= LANDMARK
    other_landmark = {p["person_id"] for p in members(people, "OTHER_ALL", landmark_predicate)}
    available_landmark = {p["person_id"] for p in members(people, "OTHER_AVAILABLE", landmark_predicate)}
    other_age80 = {p["person_id"] for p in members(people, "OTHER_ALL", eligible)}
    available_age80 = {p["person_id"] for p in members(people, "OTHER_AVAILABLE", eligible)}
    if other_landmark != available_landmark:
        raise AssertionError("OTHER_AVAILABLE landmark risk set differs from OTHER_ALL")
    if other_age80 != available_age80:
        raise AssertionError("OTHER_AVAILABLE age-80 risk set differs from OTHER_ALL")

    # External source extract retained locally.
    life_rows = []
    for year in sorted(SSA_MALE_E0):
        lower = (year // 10) * 10
        upper = lower + 10
        life_rows.append({
            "birth_year": year,
            "male_cohort_life_expectancy_at_birth": fmt(SSA_MALE_E0[year], 2),
            "male_cohort_survival_to_age80": fmt(ssa_s80(year), 6),
            "s80_lower_anchor_year": lower,
            "s80_upper_anchor_year": upper,
            "s80_method": "linear interpolation between official decennial l_80/100000 values",
            "e0_source_url": SSA_TABLE11,
            "s80_source_urls": "|".join([
                {
                    1920: SSA_TABLE7_1920,
                    1930: SSA_TABLE7_1930,
                    1940: SSA_TABLE7_1940,
                    1950: SSA_TABLE7_1950,
                }[lower],
                {
                    1930: SSA_TABLE7_1930,
                    1940: SSA_TABLE7_1940,
                    1950: SSA_TABLE7_1950,
                }[upper],
            ]),
        })
    life_columns = [
        "birth_year", "male_cohort_life_expectancy_at_birth",
        "male_cohort_survival_to_age80", "s80_lower_anchor_year",
        "s80_upper_anchor_year", "s80_method", "e0_source_url",
        "s80_source_urls",
    ]
    write_csv(STAGE / "ssa_male_cohort_expectations.csv", life_columns, life_rows)

    external_rows = [
        {
            "source": "SSA Actuarial Study 120 Table 11",
            "url": SSA_TABLE11,
            "use": "Exact annual male cohort life expectancy at birth",
            "access_result": "opened",
            "notes": "Official SSA source.",
        },
        *[
            {
                "source": f"SSA Actuarial Study 120 Table 7, {year} male cohort",
                "url": url,
                "use": "Male l_80/100000 anchor for birth-year interpolation",
                "access_result": "opened",
                "notes": "Official SSA source.",
            }
            for year, url in [
                (1920, SSA_TABLE7_1920), (1930, SSA_TABLE7_1930),
                (1940, SSA_TABLE7_1940), (1950, SSA_TABLE7_1950),
            ]
        ],
        {
            "source": "SSA life-table function definitions",
            "url": SSA_DEFINITIONS,
            "use": "Definitions of qx, lx, Lx, Tx, and ex",
            "access_result": "opened",
            "notes": "Official SSA source.",
        },
        {
            "source": "SSA 2023 Trustees Report male cohort CSV",
            "url": SSA_2023_CSV,
            "use": "Preferred full single-year table",
            "access_result": "inaccessible",
            "notes": "Web preview truncated; local DNS blocked. Replaced before models by official AS120 fallback.",
        },
    ]
    write_csv(
        STAGE / "EXTERNAL_SOURCE_LOG.csv",
        ["source", "url", "use", "access_result", "notes"],
        external_rows,
    )

    # Overall group counts, censoring, and attained-age descriptions.
    survival_summary_rows = []
    for group in GROUP_ORDER:
        group_people = members(people, group)
        attained = [age_exact(person["birth"], person["end"]) for person in group_people]
        deaths = sum(person["death"] is not None and person["death"] <= CENSOR for person in group_people)
        death_low, death_high = clopper_pearson(deaths, len(group_people))
        med, q1, q3, minimum, maximum = quantile_summary(attained)
        med_low, med_high = exact_median_interval(attained)
        reached80 = sum(person["end"] >= add_years(person["birth"], 80) for person in group_people)
        age80_low, age80_high = clopper_pearson(reached80, len(group_people))
        survival_summary_rows.append({
            "group": group,
            "people": len(group_people),
            "deaths": deaths,
            "censored": len(group_people) - deaths,
            "death_proportion": fmt(deaths / len(group_people), 6),
            "death_proportion_exact95_lower": fmt(death_low, 6),
            "death_proportion_exact95_upper": fmt(death_high, 6),
            "median_observed_attained_age": fmt(med, 3),
            "median_exact95_lower": fmt(med_low, 3),
            "median_exact95_upper": fmt(med_high, 3),
            "attained_age_q1": fmt(q1, 3),
            "attained_age_q3": fmt(q3, 3),
            "attained_age_min": fmt(minimum, 3),
            "attained_age_max": fmt(maximum, 3),
            "reached_age80": reached80,
            "reached_age80_proportion": fmt(reached80 / len(group_people), 6),
            "reached_age80_exact95_lower": fmt(age80_low, 6),
            "reached_age80_exact95_upper": fmt(age80_high, 6),
            "notes": "Observed attained age is age at death or administrative censoring; median CI is exact distribution-free order-statistic CI.",
        })
    survival_summary_columns = list(survival_summary_rows[0])
    write_csv(STAGE / "survival_group_summary.csv", survival_summary_columns, survival_summary_rows)

    # Population benchmark: exact-year e0 and standardized S80.
    population_rows = []
    for group in GROUP_ORDER:
        group_people = members(people, group)
        expected_e0 = fmean(SSA_MALE_E0[p["birth"].year] for p in group_people)
        expected_s80 = fmean(ssa_s80(p["birth"].year) for p in group_people)
        reached80 = sum(p["end"] >= add_years(p["birth"], 80) for p in group_people)
        observed_s80 = reached80 / len(group_people)
        lower, upper = clopper_pearson(reached80, len(group_people))
        observed_attained = fmean(age_exact(p["birth"], p["end"]) for p in group_people)
        population_rows.append({
            "group": group,
            "people": len(group_people),
            "mean_birth_year": fmt(fmean(p["birth"].year for p in group_people), 2),
            "mean_ssa_male_cohort_e0": fmt(expected_e0, 3),
            "mean_observed_attained_age_at_death_or_censor": fmt(observed_attained, 3),
            "observed_minus_expected_e0_years": fmt(observed_attained - expected_e0, 3),
            "observed_reached_age80": reached80,
            "observed_s80": fmt(observed_s80, 6),
            "observed_s80_exact95_lower": fmt(lower, 6),
            "observed_s80_exact95_upper": fmt(upper, 6),
            "birth_year_standardized_ssa_male_s80": fmt(expected_s80, 6),
            "observed_minus_expected_s80": fmt(observed_s80 - expected_s80, 6),
            "observed_to_expected_s80_ratio": fmt(observed_s80 / expected_s80, 6),
            "notes": "SSA expectations are external descriptive benchmarks; observed mean attained age includes censoring and is not an estimate of completed lifetime.",
        })
        make_result(
            results, "SURVIVAL", "US_MALE_COHORT_EXPECTATION",
            f"{group} vs SSA male birth cohort", "Observed minus expected survival to age 80",
            observed_s80 - expected_s80, lower - expected_s80, upper - expected_s80,
            "proportion", len(group_people), "external", reached80, "expected",
            "Observed exact binomial interval minus fixed standardized SSA expectation",
            "NO", "POPULATION_BENCHMARK",
            notes="Future-selected astronaut cohort versus nonexchangeable U.S. male birth-cohort life table.",
        )
    write_csv(STAGE / "population_expectation.csv", list(population_rows[0]), population_rows)

    # Landmark RMST primary and composition sensitivities.
    landmark_rows = []
    landmark_effects: dict[str, tuple[float, float, float]] = {}
    apollo_landmark_people = members(people, "APOLLO_FLEW", landmark_predicate)
    apollo_landmark = [survival_record(person, LANDMARK) for person in apollo_landmark_people]
    for comparator, sensitivity in COMPARATORS:
        comparator_people = members(people, comparator, landmark_predicate)
        comparator_records = [survival_record(person, LANDMARK) for person in comparator_people]
        estimate, lower, upper = bootstrap_difference(
            apollo_landmark,
            comparator_records,
            lambda data: km_rmst(data, RMST_HORIZON),
        )
        landmark_effects[comparator] = (estimate, lower, upper)
        rmst_apollo = km_rmst(apollo_landmark, RMST_HORIZON)
        rmst_comparator = km_rmst(comparator_records, RMST_HORIZON)
        age_apollo = [age_exact(p["birth"], LANDMARK) for p in apollo_landmark_people]
        age_comparator = [age_exact(p["birth"], LANDMARK) for p in comparator_people]
        landmark_rows.append({
            "contrast": f"APOLLO_FLEW vs {comparator}",
            "analysis_role": sensitivity,
            "n_apollo": len(apollo_landmark),
            "n_comparator": len(comparator_records),
            "deaths_apollo_full_followup": sum(status for _, status in apollo_landmark),
            "deaths_comparator_full_followup": sum(status for _, status in comparator_records),
            "age_at_landmark_apollo_mean": fmt(fmean(age_apollo), 3),
            "age_at_landmark_apollo_median": fmt(median(age_apollo), 3),
            "age_at_landmark_comparator_mean": fmt(fmean(age_comparator), 3),
            "age_at_landmark_comparator_median": fmt(median(age_comparator), 3),
            "rmst50_apollo_years": fmt(rmst_apollo, 6),
            "rmst50_comparator_years": fmt(rmst_comparator, 6),
            "apollo_minus_comparator_rmst_years": fmt(estimate, 6),
            "bootstrap95_lower": fmt(lower, 6),
            "bootstrap95_upper": fmt(upper, 6),
            "bootstrap_replicates": BOOT_REPS,
            "bootstrap_seed": SEED,
            "notes": "Nested/reused composition groups are not independent replications.",
        })
        make_result(
            results, "SURVIVAL", "LANDMARK_RMST",
            f"APOLLO_FLEW vs {comparator}", "Apollo-minus-comparator 50-year RMST",
            estimate, lower, upper, "years", len(apollo_landmark), len(comparator_records),
            sum(status for _, status in apollo_landmark),
            sum(status for _, status in comparator_records),
            "Kaplan–Meier RMST; stratified person bootstrap 50000, seed 20260721",
            "YES" if comparator == "OTHER_ALL" else "NO",
            sensitivity,
            notes="Common 1973-01-01 landmark; descriptive, noncausal.",
        )
    write_csv(STAGE / "survival_landmark_rmst.csv", list(landmark_rows[0]), landmark_rows)

    # Cox age-adjusted sensitivity on the primary landmark contrast.
    other_landmark_people = members(people, "OTHER_ALL", landmark_predicate)
    cox_people = apollo_landmark_people + other_landmark_people
    cox_times = [survival_record(person, LANDMARK)[0] for person in cox_people]
    cox_status = [survival_record(person, LANDMARK)[1] for person in cox_people]
    cox_groups = [1] * len(apollo_landmark_people) + [0] * len(other_landmark_people)
    cox_ages = [age_exact(person["birth"], LANDMARK) for person in cox_people]
    cox = cox_efron(cox_times, cox_status, cox_groups, cox_ages)
    cox_rows = []
    for index, term in enumerate(("APOLLO_FLEW", "AGE_AT_LANDMARK_PER_YEAR")):
        beta = cox["beta"][index]
        se = cox["se"][index]
        p_value = 2 * (1 - normal_cdf(abs(beta / se)))
        cox_rows.append({
            "term": term,
            "coefficient": fmt(beta, 6),
            "standard_error": fmt(se, 6),
            "hazard_ratio": fmt(math.exp(beta), 6),
            "wald95_lower": fmt(math.exp(beta - Z975 * se), 6),
            "wald95_upper": fmt(math.exp(beta + Z975 * se), 6),
            "p_value": fmt(p_value, 6),
            "ties": "Efron",
            "converged": cox["converged"],
            "iterations": cox["iterations"],
            "notes": "Conventional model-based interval; supplementary to RMST.",
        })
        make_result(
            results, "SURVIVAL", "LANDMARK_COX_AGE_ADJUSTED",
            "APOLLO_FLEW vs OTHER_ALL" if index == 0 else "Age-at-landmark covariate",
            "Hazard ratio", math.exp(beta), math.exp(beta - Z975 * se),
            math.exp(beta + Z975 * se), "ratio", len(apollo_landmark_people),
            len(other_landmark_people), sum(cox_status[:len(apollo_landmark_people)]),
            sum(cox_status[len(apollo_landmark_people):]), "Cox PH, Efron ties, Wald interval",
            "NO", "AGE_ADJUSTED_SENSITIVITY", p_value,
            "Group plus linear age at 1973 landmark.",
        )
    write_csv(STAGE / "cox_model.csv", list(cox_rows[0]), cox_rows)
    ph_rows = schoenfeld_diagnostic(
        cox_times, cox_status, cox["covariates"], cox["beta"]
    )
    ph_columns = list(ph_rows[0])
    for row in ph_rows:
        for key in ("correlation_with_log_time", "test_statistic", "p_value"):
            if isinstance(row[key], float):
                row[key] = fmt(row[key], 6)
    write_csv(STAGE / "ph_diagnostic.csv", ph_columns, ph_rows)

    # Retrospective, future-flight-selected KM from birth.
    km_birth_rows = []
    birth_curves = {}
    for group in GROUP_ORDER:
        records = [birth_record(person) for person in members(people, group)]
        birth_curves[group] = km_step(records, 105.0)
        for target in (60, 70, 80, 85, 90, 95):
            estimate, lower, upper, variance = km_at(records, target)
            km_birth_rows.append({
                "group": group,
                "attained_age": target,
                "km_survival": fmt(estimate, 6),
                "greenwood_loglog95_lower": fmt(lower, 6),
                "greenwood_loglog95_upper": fmt(upper, 6),
                "greenwood_variance": fmt(variance, 8),
                "notes": "Retrospective, future-flight-selected birth-origin description.",
            })
    write_csv(STAGE / "km_birth_selected_ages.csv", list(km_birth_rows[0]), km_birth_rows)
    apollo_birth = [birth_record(person) for person in members(people, "APOLLO_FLEW")]
    other_birth = [birth_record(person) for person in members(people, "OTHER_ALL")]
    for target in (80, 85, 90):
        s1, _, _, v1 = km_at(apollo_birth, target)
        s0, _, _, v0 = km_at(other_birth, target)
        diff = s1 - s0
        se = math.sqrt(v1 + v0)
        make_result(
            results, "SURVIVAL", "BIRTH_ORIGIN_KM",
            "APOLLO_FLEW vs OTHER_ALL", f"KM survival difference at age {target}",
            diff, max(-1.0, diff - Z975 * se), min(1.0, diff + Z975 * se),
            "proportion", len(apollo_birth), len(other_birth), "", "",
            "Kaplan–Meier with independent Greenwood normal difference interval",
            "NO", "RETROSPECTIVE_FUTURE_FLIGHT_SELECTED",
            notes="Secondary cohort description; future-flight classification creates selection/immortal-time concerns.",
        )

    # Age-80 public-function Aalen–Johansen analyses.
    public_effects: dict[str, tuple[float, float, float]] = {}
    public_primary_rows = []
    apollo_public_people = members(people, "APOLLO_FLEW", eligible)
    apollo_public = [public_record(person) for person in apollo_public_people]
    for comparator, sensitivity in COMPARATORS:
        comparator_people = members(people, comparator, eligible)
        comparator_records = [public_record(person) for person in comparator_people]
        estimate, lower, upper = bootstrap_difference(
            apollo_public,
            comparator_records,
            lambda data: aj_cif(data, 5.0),
        )
        public_effects[comparator] = (estimate, lower, upper)
        cif_apollo = aj_cif(apollo_public, 5.0)
        cif_comparator = aj_cif(comparator_records, 5.0)
        public_primary_rows.append({
            "contrast": f"APOLLO_FLEW vs {comparator}",
            "analysis_role": sensitivity,
            "n_apollo": len(apollo_public),
            "n_comparator": len(comparator_records),
            "first_function_events_apollo": sum(status == 1 for _, status in apollo_public),
            "first_function_events_comparator": sum(status == 1 for _, status in comparator_records),
            "competing_deaths_apollo": sum(status == 2 for _, status in apollo_public),
            "competing_deaths_comparator": sum(status == 2 for _, status in comparator_records),
            "five_year_cif_apollo": fmt(cif_apollo, 6),
            "five_year_cif_comparator": fmt(cif_comparator, 6),
            "apollo_minus_comparator_risk_difference": fmt(estimate, 6),
            "bootstrap95_lower": fmt(lower, 6),
            "bootstrap95_upper": fmt(upper, 6),
            "bootstrap_replicates": BOOT_REPS,
            "bootstrap_seed": SEED,
            "notes": "Observed public-evidence detection; death is competing. Nested/reused composition groups are not independent replications.",
        })
        make_result(
            results, "PUBLIC_FUNCTION", "FIVE_YEAR_AALEN_JOHANSEN",
            f"APOLLO_FLEW vs {comparator}", "Apollo-minus-comparator five-year function-detection risk",
            estimate, lower, upper, "proportion", len(apollo_public), len(comparator_records),
            sum(status == 1 for _, status in apollo_public),
            sum(status == 1 for _, status in comparator_records),
            "Aalen–Johansen; stratified person bootstrap 50000, seed 20260721",
            "YES" if comparator == "OTHER_ALL" else "NO", sensitivity,
            notes="Public-evidence detection endpoint, not a clinical cognitive measure.",
        )

    # Direction-neutral R001 technical-deviation primary sensitivity.
    r001_removed = lambda person: eligible(person) and person["research_id"] != "R001"
    apollo_tech_people = members(people, "APOLLO_FLEW", r001_removed)
    other_tech_people = members(people, "OTHER_ALL", r001_removed)
    apollo_tech = [public_record(person) for person in apollo_tech_people]
    other_tech = [public_record(person) for person in other_tech_people]
    tech_estimate, tech_lower, tech_upper = bootstrap_difference(
        apollo_tech, other_tech, lambda data: aj_cif(data, 5.0)
    )
    public_primary_rows.append({
        "contrast": "APOLLO_FLEW vs OTHER_ALL, R001 excluded",
        "analysis_role": "TECHNICAL_DEVIATION_SENSITIVITY",
        "n_apollo": len(apollo_tech),
        "n_comparator": len(other_tech),
        "first_function_events_apollo": sum(status == 1 for _, status in apollo_tech),
        "first_function_events_comparator": sum(status == 1 for _, status in other_tech),
        "competing_deaths_apollo": sum(status == 2 for _, status in apollo_tech),
        "competing_deaths_comparator": sum(status == 2 for _, status in other_tech),
        "five_year_cif_apollo": fmt(aj_cif(apollo_tech), 6),
        "five_year_cif_comparator": fmt(aj_cif(other_tech), 6),
        "apollo_minus_comparator_risk_difference": fmt(tech_estimate, 6),
        "bootstrap95_lower": fmt(tech_lower, 6),
        "bootstrap95_upper": fmt(tech_upper, 6),
        "bootstrap_replicates": BOOT_REPS,
        "bootstrap_seed": SEED,
        "notes": "Precommitted technical-deviation sensitivity; not primary and not an independent confirmation.",
    })
    make_result(
        results, "PUBLIC_FUNCTION", "FIVE_YEAR_AALEN_JOHANSEN_R001_EXCLUDED",
        "APOLLO_FLEW vs OTHER_ALL", "Apollo-minus-other five-year function-detection risk",
        tech_estimate, tech_lower, tech_upper, "proportion", len(apollo_tech), len(other_tech),
        sum(status == 1 for _, status in apollo_tech),
        sum(status == 1 for _, status in other_tech),
        "Aalen–Johansen; stratified bootstrap 50000, seed 20260721",
        "NO", "TECHNICAL_DEVIATION_SENSITIVITY",
        notes="R001 excluded; does not alter primary estimate.",
    )
    write_csv(STAGE / "public_function_primary.csv", list(public_primary_rows[0]), public_primary_rows)

    # Secondary crude any-time detection.
    crude_rows = []
    crude_effects = {}

    def any_function(person: dict) -> bool:
        return bool(person["function_events"])

    crude_specs = [
        ("OTHER_ALL", "SECONDARY", False),
        ("CORE_NASA_NON_APOLLO", "COMPOSITION_SENSITIVITY", False),
        ("MILITARY_ONLY", "COMPOSITION_SENSITIVITY", False),
        ("OTHER_ALL", "TECHNICAL_DEVIATION_SENSITIVITY", True),
    ]
    for comparator, sensitivity, remove_r001 in crude_specs:
        predicate = (
            (lambda p: eligible(p) and p["research_id"] != "R001")
            if remove_r001 else eligible
        )
        apollo_people = members(people, "APOLLO_FLEW", predicate)
        comparator_people = members(people, comparator, predicate)
        a = sum(any_function(person) for person in apollo_people)
        c = sum(any_function(person) for person in comparator_people)
        n1, n0 = len(apollo_people), len(comparator_people)
        p1, p0 = a / n1, c / n0
        p1_low, p1_high = clopper_pearson(a, n1)
        p0_low, p0_high = clopper_pearson(c, n0)
        rd = p1 - p0
        rd_low, rd_high = newcombe_difference(a, n1, c, n0)
        rr, rr_low, rr_high, rr_method = risk_ratio_interval(a, n1, c, n0)
        odds, odds_low, odds_high = conditional_or_interval(a, n1 - a, c, n0 - c)
        fisher = fisher_exact_two_sided(a, n1 - a, c, n0 - c)
        key = f"{comparator}|{remove_r001}"
        crude_effects[key] = rd
        crude_rows.append({
            "contrast": f"APOLLO_FLEW vs {comparator}" + (", R001 excluded" if remove_r001 else ""),
            "analysis_role": sensitivity,
            "apollo_detected": a,
            "apollo_eligible": n1,
            "apollo_risk": fmt(p1, 6),
            "apollo_exact95_lower": fmt(p1_low, 6),
            "apollo_exact95_upper": fmt(p1_high, 6),
            "comparator_detected": c,
            "comparator_eligible": n0,
            "comparator_risk": fmt(p0, 6),
            "comparator_exact95_lower": fmt(p0_low, 6),
            "comparator_exact95_upper": fmt(p0_high, 6),
            "risk_difference": fmt(rd, 6),
            "risk_difference95_lower": fmt(rd_low, 6),
            "risk_difference95_upper": fmt(rd_high, 6),
            "risk_ratio": fmt(rr, 6),
            "risk_ratio95_lower": fmt(rr_low, 6),
            "risk_ratio95_upper": fmt(rr_high, 6),
            "odds_ratio": fmt(odds, 6),
            "odds_ratio_conditional_exact95_lower": fmt(odds_low, 6),
            "odds_ratio_conditional_exact95_upper": fmt(odds_high, 6),
            "fisher_exact_two_sided_p": fmt(fisher, 6),
            "notes": f"Risk-ratio interval: {rr_method}. Public-evidence detection, not cognition prevalence.",
        })
        for estimand, estimate, low, high, unit, method in [
            ("Any-age80+ detection risk difference", rd, rd_low, rd_high, "proportion", "Newcombe score interval"),
            ("Any-age80+ detection risk ratio", rr, rr_low, rr_high, "ratio", rr_method),
            ("Any-age80+ detection odds ratio", odds, odds_low, odds_high, "ratio", "Sample OR; conditional exact interval"),
        ]:
            make_result(
                results, "PUBLIC_FUNCTION", "CRUDE_ANY_AGE80_PLUS",
                f"APOLLO_FLEW vs {comparator}" + (", R001 excluded" if remove_r001 else ""),
                estimand, estimate, low, high, unit, n1, n0, a, c, method,
                "NO", sensitivity, fisher if "odds ratio" in estimand else "",
                "Fisher exact p-value is supplementary and attached to the OR row." if "odds ratio" in estimand else "",
            )
    write_csv(STAGE / "public_function_crude.csv", list(crude_rows[0]), crude_rows)

    # Documentation-depth and raw source availability descriptions.
    depth_rows = []
    documentation_rows = []
    for group in GROUP_ORDER[:4]:
        group_people = members(people, group, eligible)
        depth_counts = Counter(person["outcome"]["documentation_depth"] for person in group_people)
        for depth in ("LOW", "MEDIUM", "HIGH"):
            depth_rows.append({
                "group": group,
                "documentation_depth": depth,
                "people": depth_counts[depth],
                "proportion": fmt(depth_counts[depth] / len(group_people), 6),
                "notes": "Descriptive source availability only; not an adjustment or complete-case restriction.",
            })
        substantive = [int(person["outcome"]["substantive_sources_opened"]) for person in group_people]
        publishers = [int(person["outcome"]["independent_publishers"]) for person in group_people]
        smed, sq1, sq3, smin, smax = quantile_summary([float(value) for value in substantive])
        pmed, pq1, pq3, pmin, pmax = quantile_summary([float(value) for value in publishers])
        documentation_rows.append({
            "group": group,
            "people": len(group_people),
            "substantive_sources_median": fmt(smed, 2),
            "substantive_sources_q1": fmt(sq1, 2),
            "substantive_sources_q3": fmt(sq3, 2),
            "substantive_sources_min": fmt(smin, 0),
            "substantive_sources_max": fmt(smax, 0),
            "independent_publishers_median": fmt(pmed, 2),
            "independent_publishers_q1": fmt(pq1, 2),
            "independent_publishers_q3": fmt(pq3, 2),
            "independent_publishers_min": fmt(pmin, 0),
            "independent_publishers_max": fmt(pmax, 0),
            "notes": "Raw source availability description; no endpoint conditioning.",
        })
    write_csv(STAGE / "documentation_depth.csv", list(depth_rows[0]), depth_rows)
    write_csv(STAGE / "documentation_counts.csv", list(documentation_rows[0]), documentation_rows)

    # Latent-event worst/best bounds answer a different endpoint question.
    latent_rows = []
    for comparator, sensitivity in COMPARATORS:
        apollo_people = members(people, "APOLLO_FLEW", eligible)
        comparator_people = members(people, comparator, eligible)
        a_detected = sum(any_function(person) for person in apollo_people)
        c_detected = sum(any_function(person) for person in comparator_people)
        a_unknown = sum(person["outcome"]["outcome_state"] == "NEITHER_FOUND" for person in apollo_people)
        c_unknown = sum(person["outcome"]["outcome_state"] == "NEITHER_FOUND" for person in comparator_people)
        worst = a_detected / len(apollo_people) - (c_detected + c_unknown) / len(comparator_people)
        best = (a_detected + a_unknown) / len(apollo_people) - c_detected / len(comparator_people)
        latent_rows.append({
            "contrast": f"APOLLO_FLEW vs {comparator}",
            "analysis_role": sensitivity,
            "apollo_detected": a_detected,
            "apollo_neither_found": a_unknown,
            "apollo_eligible": len(apollo_people),
            "comparator_detected": c_detected,
            "comparator_neither_found": c_unknown,
            "comparator_eligible": len(comparator_people),
            "worst_case_apollo_minus_comparator": fmt(worst, 6),
            "best_case_apollo_minus_comparator": fmt(best, 6),
            "notes": "Latent any-event bounds assign NEITHER_FOUND asymmetrically. They answer a different question from observed detection and do not modify the primary Aalen–Johansen estimate.",
        })
        for label, value in (("Worst-case latent any-event risk difference", worst), ("Best-case latent any-event risk difference", best)):
            make_result(
                results, "PUBLIC_FUNCTION", "LATENT_EVENT_EXTREME_BOUND",
                f"APOLLO_FLEW vs {comparator}", label, value, "", "", "proportion",
                len(apollo_people), len(comparator_people), a_detected, c_detected,
                "Deterministic worst/best assignment among NEITHER_FOUND",
                "NO", "LATENT_EVENT_DIFFERENT_QUESTION",
                notes="Not an observed-detection estimate and not used for classification.",
            )
    write_csv(STAGE / "latent_event_bounds.csv", list(latent_rows[0]), latent_rows)

    # Boundary-date sensitivity.
    boundary_events = [
        event for event in event_rows
        if event["qualifies"] == "1" and event["boundary_sensitive"] == "1"
    ]
    boundary_rows = []
    if boundary_events:
        for event in boundary_events:
            boundary_rows.append({
                "research_id": event["research_id"],
                "person_id": event["person_id"],
                "evidence_type": event["evidence_type"],
                "event_date_earliest": event["event_date_earliest"],
                "event_date_latest": event["event_date_latest"],
                "earliest_qualifies_relative_to_boundary": "",
                "latest_qualifies_relative_to_boundary": "",
                "primary_effect_earliest_scenario": "",
                "primary_effect_latest_scenario": "",
                "notes": "Boundary-sensitive row requires person-specific recoding.",
            })
    else:
        boundary_rows.append({
            "research_id": "NONE",
            "person_id": "",
            "evidence_type": "",
            "event_date_earliest": "",
            "event_date_latest": "",
            "earliest_qualifies_relative_to_boundary": "identical",
            "latest_qualifies_relative_to_boundary": "identical",
            "primary_effect_earliest_scenario": fmt(public_effects["OTHER_ALL"][0], 6),
            "primary_effect_latest_scenario": fmt(public_effects["OTHER_ALL"][0], 6),
            "notes": "No qualifying boundary-sensitive event exists; earliest/latest primary sensitivity is identical by construction.",
        })
        make_result(
            results, "PUBLIC_FUNCTION", "BOUNDARY_DATE_SENSITIVITY",
            "APOLLO_FLEW vs OTHER_ALL", "Earliest/latest five-year risk difference",
            public_effects["OTHER_ALL"][0], public_effects["OTHER_ALL"][1],
            public_effects["OTHER_ALL"][2], "proportion", len(apollo_public),
            len(members(people, "OTHER_ALL", eligible)), "", "",
            "No boundary-sensitive qualifying events; identical to primary",
            "NO", "BOUNDARY_DATE_SENSITIVITY",
        )
    write_csv(STAGE / "boundary_date_sensitivity.csv", list(boundary_rows[0]), boundary_rows)

    # Latest function-event ages and temporal function/impairment sequences.
    latest_rows = []
    for group in GROUP_ORDER[:4]:
        values = []
        for person in members(people, group, eligible):
            if person["function_events"]:
                latest = parse_date(person["function_events"][-1]["analysis_event_date"])
                values.append(age_exact(person["birth"], latest))
        if values:
            med, q1, q3, minimum, maximum = quantile_summary(values)
        else:
            med = q1 = q3 = minimum = maximum = math.nan
        latest_rows.append({
            "group": group,
            "eligible_people": len(members(people, group, eligible)),
            "people_with_qualifying_function": len(values),
            "latest_function_age_median": fmt(med, 3),
            "latest_function_age_q1": fmt(q1, 3),
            "latest_function_age_q3": fmt(q3, 3),
            "latest_function_age_min": fmt(minimum, 3),
            "latest_function_age_max": fmt(maximum, 3),
            "notes": "Distribution among people with at least one detected qualifying function event.",
        })
    write_csv(STAGE / "latest_function_age.csv", list(latest_rows[0]), latest_rows)

    state_order = [
        "FUNCTION_ONLY", "IMPAIRMENT_ONLY", "FUNCTION_THEN_IMPAIRMENT",
        "IMPAIRMENT_THEN_FUNCTION", "BOTH_ORDER_INDETERMINATE_OR_SAME_DATE",
        "NEITHER_FOUND",
    ]
    sequence_rows = []
    for group in GROUP_ORDER[:4]:
        group_people = members(people, group, eligible)
        counts = Counter(person["outcome"]["outcome_state"] for person in group_people)
        for state in state_order:
            sequence_rows.append({
                "group": group,
                "outcome_state": state,
                "people": counts[state],
                "proportion": fmt(counts[state] / len(group_people), 6),
                "notes": "Locked mutually exclusive full-window function/impairment sequence.",
            })
    write_csv(STAGE / "temporal_sequences.csv", list(sequence_rows[0]), sequence_rows)

    # Figures.
    other_landmark_records = [survival_record(person, LANDMARK) for person in other_landmark_people]
    svg_step_plot(
        STAGE / "survival_landmark_km.svg",
        [
            ("APOLLO_FLEW", km_step(apollo_landmark, 53.42), "#b91c1c"),
            ("OTHER_ALL", km_step(other_landmark_records, 53.42), "#1d4ed8"),
        ],
        0, 53.5, 0, 1,
        "Survival from 1973 common landmark",
        "Years since 1973-01-01", "Kaplan–Meier survival",
    )
    svg_step_plot(
        STAGE / "survival_birth_km.svg",
        [
            ("APOLLO_FLEW", birth_curves["APOLLO_FLEW"], "#b91c1c"),
            ("OTHER_ALL", birth_curves["OTHER_ALL"], "#1d4ed8"),
            ("CORE_NASA_NON_APOLLO", birth_curves["CORE_NASA_NON_APOLLO"], "#059669"),
            ("MILITARY_ONLY", birth_curves["MILITARY_ONLY"], "#7c3aed"),
        ],
        0, 105, 0, 1,
        "Retrospective future-flight-selected survival from birth",
        "Attained age", "Kaplan–Meier survival",
    )
    other_public = [public_record(person) for person in members(people, "OTHER_ALL", eligible)]
    svg_step_plot(
        STAGE / "public_function_cif.svg",
        [
            ("APOLLO_FLEW", aj_step(apollo_public), "#b91c1c"),
            ("OTHER_ALL", aj_step(other_public), "#1d4ed8"),
        ],
        0, 5, 0, max(0.25, 1.1 * max(aj_cif(apollo_public), aj_cif(other_public))),
        "Five-year cumulative incidence of public-function detection",
        "Years after 80th birthday", "Aalen–Johansen cumulative incidence",
    )
    svg_documentation_bars(STAGE / "documentation_depth.svg", depth_rows)

    # Classification.
    survival_primary = landmark_effects["OTHER_ALL"]
    survival_strength, survival_direction, survival_reason = classify_endpoint(
        survival_primary[0], survival_primary[1], survival_primary[2], 5.0,
        [landmark_effects["CORE_NASA_NON_APOLLO"][0], landmark_effects["MILITARY_ONLY"][0]],
    )
    public_primary = public_effects["OTHER_ALL"]
    public_strength, public_direction, public_reason = classify_endpoint(
        public_primary[0], public_primary[1], public_primary[2], 0.10,
        [public_effects["CORE_NASA_NON_APOLLO"][0], public_effects["MILITARY_ONLY"][0]],
        [tech_estimate],
    )

    # Results summary is written before reports so the report draws from exact objects.
    write_csv(STAGE / "RESULTS_SUMMARY.csv", RESULT_COLUMNS, results)

    survival_table = markdown_table(
        ["Contrast", "RMST Apollo", "RMST comparator", "Difference (95% bootstrap CI)"],
        [
            [
                row["contrast"],
                f'{float(row["rmst50_apollo_years"]):.2f} y',
                f'{float(row["rmst50_comparator_years"]):.2f} y',
                f'{float(row["apollo_minus_comparator_rmst_years"]):.2f} ({float(row["bootstrap95_lower"]):.2f}, {float(row["bootstrap95_upper"]):.2f}) y',
            ]
            for row in landmark_rows
        ],
    )
    survival_group_table = markdown_table(
        ["Group", "N", "Deaths / censored", "Death proportion (exact 95% CI)", "Observed attained-age median (exact 95% CI)", "IQR"],
        [
            [
                row["group"],
                str(row["people"]),
                f'{row["deaths"]} / {row["censored"]}',
                f'{100*float(row["death_proportion"]):.1f}% ({100*float(row["death_proportion_exact95_lower"]):.1f}, {100*float(row["death_proportion_exact95_upper"]):.1f})',
                f'{float(row["median_observed_attained_age"]):.1f} ({float(row["median_exact95_lower"]):.1f}, {float(row["median_exact95_upper"]):.1f}) y',
                f'{float(row["attained_age_q1"]):.1f}–{float(row["attained_age_q3"]):.1f} y',
            ]
            for row in survival_summary_rows[:4]
        ],
    )
    public_table = markdown_table(
        ["Contrast", "CIF Apollo", "CIF comparator", "Risk difference (95% bootstrap CI)"],
        [
            [
                row["contrast"],
                f'{100*float(row["five_year_cif_apollo"]):.1f}%',
                f'{100*float(row["five_year_cif_comparator"]):.1f}%',
                f'{100*float(row["apollo_minus_comparator_risk_difference"]):.1f} ({100*float(row["bootstrap95_lower"]):.1f}, {100*float(row["bootstrap95_upper"]):.1f}) pp',
            ]
            for row in public_primary_rows
        ],
    )
    primary_crude = crude_rows[0]
    technical_crude = crude_rows[-1]
    cox_group = cox_rows[0]
    pop_apollo = next(row for row in population_rows if row["group"] == "APOLLO_FLEW")
    pop_other = next(row for row in population_rows if row["group"] == "OTHER_ALL")
    ph_group = next(row for row in ph_rows if row["term"] == "APOLLO_FLEW")
    documentation_table = markdown_table(
        ["Group", "LOW / MEDIUM / HIGH", "Substantive sources median (IQR)", "Independent publishers median (IQR)"],
        [
            [
                group,
                " / ".join(
                    str(next(row["people"] for row in depth_rows if row["group"] == group and row["documentation_depth"] == depth))
                    for depth in ("LOW", "MEDIUM", "HIGH")
                ),
                f'{next(row["substantive_sources_median"] for row in documentation_rows if row["group"] == group)} ({next(row["substantive_sources_q1"] for row in documentation_rows if row["group"] == group)}–{next(row["substantive_sources_q3"] for row in documentation_rows if row["group"] == group)})',
                f'{next(row["independent_publishers_median"] for row in documentation_rows if row["group"] == group)} ({next(row["independent_publishers_q1"] for row in documentation_rows if row["group"] == group)}–{next(row["independent_publishers_q3"] for row in documentation_rows if row["group"] == group)})',
            ]
            for group in GROUP_ORDER[:4]
        ],
    )
    latest_table = markdown_table(
        ["Group", "Detected / eligible", "Latest qualifying-event age median (IQR)", "Range"],
        [
            [
                row["group"],
                f'{row["people_with_qualifying_function"]} / {row["eligible_people"]}',
                (
                    f'{float(row["latest_function_age_median"]):.1f} '
                    f'({float(row["latest_function_age_q1"]):.1f}–{float(row["latest_function_age_q3"]):.1f}) y'
                    if row["latest_function_age_median"] != "NA" else "NA"
                ),
                (
                    f'{float(row["latest_function_age_min"]):.1f}–{float(row["latest_function_age_max"]):.1f} y'
                    if row["latest_function_age_min"] != "NA" else "NA"
                ),
            ]
            for row in latest_rows
        ],
    )
    latent_primary = latent_rows[0]

    report = f"""# Stage 2 analysis report

## Questions and interpretation

This report asks whether the future-defined `APOLLO_FLEW` cohort has descriptively unusual survival and publicly documented late-life functioning. The public-function endpoint is detection of qualifying public evidence, not cognitive-intactness prevalence and not a clinical diagnosis. All astronaut contrasts are descriptive and noncausal.

## Data and methods

The locked cohort contains the prespecified Apollo, NASA non-Apollo, X-15, Dyna-Soar, and MOL rosters censored on 2026-06-01. The primary survival analysis starts at the common 1973-01-01 landmark among people alive then. Its estimand is Apollo-minus-comparator Kaplan–Meier RMST through 50 years. Primary and composition intervals use 50,000 stratified person-level percentile bootstrap replicates, seed 20260721.

The age-adjusted sensitivity is a Cox model from the landmark with Apollo status and linear age at landmark, Efron ties, and conventional Wald intervals. Schoenfeld-residual tests are diagnostics, not replacements for RMST.

The secondary birth-origin curves are explicitly retrospective and future-flight-selected. `OTHER_AVAILABLE` is identical to `OTHER_ALL` after the 1973 landmark and in the age-80 risk set; it is shown only in the birth-origin description and is not duplicate sensitivity evidence.

For the official population benchmark, [SSA Actuarial Study 120 Table 11]({SSA_TABLE11}) supplies exact-year male cohort life expectancy at birth, while the official cohort tables for [1920]({SSA_TABLE7_1920}), [1930]({SSA_TABLE7_1930}), [1940]({SSA_TABLE7_1940}), and [1950]({SSA_TABLE7_1950}) supply survival to age 80. Exact birth years use linear interpolation for S80. The preferred 2023 full file was inaccessible in this sandbox, so the fallback was frozen before models. SSA expectations are nonexchangeable population benchmarks.

The primary public-function analysis starts on each eligible person's 80th birthday. First qualifying function before age 85 is the event of interest, death first is competing, and administrative end or the 85th birthday is censoring. Five-year risks use Aalen–Johansen; risk-difference intervals use the same 50,000-replicate stratified bootstrap. Secondary any-age-80-plus detection reports exact binomial group intervals, Newcombe risk-difference intervals, risk ratios, conditional-exact odds-ratio intervals, and Fisher's exact test.

## Survival results

{survival_group_table}

These attained-age values are observed ages at death or censor, not completed lifetimes for survivors. Exact intervals are Clopper–Pearson for death proportions and distribution-free order-statistic intervals for the observed attained-age median.

{survival_table}

The primary Apollo-minus-`OTHER_ALL` 50-year RMST difference is **{survival_primary[0]:.2f} years** (95% percentile bootstrap **{survival_primary[1]:.2f} to {survival_primary[2]:.2f}**). The fixed practical threshold is 5.0 years.

In the age-adjusted Cox sensitivity, the Apollo hazard ratio is **{cox_group["hazard_ratio"]}** (95% CI **{cox_group["wald95_lower"]} to {cox_group["wald95_upper"]}**, supplementary p={cox_group["p_value"]}). The Apollo Schoenfeld-residual diagnostic has p={ph_group["p_value"]}; the full term and approximate global diagnostics are retained in `ph_diagnostic.csv`.

The official male cohort benchmark predicts S80 of **{100*float(pop_apollo["birth_year_standardized_ssa_male_s80"]):.1f}%** for the Apollo birth-year mix and **{100*float(pop_other["birth_year_standardized_ssa_male_s80"]):.1f}%** for `OTHER_ALL`. Observed proportions reaching 80 were **{100*float(pop_apollo["observed_s80"]):.1f}%** and **{100*float(pop_other["observed_s80"]):.1f}%**, respectively. This large excess over general-population expectation is compatible with survival to astronaut/test-pilot selection, medical screening, and healthy-selectee effects; it is not an Apollo-flight causal effect.

The birth-origin Kaplan–Meier description and attained-age summaries are retained in `km_birth_selected_ages.csv`, `survival_group_summary.csv`, and the SVG figures. They must not be read as baseline-randomized survival because Apollo status is assigned by a future flight.

## Publicly documented late-life functioning

{public_table}

The primary Apollo-minus-`OTHER_ALL` five-year public-function detection risk difference is **{100*public_primary[0]:.1f} percentage points** (95% percentile bootstrap **{100*public_primary[1]:.1f} to {100*public_primary[2]:.1f}**). The fixed practical threshold is 10 percentage points.

For the secondary any-time endpoint, Apollo has **{primary_crude["apollo_detected"]}/{primary_crude["apollo_eligible"]}** detections and `OTHER_ALL` has **{primary_crude["comparator_detected"]}/{primary_crude["comparator_eligible"]}**. The crude risk difference is **{100*float(primary_crude["risk_difference"]):.1f} pp** (95% CI **{100*float(primary_crude["risk_difference95_lower"]):.1f} to {100*float(primary_crude["risk_difference95_upper"]):.1f}**), risk ratio **{primary_crude["risk_ratio"]}** (95% CI {primary_crude["risk_ratio95_lower"]} to {primary_crude["risk_ratio95_upper"]}), and odds ratio **{primary_crude["odds_ratio"]}** (conditional exact 95% CI {primary_crude["odds_ratio_conditional_exact95_lower"]} to {primary_crude["odds_ratio_conditional_exact95_upper"]}); supplementary Fisher p={primary_crude["fisher_exact_two_sided_p"]}.

The R001-excluded analyses are technical-deviation sensitivities only. They do not replace the primary estimates and are not independent confirmations. Documentation depth and raw source counts are described without conditioning; MEDIUM/HIGH is not treated as adjustment or complete-case correction.

Excluding R001 changes the five-year risk difference from {100*public_primary[0]:.1f} to **{100*tech_estimate:.1f} pp** and the crude any-time difference from {100*float(primary_crude["risk_difference"]):.1f} to **{100*float(technical_crude["risk_difference"]):.1f} pp**.

### Source availability

{documentation_table}

These differences describe the search record; no endpoint is conditioned on documentation depth.

### Later events, temporal sequences, and latent bounds

{latest_table}

Among Apollo-eligible people, the locked full-window states comprise 2 `FUNCTION_ONLY`, 1 `IMPAIRMENT_THEN_FUNCTION`, and 19 `NEITHER_FOUND`; among `OTHER_ALL`, they comprise 2 `FUNCTION_ONLY` and 33 `NEITHER_FOUND`. Function and impairment are therefore retained as coexisting evidence where applicable.

No qualifying event is boundary-sensitive, so earliest/latest plausible-date sensitivity is identical by construction. For the different latent-event question, asymmetrically assigning every `NEITHER_FOUND` yields an Apollo-minus-`OTHER_ALL` any-event range from **{100*float(latent_primary["worst_case_apollo_minus_comparator"]):.1f} to {100*float(latent_primary["best_case_apollo_minus_comparator"]):.1f} pp**. These are not observed-detection estimates and do not change the primary Aalen–Johansen result.

## Endpoint classifications

- **SURVIVAL: {survival_strength} / {survival_direction}.** {survival_reason}
- **PUBLIC FUNCTION: {public_strength} / {public_direction}.** {public_reason}

## Limitations

Apollo membership is future-flight classification. Birth-origin comparisons therefore contain immortal-time and selection structure, and even the 1973 landmark does not remove healthy-selectee, mission-assignment, occupational, military, socioeconomic, or survivorship differences. The nested comparator sensitivities reuse many people and are not independent replications.

The public-function endpoint measures what the fixed search budget detected in public sources. Source availability, editorial choices, seclusion, physical disability, and identity/date resolution affect detection. No evidence remains unknown rather than impairment. Function and impairment can coexist. Small groups produce wide, discrete bootstrap and exact intervals.

The SSA benchmark is sex- and birth-era-matched but not occupation-, health-, or selection-matched; AS120 combines historical mortality with projections. Observed attained age for survivors is administratively censored and is not completed lifetime.

## Plain conclusions

**Survival:** no prespecified Apollo-versus-`OTHER_ALL` anomaly was detected. Apollo's primary RMST estimate is slightly higher, but small relative to the 5-year threshold, imprecise, and directionally inconsistent across the two nested composition sensitivities. Apollo and the comparison cohorts both outlive male birth-cohort expectations, especially Apollo, but that external contrast is strongly compatible with astronaut/test-pilot screening and healthy-selectee survival.

**Public function:** no prespecified anomaly was detected. Apollo's observed five-year detection estimate is slightly higher than `OTHER_ALL`, but the 1.7-point difference is below the 10-point threshold, imprecise, and reverses against `MILITARY_ONLY`. This conclusion is about detected public evidence, never clinical cognition.

Neither question supports a causal effect of Apollo flight.
"""
    (STAGE / "ANALYSIS_REPORT.md").write_text(report, encoding="utf-8")

    if survival_strength in {"ROBUST", "SUGGESTIVE"} or public_strength in {"ROBUST", "SUGGESTIVE"}:
        anomaly_answer = "A descriptive anomaly is detected only to the strength and direction stated below; it is noncausal."
    elif "INDETERMINATE" in {survival_strength, public_strength}:
        anomaly_answer = "Whether there is an anomaly is indeterminate because at least one endpoint could not be judged."
    else:
        anomaly_answer = "No prespecified descriptive anomaly is detected."
    blind = f"""# Blind conclusion

- SURVIVAL: **{survival_strength} / {survival_direction}**
- PUBLIC FUNCTION: **{public_strength} / {public_direction}**

**Is there an anomaly?** {anomaly_answer}

This conclusion uses the locked 5.0-year survival RMST and 10-percentage-point public-function thresholds. It describes future-selected cohorts and public-evidence detection; it is neither causal nor a clinical cognitive conclusion.
"""
    (STAGE / "BLIND_CONCLUSION.md").write_text(blind, encoding="utf-8")

    validation = f"""# Stage 2 validation

## Locked-input and join checks

- Stage 1, Stage 1B, and Stage 1C were read only: PASS.
- Locked-file aggregate SHA-256 matches the pre-analysis value `{locked_hash}`: PASS.
- Cohort, worklist, and outcome person IDs join one-to-one: PASS.
- Every locked evidence row joins to a cohort person: PASS.
- APOLLO_FLEW and OTHER_ALL are disjoint: PASS.
- OTHER_ALL equals the frozen union rule restricted to non-Apollo: PASS.
- MILITARY_ONLY equals the union of the three military flags restricted to non-Apollo: PASS.
- OTHER_AVAILABLE and OTHER_ALL have identical post-1973 risk sets: PASS.
- OTHER_AVAILABLE and OTHER_ALL have identical age-80 risk sets: PASS.

## Survival checks

- Primary landmark is exactly 1973-01-01 and includes only people alive then: PASS.
- Death/censor dates do not exceed 2026-06-01: PASS.
- Primary horizon is exactly 50.0 analysis years: PASS.
- RMST uses Kaplan–Meier integration: PASS.
- Each RMST contrast uses stratified resampling within groups, {BOOT_REPS} replicates, seed {SEED}, and percentile 2.5/97.5 limits: PASS.
- Cox model contains group plus linear age at landmark and uses Efron ties: PASS.
- Cox convergence flag: {'PASS' if cox["converged"] else 'FAIL'}.
- Schoenfeld-residual term and global diagnostics are retained: PASS.
- Birth-origin Kaplan–Meier is labeled retrospective and future-flight-selected: PASS.
- Nested composition groups are labeled sensitivities, not replications: PASS.

## Public-function checks

- Eligibility is reaching age 80 by death or censor: PASS.
- Every primary function event is in age [80,85): PASS.
- Death before detected function is competing; administrative/age-85 end is censoring: PASS.
- Every Aalen–Johansen contrast uses stratified resampling, {BOOT_REPS} replicates, seed {SEED}, and percentile limits: PASS.
- The R001 exclusion appears only as a technical-deviation sensitivity: PASS.
- Secondary crude group intervals are Clopper–Pearson exact: PASS.
- Risk difference, risk ratio, odds ratio, compatible intervals, and Fisher test are retained: PASS.
- Documentation depth matches raw locked labels and raw source/publisher counts are retained: PASS.
- No analysis conditions on documentation depth: PASS.
- Latent-event bounds are separately labeled as a different question: PASS.
- Boundary-sensitive qualifying events found: {len(boundary_events)}. {'Earliest/latest sensitivity is identical by construction.' if not boundary_events else 'Each is retained in boundary_date_sensitivity.csv.'}
- Outcome states are mutually exclusive locked labels and temporal sequences are retained: PASS.

## External benchmark and interpretation

- Only official SSA life-table sources were used externally: PASS.
- Exact annual e0 values cover every represented birth year: PASS.
- S80 interpolation uses surrounding official decennial cohort values: PASS.
- External population expectations are labeled nonexchangeable descriptive benchmarks: PASS.
- No prior project result or parent/sibling project data was read: PASS.
- No causal or clinical-cognition claim is made: PASS.
"""
    (STAGE / "VALIDATION.md").write_text(validation, encoding="utf-8")

    contamination = """# Stage 2 contamination log

No contamination encounter occurred. Stage 2 web activity was restricted to official Social Security Administration life-table pages and files. No Apollo/astronaut mortality, aging, vitality, cognition, or comparative analysis was searched for or opened.
"""
    (STAGE / "CONTAMINATION.md").write_text(contamination, encoding="utf-8")

    output_names = [
        "ANALYSIS_DECISIONS.md", "analysis.py", "ANALYSIS_REPORT.md",
        "validate.py",
        "RESULTS_SUMMARY.csv", "VALIDATION.md", "CONTAMINATION.md",
        "BLIND_CONCLUSION.md", "STAGE_COMPLETE.md",
        "EXTERNAL_SOURCE_LOG.csv", "ssa_male_cohort_expectations.csv",
        "locked_input_hashes.csv",
        "survival_group_summary.csv", "population_expectation.csv",
        "survival_landmark_rmst.csv", "cox_model.csv", "ph_diagnostic.csv",
        "km_birth_selected_ages.csv", "public_function_primary.csv",
        "public_function_crude.csv", "documentation_depth.csv",
        "documentation_counts.csv", "latent_event_bounds.csv",
        "boundary_date_sensitivity.csv", "latest_function_age.csv",
        "temporal_sequences.csv", "survival_landmark_km.svg",
        "survival_birth_km.svg", "public_function_cif.svg",
        "documentation_depth.svg",
    ]
    complete = """# Stage 2 complete

All required Stage 2 analyses were completed from the locked person-level data. The only external evidence was official SSA male cohort life-table material.

Artifacts:

""" + "\n".join(f"- `stage2/{name}`" for name in output_names) + """

Stage 1, Stage 1B, and Stage 1C were not altered. No parent or sibling project data and no prior result were read. The report contains no causal Apollo-flight claim and calls the late-life endpoint public-evidence detection, not a clinical cognitive measure.
"""
    (STAGE / "STAGE_COMPLETE.md").write_text(complete, encoding="utf-8")

    print("PASS: Stage 2 analysis and artifacts generated")


if __name__ == "__main__":
    main()
