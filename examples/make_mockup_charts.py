"""Mockup charts for the Climate Profile mockup PDF - ILLUSTRATIVE DATA ONLY."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager as fm
import pathlib

for f in pathlib.Path("../fonts").glob("RobotoCondensed-*.ttf"):
    fm.fontManager.addfont(str(f))
plt.rcParams["font.family"] = "Roboto Condensed"

ACCENT = "#3D5A99"
MUTED = "#9A958C"
TEXT = "#20201d"

years = np.arange(1985, 2025)
# Illustrative warming trend with noise
temp = 28.1 + 0.029 * (years - 1985) + np.random.RandomState(7).normal(0, 0.18, len(years))

fig, ax = plt.subplots(figsize=(7.2, 3.0), dpi=150)
ax.plot(years, temp, color=ACCENT, linewidth=1.8)
z = np.polyfit(years, temp, 1)
ax.plot(years, np.polyval(z, years), color=MUTED, linestyle="--", linewidth=1.2)
ax.annotate(f"+{z[0]*10:.1f} C/decade", xy=(2018, np.polyval(z, 2018)),
            xytext=(1996, 28.05), fontsize=9, color=TEXT)
ax.set_title("Mean annual temperature, 1985-2024 (illustrative)", fontsize=10,
             color=TEXT, loc="left", fontweight="bold")
ax.set_ylabel("deg C", fontsize=9, color=MUTED)
ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="y", linestyle="--", linewidth=0.5, alpha=0.25)
ax.tick_params(labelsize=8, colors=MUTED)
fig.tight_layout()
fig.savefig("chart_temperature.png", bbox_inches="tight")
plt.close(fig)

months = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]
baseline = [1, 3, 12, 45, 68, 88, 130, 145, 92, 30, 5, 2]
recent = [0, 2, 8, 38, 60, 80, 112, 132, 85, 24, 4, 1]
x = np.arange(12)

fig, ax = plt.subplots(figsize=(7.2, 3.0), dpi=150)
ax.bar(x - 0.2, baseline, 0.4, label="1985-2005 baseline", color=MUTED, alpha=0.55)
ax.bar(x + 0.2, recent, 0.4, label="2015-2024 average", color=ACCENT)
ax.set_title("Monthly rainfall: recent decade vs historical baseline, mm (illustrative)",
             fontsize=10, color=TEXT, loc="left", fontweight="bold")
ax.set_xticks(x, months, fontsize=8)
ax.set_ylabel("mm/month", fontsize=9, color=MUTED)
ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="y", linestyle="--", linewidth=0.5, alpha=0.25)
ax.legend(frameon=False, fontsize=8, loc="upper left")
ax.tick_params(labelsize=8, colors=MUTED)
fig.tight_layout()
fig.savefig("chart_rainfall.png", bbox_inches="tight")
plt.close(fig)
print("charts done")
