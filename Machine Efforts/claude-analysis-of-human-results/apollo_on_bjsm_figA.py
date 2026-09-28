#!/usr/bin/env python3
"""
Overlay the 29 Apollo astronauts' Kaplan–Meier survival (follow-up from age 30) on panel A of
Figure 2 from Antero et al. 2021 (Br J Sports Med 55:206–212), which shows male/female US Olympians
against their general-population controls by follow-up time since the Games.
[AUTHOR]'s ask, 2026-09-07 20:30 PDT. Attribution is printed on the image. The third-party figure is BMJ's;
the overlay is a study aid for her essay and the caption says exactly what was added.

Calibration (measured from the JPG, not eyeballed): panel A y-ticks at rows 31/108/187/265/342 for 100/75/50/25/0 %;
x-ticks at columns 119/237/355 for 0/20/40 years (5.9 px per year; 80 y at 591).
Apollo KM: events = deaths at (age at death − 30); censored = living at (2026 − birth − 30); ties: events before censoring.
"""
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
HERE = Path(__file__).resolve().parent
SRC = HERE.parent.parent / "Human Efforts" / "Graphs" / "Third Party" / "bjsports-2021-February-55-4-206-F2.large (1).jpg"
DATA = HERE.parent.parent / "Human Efforts" / "scripts" / "Astronaut MC" / "apolloData.h"
X0, PX_PER_YR = 119, (355-119)/40          # x = X0 + t*px
Y0, PX_PER_PCT = 342, (342-31)/100          # y = Y0 - S%*px
ROW = re.compile(r'\{\s*"((?:[^"\\]|\\.)+)"\s*,\s*(\d+)\s*,\s*(\d+)\s*,')
obs = []
for m in ROW.finditer(DATA.read_text()):
    b, d = int(m.group(2)), int(m.group(3))
    obs.append((((d-b) if d else (2026-b)) - 30, 1 if d else 0))
obs.sort(key=lambda x: (x[0], -x[1]))       # events before censoring at tied times
S, at = 1.0, len(obs); steps = [(0.0, 1.0)]
for t, e in obs:
    if e: S *= (1 - 1/at); steps.append((t, S))
    at -= 1
last_censor = max(t for t, e in obs if e == 0)
print("KM steps:", [(t, round(s, 3)) for t, s in steps]); print("last censoring at t =", last_censor)

im = Image.open(SRC).convert("RGB")
panel = im.crop((0, 0, 640, 410))            # panel A incl. its x-axis label; at-risk table excluded
draw = ImageDraw.Draw(panel)
# step curve
pts = []; prev_t, prev_s = 0.0, 1.0
for t, s in steps[1:]:
    pts += [(X0 + prev_t*PX_PER_YR, Y0 - prev_s*100*PX_PER_PCT), (X0 + t*PX_PER_YR, Y0 - prev_s*100*PX_PER_PCT), (X0 + t*PX_PER_YR, Y0 - s*100*PX_PER_PCT)]
    prev_t, prev_s = t, s
col = (214, 69, 0)
draw.line(pts, fill=col, width=3)
# censoring ticks
for t, e in obs:
    if e == 0:
        s_at = next((s for tt, s in reversed(steps) if tt <= t), 1.0)
        x, y = X0 + t*PX_PER_YR, Y0 - s_at*100*PX_PER_PCT
        draw.line([(x, y-5), (x, y+5)], fill=col, width=2)
# legend entry, inside the panel near the existing legend
try: font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 15); small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 12)
except Exception: font = small = ImageFont.load_default()
draw.rectangle([150, 332, 172, 344], fill=col); draw.text((178, 331), "Apollo astronauts (n=29), follow-up from age 30", fill=col, font=font)
# caption strip
cap = Image.new("RGB", (640, 118), "white"); cd = ImageDraw.Draw(cap)
lines = ["Adapted from: Antero J, Tanaka H, De Larochelambert Q, Pouliquen A, Toussaint J-F. Female and male US Olympic",
         "athletes live 5 years longer than their general population controls. Br J Sports Med 2021;55:206-212, Figure 2A.",
         "Original figure (c) BMJ / the authors. Overlay added for [AUTHOR]'s Apollo essay, not part of the original figure.",
         "Apollo: Kaplan-Meier from age 30 (23 deaths; 6 living censored at 61-66 y of follow-up, ticks). The final drop to zero",
         "is the KM convention when the last observation is a death (Lovell, 97). Olympians' follow-up runs from their Games,",
         "so the two x-axes are follow-up time, not age; the curves are not age-aligned. Source data: apolloData.h."]
for i, l in enumerate(lines): cd.text((8, 6 + i*18), l, fill=(60, 60, 60), font=small)
out = Image.new("RGB", (640, 410 + 118), "white"); out.paste(panel, (0, 0)); out.paste(cap, (0, 410))
out = out.resize((1280, 1056), Image.LANCZOS)
out.save(HERE / "apollo_on_bjsm_2021_figA.png"); print("wrote apollo_on_bjsm_2021_figA.png")

# ---- SVG version ([AUTHOR]'s ask, 20:33): the BMJ panel embedded as a raster, the Apollo overlay as editable vectors
import base64, io
buf = io.BytesIO(); im.crop((0, 0, 640, 410)).save(buf, format="JPEG", quality=92)
b64 = base64.b64encode(buf.getvalue()).decode()
def P(t, s): return (X0 + t*PX_PER_YR, Y0 - s*100*PX_PER_PCT)
d = []; prev_t, prev_s = 0.0, 1.0
d.append("M %.1f %.1f" % P(0, 1.0))
for t, s in steps[1:]:
    d.append("H %.1f" % P(t, prev_s)[0]); d.append("V %.1f" % P(t, s)[1]); prev_t, prev_s = t, s
ticks = []
for t, e in obs:
    if e == 0:
        s_at = next((s for tt, s in reversed(steps) if tt <= t), 1.0); x, y = P(t, s_at)
        ticks.append(f'<line x1="{x:.1f}" y1="{y-5:.1f}" x2="{x:.1f}" y2="{y+5:.1f}"/>')
cap_lines = lines
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="640" height="{410+118}" viewBox="0 0 640 {410+118}" font-family="Helvetica, Arial, sans-serif">',
       f'<rect id="bg" width="640" height="{410+118}" fill="#fff"/>',
       f'<g id="bjsm-figure-2A-raster"><image href="data:image/jpeg;base64,{b64}" x="0" y="0" width="640" height="410"/></g>',
       f'<g id="apollo-km" fill="none" stroke="#d64500" stroke-width="3" stroke-linejoin="miter"><path id="apollo-km-path" d="{" ".join(d)}"/></g>',
       f'<g id="apollo-censoring-ticks" stroke="#d64500" stroke-width="2">{"".join(ticks)}</g>',
       '<g id="apollo-legend"><rect x="150" y="332" width="22" height="12" fill="#d64500"/><text x="178" y="343" font-size="15" fill="#d64500">Apollo astronauts (n=29), follow-up from age 30</text></g>',
       '<g id="attribution" font-size="11.5" fill="#3c3c3c">']
for i, l in enumerate(cap_lines): svg.append(f'<text x="8" y="{410+18+i*18}">{l.replace("&","&amp;").replace("<","&lt;")}</text>')
svg.append('</g></svg>')
(HERE / "apollo_on_bjsm_2021_figA.svg").write_text("\n".join(svg)); print("wrote apollo_on_bjsm_2021_figA.svg (raster panel embedded, overlay as vectors)")
