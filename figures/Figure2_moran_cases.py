#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render paratyphoid Figure 2 BLACK/GREY FINAL (minimal, PNG only).

Annotation-free black/grey journal version. No red/brown/salmon/pink anywhere.
Structure, data, marker/p-value coding, and the 2010/2011 boundary are unchanged;
all in-figure explanatory text is handled in the caption.

Single Arial family; bold only on panel letters. PNG only.
Source files read-only; output goes to figures/.
"""

from __future__ import annotations

import hashlib
import os
import tempfile
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "paratyphoid_mpl"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D


DPI = 600
FIG_W = 6.8
FIG_H = 4.4

# Typography
FS_PANEL = 10.0     # A / B, bold
FS_AXIS = 9.5       # axis labels, regular
FS_TICK = 8.0       # tick labels
FS_LEGEND = 8.0     # legend labels

# Black / grey palette (no red/brown/salmon/pink)
LINE = "#333333"          # Moran's I line + significant markers + open outline
BAR = "#C7CBD0"           # general reported-cases bars (light neutral grey)
BAR_EDGE = "#b3b7bc"
BAR_2002 = "#8F969C"      # 2002 bar, medium grey (greyscale emphasis)
BAR_2002_EDGE = "#7e858b"
DIVIDER = "#D0D0D0"       # very light grey vertical boundary (must not stand out)
LEG_BORDER = "#E0E0E0"    # near-invisible legend box border
TEXT = "#1a1a1a"

plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
        "axes.edgecolor": "#444444",
        "axes.linewidth": 0.6,
        "xtick.color": "#444444",
        "ytick.color": "#444444",
    }
)

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    morans_path = REPO_ROOT / "results" / "moran_annual.csv"
    morans = pd.read_csv(morans_path, encoding="utf-8-sig")
    df = morans.rename(columns={"total_cases": "reported_cases"}).sort_values("year")

    expected_years = list(range(2001, 2025))
    if len(df) != len(expected_years) or df["year"].tolist() != expected_years:
        raise RuntimeError("Figure 2 annual data do not cover 2001-2024 exactly.")
    if int(df.loc[df["year"] == 2002, "reported_cases"].iloc[0]) != 401:
        raise RuntimeError("2002 reported cases are not 401 in the locked 223-district panel.")
    if int(df["districts"].iloc[0]) != 223:
        raise RuntimeError("Annual Moran data are not based on the locked 223-district analysis set.")

    years = df["year"].to_numpy()
    moran_i = df["moran_i"].to_numpy()
    significant = df["significant_p05"].astype(bool).to_numpy()
    reported_cases = df["reported_cases"].to_numpy()

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(FIG_W, FIG_H), sharex=True,
        gridspec_kw={"height_ratios": [3.0, 2.0], "hspace": 0.12},
    )

    # ---- Panel A: Global Moran's I -------------------------------------
    # Horizontal zero reference line removed (avoids the cross-hair look).
    ax1.axvline(2010.5, color=DIVIDER, lw=0.6, ls=(0, (3, 2)), alpha=0.9, zorder=1)
    ax1.plot(years, moran_i, color=LINE, lw=1.1, zorder=2)
    ax1.scatter(years[significant], moran_i[significant],
                s=14, color=LINE, edgecolor=LINE, linewidth=0.5, zorder=3)
    ax1.scatter(years[~significant], moran_i[~significant],
                s=14, facecolor="white", edgecolor=LINE, linewidth=0.95, zorder=3)
    ax1.set_ylabel("Global Moran's I", fontsize=FS_AXIS)
    ax1.set_ylim(-0.10, 0.27)
    ax1.set_yticks([0.0, 0.1, 0.2])
    ax1.text(0.010, 0.965, "A", transform=ax1.transAxes, fontsize=FS_PANEL, fontweight="bold", color=TEXT, va="top")

    # Vertical legend box, inside the top panel top-right, over empty space.
    legend_handles = [
        Line2D([0], [0], color=LINE, lw=1.0, marker="o", markersize=3.6,
               markerfacecolor=LINE, markeredgecolor=LINE, label="p < 0.05"),
        Line2D([0], [0], color=LINE, lw=1.0, marker="o", markersize=3.6,
               markerfacecolor="white", markeredgecolor=LINE, label="p ≥ 0.05"),
    ]
    leg = ax1.legend(handles=legend_handles, loc="upper right", bbox_to_anchor=(0.995, 0.97),
                     frameon=True, fontsize=FS_LEGEND, handlelength=1.3, handletextpad=0.4,
                     borderpad=0.5, labelspacing=0.5, ncol=1)
    leg.get_frame().set_edgecolor(LEG_BORDER)
    leg.get_frame().set_linewidth(0.3)
    leg.get_frame().set_facecolor("white")
    leg.get_frame().set_alpha(0.95)

    # ---- Panel B: reported cases ---------------------------------------
    ax2.axvline(2010.5, color=DIVIDER, lw=0.6, ls=(0, (3, 2)), alpha=0.9, zorder=1)
    bar_colors = [BAR_2002 if y == 2002 else BAR for y in years]
    bar_edges = [BAR_2002_EDGE if y == 2002 else BAR_EDGE for y in years]
    ax2.bar(years, reported_cases, width=0.66, color=bar_colors, edgecolor=bar_edges, lw=0.2, zorder=2)
    ax2.set_ylabel("Reported cases", fontsize=FS_AXIS)
    ax2.set_xlabel("Year", fontsize=FS_AXIS)
    ax2.set_ylim(0, 440)
    ax2.set_yticks([0, 100, 200, 300, 400])
    ax2.set_xlim(2000.25, 2024.75)
    ax2.set_xticks(np.arange(2001, 2025, 2))
    ax2.text(0.010, 0.965, "B", transform=ax2.transAxes, fontsize=FS_PANEL, fontweight="bold", color=TEXT, va="top")

    for ax in (ax1, ax2):
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(labelsize=FS_TICK, width=0.6, length=2.8)

    fig.subplots_adjust(left=0.093, right=0.985, top=0.985, bottom=0.110)

    out_png = OUT_DIR / "Figure2_moran_cases.png"
    fig.savefig(out_png, dpi=DPI, facecolor="white")   # PNG only
    fig_w_px, fig_h_px = int(round(FIG_W * DPI)), int(round(FIG_H * DPI))
    plt.close(fig)

    caption = (
        "Fig. 2. Annual global Moran's I and annual reported cases of paratyphoid "
        "fever, South Korea, 2001-2024 (223 connected districts). Points show "
        "annual global Moran's I of crude incidence; filled points indicate p<0.05 "
        "by permutation testing and open points indicate non-significance. Bars "
        "show annual reported cases. The vertical dashed line marks the 2010/2011 "
        "period boundary. The 2002 peak corresponds to the documented Busan "
        "Geumjeong-gu outbreak. The significant 2010 signal was attributable to "
        "low-count grouping in Gangwon east-coast districts rather than residual "
        "Busan clustering."
    )
    (OUT_DIR / "Figure2_caption.txt").write_text(caption + "\n", encoding="utf-8")

    validation = pd.DataFrame(
        {
            "check": [
                "output_format", "annual_years", "district_set", "cases_2002",
                "significant_point_rule", "vertical_dashed", "text_annotations",
                "palette", "line_color", "bar_2002_color", "font_family", "dpi",
            ],
            "value": [
                "PNG only", f"{df['year'].min()}-{df['year'].max()}", int(df["districts"].iloc[0]),
                int(df.loc[df["year"] == 2002, "reported_cases"].iloc[0]),
                "filled=p<0.05; open=p>=0.05", "2010.5 medium-light grey", "none",
                "black/grey (no red)", LINE, BAR_2002, "Arial", DPI,
            ],
            "expected": [
                "PNG only", "2001-2024", "223", "401", "filled=p<0.05; open=p>=0.05",
                "2010.5 medium-light grey", "none", "black/grey (no red)", "#333333", "#8F969C",
                "Arial", "600",
            ],
        }
    )
    validation["status"] = np.where(validation["value"].astype(str) == validation["expected"].astype(str), "PASS", "CHECK")
    validation.to_csv(OUT_DIR / "Figure2_moran_cases_validation.csv", index=False, encoding="utf-8-sig")

    hashes = pd.DataFrame(
        [
            {"source_file": str(morans_path.relative_to(REPO_ROOT)), "sha256": sha256(morans_path), "access": "READ_ONLY"},
        ]
    )
    hashes.to_csv(OUT_DIR / "Figure2_moran_cases_source_hashes.csv", index=False, encoding="utf-8-sig")

    w_cm, h_cm = FIG_W * 2.54, FIG_H * 2.54
    print("=== Figure 2 BLACK/GREY FINAL v3 (PNG only) ===")
    print(f"Saved PNG: {out_png.relative_to(REPO_ROOT)}")
    print(f"Dimensions: {FIG_W} x {FIG_H} in  =  {w_cm:.2f} x {h_cm:.2f} cm  ({fig_w_px} x {fig_h_px} px @ {DPI} dpi)")
    print(f"line/sig-marker: {LINE} | open outline: {LINE} | general bar: {BAR} | 2002 bar: {BAR_2002}")
    print(f"zero line: REMOVED | vertical dashed: {DIVIDER} (0.6pt) | legend box border: {LEG_BORDER}")
    print(f"Font: Arial | panel {FS_PANEL} bold / axis {FS_AXIS} / tick {FS_TICK} / legend {FS_LEGEND} pt")
    print("Moran line 1.1pt | filled marker s=14 | open outline 0.95pt | legend: vertical box, no title")


if __name__ == "__main__":
    main()
