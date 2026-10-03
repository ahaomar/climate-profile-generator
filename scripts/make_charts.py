#!/usr/bin/env python3
"""climate-profile-generator / Phase 2: chart engine.

Renders the standard charts from a Phase 1 data JSON
(scripts/fetch_climate.py output).

Usage:
    python3 scripts/make_charts.py output/BFA_data.json [-o output/charts]
                                                 [--force-svg]

Charts (layout locked to the approved mockup):
  1. chart_temperature  - annual temperature 1985-2024 + linear trend
  2. chart_rainfall     - monthly climatology, recent decade vs baseline

Rules (docs/TECHNICAL_SPEC.md): Roboto Condensed from ../fonts, navy
palette family, no top/right spines, dashed 25%-alpha grid, label only
trend annotations. matplotlib when available; otherwise a dependency-free
SVG fallback (same palette, same chart types) so charts never disappear.
"""
import argparse
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = ROOT / "fonts"

NAVY = "#3D5A99"
NAVY_DARK = "#1F3A7A"
WARM_GREY = "#9A958C"
TEXT = "#20201d"
MUTED = "#8b8982"

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def monthly_two_periods(npd, recent_n=10):
    """(baseline_mm_day, recent_mm_day, baseline_label, recent_label).

    Baseline = all complete years BEFORE the recent decade; recent = the
    latest `recent_n` complete years. Computed from the per-year monthly
    matrix so the comparison is honest (baseline excludes recent years).
    """
    by_year = npd.get("monthly_precip_by_year") or {}
    years = sorted(int(y) for y in by_year)
    cutoff = years[-1] - recent_n + 1
    base_rows = [by_year[str(y)] for y in years if y < cutoff]
    rec_rows = [by_year[str(y)] for y in years if y >= cutoff]
    n_m = len(base_rows)
    baseline = [statistics.mean(row[m] for row in base_rows
                                if row[m] != -999) for m in range(12)]
    recent = [statistics.mean(row[m] for row in rec_rows
                              if row[m] != -999) for m in range(12)]
    return (baseline, recent,
            "%d-%d baseline" % (years[0], cutoff - 1),
            "%d-%d average" % (cutoff, years[-1]))


def recent_mask_years(years, n=10):
    cutoff = years[-1] - n + 1
    return [y >= cutoff for y in years]


# ---------------------------------------------------------------- matplotlib
def matplotlib_available():
    try:
        import matplotlib  # noqa: F401
        return True
    except ImportError:
        return False


def setup_matplotlib():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager as fm
    for f in FONT_DIR.glob("RobotoCondensed-*.ttf"):
        try:
            fm.fontManager.addfont(str(f))
        except Exception:
            pass  # falls back to default font; chart still renders
    plt.rcParams["font.family"] = "Roboto Condensed"
    plt.rcParams["axes.unicode_minus"] = False
    return plt


def style_axes(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", linestyle="--", linewidth=0.5, alpha=0.25)
    ax.tick_params(labelsize=8, colors=MUTED)


def chart_temperature_mpl(plt, data, out_path):
    ann = data["datasets"]["nasa_power"]["annual"]
    years, temps = ann["years"], ann["temp_c"]
    fig, ax = plt.subplots(figsize=(7.2, 3.0), dpi=150)
    ax.plot(years, temps, color=NAVY, linewidth=1.8)
    if len(years) >= 10:
        z = statistics.linear_regression(years, temps)
        trend = [z.slope * y + z.intercept for y in years]
        ax.plot(years, trend, color=WARM_GREY, linestyle="--", linewidth=1.2)
        per_decade = z.slope * 10
        x_lab = years[0] + (years[-1] - years[0]) * 0.3
        y_lab = min(temps) + (max(temps) - min(temps)) * 0.12
        ax.annotate("%+.2f C/decade" % per_decade, xy=(years[-1], trend[-1]),
                    xytext=(x_lab, y_lab), fontsize=9, color=TEXT)
    ax.set_title("Mean annual temperature, %d-%d" % (years[0], years[-1]),
                 fontsize=10, color=TEXT, loc="left", fontweight="bold")
    ax.set_ylabel("deg C", fontsize=9, color=MUTED)
    style_axes(ax)
    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)


def chart_rainfall_mpl(plt, data, out_path, recent_n=10):
    npd = data["datasets"]["nasa_power"]
    ann = npd["annual"]
    years = ann["years"]
    # reconstruct monthly climatology per group from the annual monthly arrays
    # Phase 1 stores one blended climatology; recompute from raw requires the
    # monthly series, so approximate: recent decade = baseline scaled by the
    # ratio of recent-decade annual mean to full-period annual mean.
    baseline, recent, leg1, leg2 = monthly_two_periods(npd, recent_n)
    x = range(12)
    fig, ax = plt.subplots(figsize=(7.2, 3.0), dpi=150)
    ax.bar([i - 0.2 for i in x], baseline, 0.4, label=leg1,
           color=WARM_GREY, alpha=0.55)
    ax.bar([i + 0.2 for i in x], recent, 0.4, label=leg2, color=NAVY)
    ax.set_title("Monthly rainfall: recent decade vs historical baseline, mm",
                 fontsize=10, color=TEXT, loc="left", fontweight="bold")
    ax.set_xticks(list(x), MONTHS, fontsize=8)
    ax.set_ylabel("mm/month", fontsize=9, color=MUTED)
    style_axes(ax)
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)


# --------------------------------------------------------------- SVG fallback
def _svg_header(w, h):
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
            'viewBox="0 0 %d %d" font-family="Roboto Condensed, Arial, sans-serif">'
            % (w, h, w, h))


def _svg_line_chart(years, temps, out_path, title):
    W, H = 1080, 450
    ml, mr, mt, mb = 70, 20, 55, 45
    pw, ph = W - ml - mr, H - mt - mb
    ymin, ymax = min(temps), max(temps)
    pad = (ymax - ymin) * 0.15 or 1
    ymin, ymax = ymin - pad, ymax + pad

    def X(i):
        return ml + pw * i / max(len(years) - 1, 1)

    def Y(v):
        return mt + ph * (1 - (v - ymin) / (ymax - ymin))

    parts = [_svg_header(W, H)]
    parts.append('<text x="%d" y="30" font-size="19" font-weight="bold" '
                 'fill="%s">%s</text>' % (ml, TEXT, title))
    # gridlines + y labels (5 ticks)
    for k in range(5):
        v = ymin + (ymax - ymin) * k / 4
        y = Y(v)
        parts.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="%s" '
                     'stroke-width="0.8" stroke-dasharray="4 4" opacity="0.25"/>'
                     % (ml, y, W - mr, y, MUTED))
        parts.append('<text x="%d" y="%.1f" font-size="13" fill="%s" '
                     'text-anchor="end">%.1f</text>' % (ml - 8, y + 4, MUTED, v))
    # trend line
    n = len(years)
    mx, my = statistics.mean(years), statistics.mean(temps)
    slope = sum((x - mx) * (y - my) for x, y in zip(years, temps)) / \
        sum((x - mx) ** 2 for x in years)
    inter = my - slope * mx
    parts.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="%s" '
                 'stroke-width="2" stroke-dasharray="7 5"/>'
                 % (X(0), Y(inter + slope * years[0]), X(n - 1),
                    Y(inter + slope * years[-1]), WARM_GREY))
    parts.append('<text x="%d" y="%.1f" font-size="15" fill="%s">%+.1f C/decade</text>'
                 % (X(int(n * 0.3)), Y(min(temps) + (ymax - ymin) * 0.18), TEXT,
                    slope * 10))
    # data line
    pts = " ".join("%.1f,%.1f" % (X(i), Y(t)) for i, t in enumerate(temps))
    parts.append('<polyline points="%s" fill="none" stroke="%s" '
                 'stroke-width="2.5"/>' % (pts, NAVY))
    # x labels: every 5th year
    for i in range(0, n, 5):
        parts.append('<text x="%d" y="%d" font-size="13" fill="%s" '
                     'text-anchor="middle">%d</text>'
                     % (X(i), H - 18, MUTED, years[i]))
    parts.append('<text x="%d" y="%d" font-size="13" fill="%s" '
                 'text-anchor="middle">%d</text>'
                 % (X(n - 1), H - 18, MUTED, years[-1]))
    parts.append('</svg>')
    out_path.write_text("\n".join(parts), encoding="utf-8")


def _svg_bar_chart(baseline, recent, labels, out_path, title, leg1, leg2):
    W, H = 1080, 450
    ml, mr, mt, mb = 70, 20, 55, 45
    pw, ph = W - ml - mr, H - mt - mb
    ymax = max(max(baseline), max(recent)) * 1.1 or 1
    group_w = pw / 12
    parts = [_svg_header(W, H)]
    parts.append('<text x="%d" y="30" font-size="19" font-weight="bold" '
                 'fill="%s">%s</text>' % (ml, TEXT, title))
    for k in range(5):
        v = ymax * k / 4
        y = mt + ph * (1 - k / 4)
        parts.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="%s" '
                     'stroke-width="0.8" stroke-dasharray="4 4" opacity="0.25"/>'
                     % (ml, y, W - mr, y, MUTED))
        parts.append('<text x="%d" y="%.1f" font-size="13" fill="%s" '
                     'text-anchor="end">%.0f</text>' % (ml - 8, y + 4, MUTED, v))
    for i in range(12):
        cx = ml + group_w * i + group_w / 2
        h1 = ph * baseline[i] / ymax
        h2 = ph * recent[i] / ymax
        parts.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
                     'fill="%s" opacity="0.55"/>'
                     % (cx - group_w * 0.32, mt + ph - h1,
                        group_w * 0.28, h1, WARM_GREY))
        parts.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
                     'fill="%s"/>'
                     % (cx + group_w * 0.04, mt + ph - h2,
                        group_w * 0.28, h2, NAVY))
        parts.append('<text x="%.1f" y="%d" font-size="13" fill="%s" '
                     'text-anchor="middle">%s</text>'
                     % (cx, H - 18, MUTED, labels[i][:3]))
    # legend (top-left, no box)
    lx, ly = ml + 10, mt + 8
    parts.append('<rect x="%d" y="%d" width="14" height="14" fill="%s" '
                 'opacity="0.55"/>' % (lx, ly, WARM_GREY))
    parts.append('<text x="%d" y="%d" font-size="14" fill="%s">%s</text>'
                 % (lx + 20, ly + 12, TEXT, leg1))
    parts.append('<rect x="%d" y="%d" width="14" height="14" fill="%s"/>'
                 % (lx + 180, ly, NAVY))
    parts.append('<text x="%d" y="%d" font-size="14" fill="%s">%s</text>'
                 % (lx + 200, ly + 12, TEXT, leg2))
    parts.append('</svg>')
    out_path.write_text("\n".join(parts), encoding="utf-8")


# ---------------------------------------------------------------------- main
def render(data, out_dir, force_svg=False):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    engine = "svg" if force_svg or not matplotlib_available() else "matplotlib"
    npd = data["datasets"]["nasa_power"]
    years = npd["annual"]["years"]
    recent_n = 10
    y0, y1 = years[-1] - recent_n, years[-1]

    if engine == "matplotlib":
        plt = setup_matplotlib()
        t = out_dir / "chart_temperature.png"
        chart_temperature_mpl(plt, data, t)
        r = out_dir / "chart_rainfall.png"
        chart_rainfall_mpl(plt, data, r, recent_n)
    else:
        t = out_dir / "chart_temperature.svg"
        _svg_line_chart(years, npd["annual"]["temp_c"], t,
                        "Mean annual temperature, %d-%d" % (years[0], years[-1]))
        baseline, recent, leg1, leg2 = monthly_two_periods(npd, recent_n)
        r = out_dir / "chart_rainfall.svg"
        _svg_bar_chart(baseline, recent, MONTHS, r,
                       "Monthly rainfall: recent decade vs historical baseline, mm",
                       leg1, leg2)
    return engine, [str(t), str(r)]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("data_json", help="Phase 1 output JSON")
    ap.add_argument("-o", "--out", default=None, help="output directory")
    ap.add_argument("--force-svg", action="store_true",
                    help="use the dependency-free SVG fallback")
    args = ap.parse_args()
    data = load(args.data_json)
    out_dir = args.out or (Path(args.data_json).parent / "charts")
    engine, files = render(data, out_dir, force_svg=args.force_svg)
    print("engine: %s" % engine)
    for f in files:
        print("wrote %s" % f)


if __name__ == "__main__":
    main()
