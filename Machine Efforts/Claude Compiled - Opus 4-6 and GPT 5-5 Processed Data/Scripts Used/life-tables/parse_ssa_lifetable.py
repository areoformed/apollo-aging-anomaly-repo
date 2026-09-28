#!/usr/bin/env python3
"""Parse SSA 1930 male cohort life table from saved HTML.
Extracts q(x) values and outputs a C header file."""

from html.parser import HTMLParser
import sys

class SSAParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_td = False
        self.current_text = ""
        self.cells = []

    def handle_starttag(self, tag, attrs):
        if tag == 'td':
            self.in_td = True
            self.current_text = ""

    def handle_endtag(self, tag):
        if tag == 'td' and self.in_td:
            self.cells.append(self.current_text.strip())
            self.in_td = False

    def handle_data(self, data):
        if self.in_td:
            self.current_text += data

HTML_PATH = "../Final - Analysis - Enriched Datasets/../../../Human Efforts/Manually Compiled Data/Life Tables for the USSSA - Year of birth 1930.html"

if len(sys.argv) > 1:
    HTML_PATH = sys.argv[1]

with open(HTML_PATH) as f:
    html = f.read()

parser = SSAParser()
parser.feed(html)
cells = [c.replace(',', '').replace('\xa0', '').strip() for c in parser.cells]

# Table has 14 columns per row: 7 male + 7 female
# Male columns: age, q(x), l(x), d(x), L(x), T(x), e(x)
male_qx = {}
i = 0
while i < len(cells) - 13:
    age_str = cells[i]
    qx_str = cells[i + 1]
    try:
        age = int(age_str)
        qx = float(qx_str)
        male_qx[age] = qx
        i += 14
    except (ValueError, IndexError):
        i += 1

max_age = max(male_qx.keys())

print(f"/* SSA 1930 male cohort life table — q(x) values")
print(f"   Source: SSA Actuarial Study No. 120, Table 7, Year of Birth 1930")
print(f"   q(x) = probability of dying at age x, given survival to age x */")
print()
print(f"#define QX_MAX_AGE {max_age}")
print()
print("static const double ssa1930_male_qx[] = {")

for age in range(max_age + 1):
    qx = male_qx.get(age, 1.0)
    comma = "," if age < max_age else ""
    print(f"    {qx:.6f}{comma}  /* age {age} */")

print("};")

# Verification
surv_to_80 = 1.0
for age in range(0, 80):
    surv_to_80 *= (1.0 - male_qx.get(age, 0))

surv_to_80_from_30 = 1.0
for age in range(30, 80):
    surv_to_80_from_30 *= (1.0 - male_qx.get(age, 0))

print(f"\n/* Verification:")
print(f"   Survival to 80 (from birth): {surv_to_80 * 100:.1f}%")
print(f"   Survival to 80 (given alive at 30): {surv_to_80_from_30 * 100:.1f}% */")
