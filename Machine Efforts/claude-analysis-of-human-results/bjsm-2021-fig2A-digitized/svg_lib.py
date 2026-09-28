#!/usr/bin/env python3
"""A very small hand-rolled SVG chart writer: named <g> layers, no raster, white ground."""
from __future__ import annotations

import numpy as np

W, H = 1020, 800
L, R, T, B = 92, 986, 46, 470          # plot rectangle
CAP_TOP = 552
CAP_CHARS = 142        # caption wrap width, tuned to the 12.5 px face and plot width


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


class Chart:
    def __init__(self, xlim, ylim, xlabel, ylabel, title, xticks, yticks,
                 ytickfmt=lambda v: f"{v:g} %"):
        self.x0, self.x1 = xlim
        self.y0, self.y1 = ylim
        self.parts = []
        self.layers = {}
        self.legend = []
        self.title = title
        self.xlabel, self.ylabel = xlabel, ylabel
        self.xticks, self.yticks, self.ytickfmt = xticks, yticks, ytickfmt

    # ---- coordinate transforms
    def px(self, x):
        return L + (np.asarray(x, float) - self.x0) / (self.x1 - self.x0) * (R - L)

    def py(self, y):
        return B - (np.asarray(y, float) - self.y0) / (self.y1 - self.y0) * (B - T)

    # ---- layers
    def layer(self, name, content):
        self.layers.setdefault(name, []).append(content)

    def path(self, layer, xs, ys, stroke, width=2.0, dash=None, opacity=1.0, step=False):
        xs, ys = np.asarray(xs, float), np.asarray(ys, float)
        m = ~(np.isnan(xs) | np.isnan(ys))
        xs, ys = xs[m], ys[m]
        if len(xs) < 2:
            return
        X, Y = self.px(xs), self.py(ys)
        if step:
            d = [f"M {X[0]:.2f} {Y[0]:.2f}"]
            for i in range(1, len(X)):
                d.append(f"H {X[i]:.2f}")
                d.append(f"V {Y[i]:.2f}")
        else:
            d = [f"M {X[0]:.2f} {Y[0]:.2f}"] + [f"L {x:.2f} {y:.2f}" for x, y in zip(X[1:], Y[1:])]
        da = f' stroke-dasharray="{dash}"' if dash else ""
        op = f' stroke-opacity="{opacity}"' if opacity != 1.0 else ""
        self.layer(layer, f'<path fill="none" stroke="{stroke}" stroke-width="{width}"'
                          f' stroke-linejoin="round" stroke-linecap="round"{da}{op}'
                          f' d="{" ".join(d)}"/>')

    def ticks_marks(self, layer, xs, ys, stroke, half=5, width=1.6):
        out = []
        for x, y in zip(np.asarray(xs, float), np.asarray(ys, float)):
            X, Y = float(self.px(x)), float(self.py(y))
            out.append(f'<line x1="{X:.2f}" y1="{Y-half:.2f}" x2="{X:.2f}" y2="{Y+half:.2f}"/>')
        self.layer(layer, f'<g stroke="{stroke}" stroke-width="{width}">{"".join(out)}</g>')

    def add_legend(self, label, stroke, dash=None, width=2.4):
        self.legend.append((label, stroke, dash, width))

    # ---- output
    def render(self, caption_lines, legend_x=None, legend_y=None):
        s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
             f'viewBox="0 0 {W} {H}" font-family="Helvetica Neue, Helvetica, Arial, sans-serif">',
             f'<g id="background"><rect width="{W}" height="{H}" fill="#ffffff"/></g>']

        grid = []
        for v in self.yticks:
            y = float(self.py(v))
            grid.append(f'<line x1="{L}" y1="{y:.2f}" x2="{R}" y2="{y:.2f}"/>')
        for v in self.xticks:
            x = float(self.px(v))
            grid.append(f'<line x1="{x:.2f}" y1="{T}" x2="{x:.2f}" y2="{B}"/>')
        s.append('<g id="grid" stroke="#e6e6e6" stroke-width="1">' + "".join(grid) + "</g>")

        s.append(f'<g id="axes" stroke="#333" stroke-width="1.4" fill="none">'
                 f'<line x1="{L}" y1="{T}" x2="{L}" y2="{B}"/>'
                 f'<line x1="{L}" y1="{B}" x2="{R}" y2="{B}"/></g>')

        lab = []
        for v in self.xticks:
            x = float(self.px(v))
            lab.append(f'<line x1="{x:.2f}" y1="{B}" x2="{x:.2f}" y2="{B+6}" stroke="#333"/>')
            lab.append(f'<text x="{x:.2f}" y="{B+22}" font-size="13" fill="#333" '
                       f'text-anchor="middle">{v:g}</text>')
        for v in self.yticks:
            y = float(self.py(v))
            lab.append(f'<line x1="{L-6}" y1="{y:.2f}" x2="{L}" y2="{y:.2f}" stroke="#333"/>')
            lab.append(f'<text x="{L-11}" y="{y+4.5:.2f}" font-size="13" fill="#333" '
                       f'text-anchor="end">{esc(self.ytickfmt(v))}</text>')
        lab.append(f'<text x="{(L+R)/2:.0f}" y="{B+50}" font-size="14.5" fill="#222" '
                   f'text-anchor="middle">{esc(self.xlabel)}</text>')
        lab.append(f'<text transform="translate(26,{(T+B)/2:.0f}) rotate(-90)" font-size="14.5" '
                   f'fill="#222" text-anchor="middle">{esc(self.ylabel)}</text>')
        lab.append(f'<text x="{L}" y="{T-16}" font-size="17" font-weight="600" fill="#111">'
                   f'{esc(self.title)}</text>')
        s.append('<g id="axis-labels">' + "".join(lab) + "</g>")

        for name, items in self.layers.items():
            s.append(f'<g id="{name}">' + "".join(items) + "</g>")

        if self.legend:
            lx = legend_x if legend_x is not None else L + 22
            ly = legend_y if legend_y is not None else T + 24
            wpx = 52 + int(6.6 * max(len(l[0]) for l in self.legend))
            rows = [f'<rect x="{lx-14}" y="{ly-19}" width="{wpx}" '
                    f'height="{22*len(self.legend)+12}" rx="5" fill="#ffffff" '
                    f'fill-opacity="0.94" stroke="#dcdcdc"/>']
            for i, (label, stroke, dash, wdt) in enumerate(self.legend):
                y = ly + i * 22
                da = f' stroke-dasharray="{dash}"' if dash else ""
                rows.append(f'<line x1="{lx}" y1="{y}" x2="{lx+30}" y2="{y}" stroke="{stroke}" '
                            f'stroke-width="{wdt}"{da} stroke-linecap="round"/>')
                rows.append(f'<text x="{lx+40}" y="{y+4.5}" font-size="13" fill="#222">'
                            f'{esc(label)}</text>')
            s.append('<g id="legend">' + "".join(rows) + "</g>")

        wrapped = []
        for line in caption_lines:
            bold = line.startswith("**")
            body = line[2:] if bold else line
            cur = ""
            for word in body.split(" "):
                if cur and len(cur) + 1 + len(word) > CAP_CHARS:
                    wrapped.append(("**" if bold else "") + cur)
                    cur = word
                else:
                    cur = f"{cur} {word}".strip()
            wrapped.append(("**" if bold else "") + cur)
        caption_lines = wrapped

        cap = []
        for i, line in enumerate(caption_lines):
            weight = ' font-weight="600"' if line.startswith("**") else ""
            txt = line[2:] if line.startswith("**") else line
            cap.append(f'<text x="{L}" y="{CAP_TOP + i*19}" font-size="12.5" fill="#444"'
                       f'{weight}>{esc(txt)}</text>')
        s.append('<g id="attribution">' + "".join(cap) + "</g>")
        s.append("</svg>")
        return "\n".join(s)
