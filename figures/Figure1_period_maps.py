#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render paratyphoid Figure 1 (choropleth-only + Busan inset).

Journal-minimal redesign:
  * choropleth-only two-panel map (no proportional circles, no callouts)
  * national maps carry NO Geumjeong outline (it reads as a dot at this scale)
  * Panel A gets a small unobtrusive Busan inset that zooms the metro and marks
    Geumjeong-gu with a thin black outline (tiny label, thin grey inset border)
  * fonts ~15-20% smaller than the previous final; bold only on panel letters
  * 600-dpi PNG and LZW-compressed TIFF

Administrative boundary files are not redistributed. Place final.shp, final.shx,
and final.dbf under data/raw/ to regenerate the map.
"""

from __future__ import annotations

import hashlib
import os
import tempfile
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "paratyphoid_mpl"))

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image
from matplotlib.patches import Patch


DPI = 600
FIG_W = 4488 / DPI
FIG_H = 4.4 * (FIG_W / 5.6)

# --- typography (~17% smaller than previous final) ---
FS_PANEL_LETTER = 10.0
FS_PANEL_PERIOD = 10.0
FS_LEGEND_TITLE = 8.7
FS_LEGEND_LABEL = 5.7   # ~12% smaller than v2 (6.5)
FS_SCALE = 6.0
FS_INSET = 5.0

EDGE = "#b7b7b7"
EDGE_LW = 0.22
PROVINCE_EDGE = "#7d7d7d"
PROVINCE_LW = 0.38
ZERO_COLOR = "#d6d6d6"
EXCLUDED_COLOR = "#f2f2f2"
GEUMJEONG_EDGE = "#000000"
GEUMJEONG_LW_INSET = 0.7
INSET_BORDER = "#d8d8d8"
TEXT = "#1a1a1a"
SUBTEXT = "#4d4d4d"

PERIODS = [("A", "2001–2010"), ("B", "2011–2024")]
BREAK_LABELS = ["0", ">0-0.05", "0.05-0.10", "0.10-0.25", "0.25-0.75", ">0.75"]
BREAK_COLORS = {
    "0": ZERO_COLOR,
    ">0-0.05": "#fdece1",
    "0.05-0.10": "#f7c3a2",
    "0.10-0.25": "#ee8f66",
    "0.25-0.75": "#cf5238",
    ">0.75": "#8a1c1a",
}
REMOVED_ISLANDS_EXPECTED = {
    "경상남도거제시", "경상남도남해군", "경상북도울릉군",
    "인천시옹진군", "전라남도완도군", "전라남도진도군",
}

plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
        "axes.edgecolor": "#444444",
        "axes.linewidth": 0.6,
    }
)

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "figures"
SOURCE_DIR = REPO_ROOT / "data" / "raw"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def save_lzw_tiff(fig, path: Path) -> None:
    fig.savefig(
        path,
        dpi=DPI,
        format="tiff",
        facecolor="white",
        pil_kwargs={"compression": "tiff_lzw"},
    )
    with Image.open(path) as im:
        if im.mode != "RGB":
            im = im.convert("RGB")
            im.save(path, compression="tiff_lzw", dpi=(DPI, DPI))


def clean_region(value: object) -> str:
    text = str(value).replace(" ", "").replace("\t", "")
    if text == "인천시미추홀구":
        return "인천시남구"
    return text


def load_shapes() -> gpd.GeoDataFrame:
    required = [SOURCE_DIR / f"final.{ext}" for ext in ("shp", "shx", "dbf")]
    missing = [path.name for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "Administrative boundary files are not redistributed. "
            "Place final.shp, final.shx, and final.dbf under data/raw/. "
            f"Missing: {', '.join(missing)}"
        )
    shape = gpd.read_file(SOURCE_DIR / "final.shp")
    if shape.crs is None:
        shape = shape.set_crs("EPSG:5179", allow_override=True)
    elif shape.crs.to_epsg() != 5179:
        shape = shape.to_crs("EPSG:5179")
    shape["region"] = shape["region"].map(clean_region)
    return shape.sort_values("region").reset_index(drop=True)


def padded_bounds(bounds: np.ndarray, x_pad_frac=0.010, y_pad_frac=0.008) -> np.ndarray:
    xmin, ymin, xmax, ymax = bounds
    w = xmax - xmin
    h = ymax - ymin
    return np.array([xmin - w * x_pad_frac, ymin - h * y_pad_frac, xmax + w * x_pad_frac, ymax + h * y_pad_frac])


def draw_scale_bar(ax, length_km=100):
    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()
    w = xmax - xmin
    h = ymax - ymin
    x0 = xmin + 0.030 * w
    y0 = ymin + 0.080 * h
    length = length_km * 1000
    tick = 0.008 * h
    ax.plot([x0, x0 + length / 2], [y0, y0], color="black", linewidth=0.55, solid_capstyle="butt", zorder=10)
    ax.plot([x0 + length / 2, x0 + length], [y0, y0], color="#bdbdbd", linewidth=0.55, solid_capstyle="butt", zorder=10)
    for frac, label in [(0.0, "0"), (0.5, "50"), (1.0, "100")]:
        x = x0 + frac * length
        ax.plot([x, x], [y0, y0 + tick], color="black", linewidth=0.35, zorder=11)
        ax.text(x, y0 + 0.013 * h, label, ha="center", va="bottom", fontsize=FS_SCALE, color=SUBTEXT, zorder=11)
    ax.text(x0 + length / 2, y0 - 0.012 * h, "km", ha="center", va="top", fontsize=FS_SCALE, color=SUBTEXT, zorder=11)


def plot_choropleth(ax, shape_all, panel_subset):
    shape_all.plot(ax=ax, color=EXCLUDED_COLOR, edgecolor="#dcdcdc", linewidth=EDGE_LW, zorder=1)
    for label in BREAK_LABELS:
        part = panel_subset[panel_subset["incidence_class"] == label]
        if not part.empty:
            part.plot(ax=ax, color=BREAK_COLORS[label], edgecolor=EDGE, linewidth=EDGE_LW, zorder=3)


CONNECTOR = "#a6a6a6"
CONNECTOR_LW = 0.4


def add_busan_inset(parent_ax, shape_all, panel_subset, geumjeong, busan_extent, main_extent):
    # Locator inset sitting in the sea whitespace to the lower-right of Busan,
    # tied to the real Busan location by two thin grey connector lines. No label.
    ix0, iy0, iw, ih = 0.745, 0.150, 0.215, 0.215
    ins = parent_ax.inset_axes([ix0, iy0, iw, ih])
    plot_choropleth(ins, shape_all, panel_subset)
    ins.set_xlim(busan_extent[0], busan_extent[2])
    ins.set_ylim(busan_extent[1], busan_extent[3])
    ins.set_aspect("equal")
    ins.set_xticks([])
    ins.set_yticks([])
    for sp in ins.spines.values():
        sp.set_edgecolor(INSET_BORDER)
        sp.set_linewidth(0.35)
    if not geumjeong.empty:
        geumjeong.plot(ax=ins, facecolor="none", edgecolor=GEUMJEONG_EDGE, linewidth=GEUMJEONG_LW_INSET, zorder=6)

        # Two thin connector lines from the Busan location on the main map to the
        # inset's near (left) corners. Data fills the equal-aspect axes box, so
        # data fraction == axes fraction.
        gx, gy = geumjeong.geometry.iloc[0].representative_point().coords[0]
        xf = (gx - main_extent[0]) / (main_extent[2] - main_extent[0])
        yf = (gy - main_extent[1]) / (main_extent[3] - main_extent[1])
        for corner_y in (iy0 + ih, iy0):
            parent_ax.plot([xf, ix0], [yf, corner_y], transform=parent_ax.transAxes,
                           color=CONNECTOR, lw=CONNECTOR_LW, zorder=5, clip_on=False,
                           solid_capstyle="round")


def main() -> None:
    data_path = OUT_DIR / "Figure1_data_used.csv"
    shape = load_shapes()
    fig1 = pd.read_csv(data_path, encoding="utf-8-sig")
    fig1["region"] = fig1["region"].map(clean_region)
    fig1["panel_code"] = fig1["panel"].str[0]

    kept_regions = set(fig1["region"].unique())
    removed = set(shape["region"]) - kept_regions
    if removed != REMOVED_ISLANDS_EXPECTED:
        raise RuntimeError(f"Unexpected removed islands: {sorted(removed)}")
    if len(kept_regions) != 223:
        raise RuntimeError(f"Expected 223 analysis districts, got {len(kept_regions)}.")

    map_gdf = shape.merge(fig1, on="region", how="inner")
    map_gdf["incidence_class"] = pd.Categorical(map_gdf["incidence_class"], categories=BREAK_LABELS, ordered=True)
    if len(map_gdf) != 446:
        raise RuntimeError(f"Expected 446 mapped district-period rows, got {len(map_gdf)}.")

    province_gdf = (
        shape[shape["region"].isin(kept_regions)]
        .assign(sido=lambda x: x["region"].str.extract(r"^(.+?[시도])")[0])
        .dissolve(by="sido").reset_index()
    )
    geumjeong = shape[shape["region"] == "부산시금정구"]
    extent = padded_bounds(shape.total_bounds)

    # Busan metro zoom extent (Busan districts + ~45% margin for context).
    busan = shape[shape["region"].str.startswith("부산시")]
    bb = busan.total_bounds
    bw, bh = bb[2] - bb[0], bb[3] - bb[1]
    pad = 0.45
    busan_extent = np.array([bb[0] - bw * pad, bb[1] - bh * pad, bb[2] + bw * pad, bb[3] + bh * pad])

    fig, axes = plt.subplots(1, 2, figsize=(FIG_W, FIG_H), constrained_layout=False)
    for idx, (ax, (panel_code, period_label)) in enumerate(zip(axes, PERIODS)):
        subset = map_gdf[map_gdf["panel_code"] == panel_code]
        plot_choropleth(ax, shape, subset)
        province_gdf.plot(ax=ax, facecolor="none", edgecolor=PROVINCE_EDGE, linewidth=PROVINCE_LW, zorder=4)
        ax.set_xlim(extent[0], extent[2])
        ax.set_ylim(extent[1], extent[3])
        ax.set_aspect("equal")
        ax.set_axis_off()
        ax.text(0.012, 0.992, panel_code, transform=ax.transAxes, ha="left", va="top",
                fontsize=FS_PANEL_LETTER, fontweight="bold", color=TEXT, clip_on=False)
        ax.text(0.070, 0.990, period_label, transform=ax.transAxes, ha="left", va="top",
                fontsize=FS_PANEL_PERIOD, fontweight="normal", color=SUBTEXT, clip_on=False)
        if idx == 0:
            draw_scale_bar(ax)
            add_busan_inset(ax, shape, subset, geumjeong, busan_extent, extent)

    handles = [
        Patch(facecolor=BREAK_COLORS[label], edgecolor="#808080", linewidth=0.15, label=label)
        for label in BREAK_LABELS
    ]
    # Vertical legend mimicking the typhoid add_v41_legend layout: small font,
    # compact swatches/spacing, anchored low inside Panel B with loc="center" +
    # bbox_to_anchor, and an invisible frame. Category labels only (no title).
    legend = axes[1].legend(
        handles=handles,
        loc="center", bbox_to_anchor=(0.82, 0.17),
        frameon=False, ncol=1,
        fontsize=FS_LEGEND_LABEL,
        handlelength=0.92, handleheight=0.8, labelspacing=0.26,
        handletextpad=0.36, borderpad=0.3,
    )
    legend.set_zorder(20)
    fig.subplots_adjust(left=0.004, right=0.996, top=0.995, bottom=0.015, wspace=0.02)

    out_png = OUT_DIR / "Figure1_period_maps.png"
    out_tiff = OUT_DIR / "Figure_1.tiff"
    fig.savefig(out_png, dpi=DPI, facecolor="white")   # PNG only (comparison stage)
    save_lzw_tiff(fig, out_tiff)
    fig_w_px = int(round(FIG_W * DPI))
    fig_h_px = int(round(FIG_H * DPI))
    plt.close(fig)

    caption = (
        "Fig. 1. Period-specific maps of average annual crude incidence of "
        "paratyphoid fever per 100,000 population, South Korea (223 connected "
        "districts). Panel A, 2001-2010; Panel B, 2011-2024. Both panels share an "
        "identical colour scale and classification; grey indicates districts with "
        "zero reported cases. The inset in panel A enlarges the Busan metropolitan "
        "area; Busan Geumjeong-gu, the district most affected in the documented "
        "2002 outbreak, is outlined in black. Six island districts were excluded "
        "to match the queen-contiguity analysis set. This is a descriptive map of "
        "crude incidence and does not indicate model-based elevated risk."
    )
    (OUT_DIR / "Figure1_caption.txt").write_text(caption + "\n", encoding="utf-8")

    validation = pd.DataFrame(
        {
            "check": [
                "output_formats", "analysis_districts", "period_rows", "removed_island_count",
                "national_geumjeong_outline", "busan_inset", "inset_geumjeong_label",
                "shared_breaks", "font_family", "panel_label_pt", "legend_title_pt", "dpi",
            ],
            "value": [
                "PNG and TIFF", len(kept_regions), len(map_gdf), len(removed),
                "none (removed)", "Panel A, small locator in whitespace", "none",
                "; ".join(BREAK_LABELS), "Arial", f"{FS_PANEL_LETTER} bold / {FS_PANEL_PERIOD} reg",
                f"{FS_LEGEND_TITLE} regular", DPI,
            ],
            "expected": [
                "PNG and TIFF", "223", "446", "6",
                "none (removed)", "Panel A, small locator in whitespace", "none",
                "; ".join(BREAK_LABELS), "Arial", f"{FS_PANEL_LETTER} bold / {FS_PANEL_PERIOD} reg",
                f"{FS_LEGEND_TITLE} regular", str(DPI),
            ],
        }
    )
    validation["status"] = np.where(validation["value"].astype(str) == validation["expected"].astype(str), "PASS", "CHECK")
    validation.to_csv(OUT_DIR / "Figure1_period_maps_validation.csv", index=False, encoding="utf-8-sig")

    hash_rows = [{"source_file": str(data_path.relative_to(REPO_ROOT)), "sha256": sha256(data_path), "access": "READ_ONLY"}]
    for ext in ("shp", "shx", "dbf", "prj"):
        path = SOURCE_DIR / f"final.{ext}"
        if path.exists():
            hash_rows.append({"source_file": str(path.relative_to(REPO_ROOT)), "sha256": sha256(path), "access": "READ_ONLY"})
    hashes = pd.DataFrame(hash_rows)
    hashes.to_csv(OUT_DIR / "Figure1_period_maps_source_hashes.csv", index=False, encoding="utf-8-sig")

    w_cm, h_cm = FIG_W * 2.54, FIG_H * 2.54
    print("=== Figure 1 INSET vertical-legend FINAL v3 (PNG + TIFF) ===")
    print(f"Saved PNG: {out_png.relative_to(REPO_ROOT)}")
    print(f"Saved TIFF: {out_tiff.relative_to(REPO_ROOT)}")
    print(f"Dimensions: {FIG_W} x {FIG_H} in  =  {w_cm:.2f} x {h_cm:.2f} cm  ({fig_w_px} x {fig_h_px} px @ {DPI} dpi)")
    print("Font: Arial | national Geumjeong outline: removed | Busan inset: Panel A small locator (no label)")
    print("Color breaks (per 100,000): " + "; ".join(BREAK_LABELS))


if __name__ == "__main__":
    main()
