#!/usr/bin/env python3
"""Render the figures in this folder from the bundled CSVs in ../data.

Every number drawn here is recomputed from data/ at render time — nothing is
hard-coded. Run `python figures/make_figures.py` from the repo root (or from
inside figures/) to regenerate.

Light and dark variants are written for each figure so the README renders
correctly in either GitHub theme.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

# --- Theme -------------------------------------------------------------------
# Two selected themes, not an automatic flip: each series hue is stepped for its
# own surface, and both pairs are validated for colour-vision deficiency
# separation (worst-pair CVD dE 24.7 light / 26.8 dark).
THEMES = {
    "light": {
        "surface": "#fcfcfb",
        "ink": "#0b0b0b",
        "ink_soft": "#52514e",
        "grid": "#e3e2de",
        "ours": "#2a78d6",
        "ref": "#eb6834",
    },
    "dark": {
        "surface": "#1a1a19",
        "ink": "#ffffff",
        "ink_soft": "#c3c2b7",
        "grid": "#383835",
        "ours": "#3987e5",
        "ref": "#d95926",
    },
}


def find_data_dir() -> Path:
    """Locate data/ whether we're run from the repo root or from figures/."""
    for base in (Path.cwd(), *Path.cwd().parents, Path(__file__).resolve().parent.parent):
        cand = base / "data"
        if (cand / "forest_carbon_flux_ci.csv").exists():
            return cand
    raise FileNotFoundError("Could not locate data/. Run from the repo root.")


def load() -> pd.DataFrame:
    """Join our per-state results to the Walters reference, one sign convention.

    Walters publishes negative = sink; we report positive = sink. Negating a
    flux flips the sign *and* swaps which bound is upper vs lower.
    """
    d = find_data_dir()
    ours = pd.read_csv(d / "forest_carbon_flux_ci.csv")
    wal = pd.read_csv(d / "walters_2026_frf_net_flux_2023.csv")
    ref = pd.DataFrame(
        {
            "state_name": wal["State"],
            "ref": -wal["2023 Flux Estimate (MMT CO2 Eq.)"],
            "ref_lo": -wal["Upper Bound (MMT CO2 Eq.)"],
            "ref_hi": -wal["Lower Bound (MMT CO2 Eq.)"],
        }
    )
    df = ours.merge(ref, on="state_name", how="inner").rename(
        columns={
            "point_mmt_c": "ours",
            "ci_lower_mmt_c": "ours_lo",
            "ci_upper_mmt_c": "ours_hi",
        }
    )
    df["overlap"] = (df.ours_lo <= df.ref_hi) & (df.ref_lo <= df.ours_hi)
    df["in_band"] = (df.ours >= df.ref_lo) & (df.ours <= df.ref_hi)
    return df


def style(ax, t: dict) -> None:
    ax.set_facecolor(t["surface"])
    ax.grid(True, color=t["grid"], lw=0.6, alpha=0.9)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(t["grid"])
    ax.tick_params(colors=t["ink_soft"], labelsize=9, length=3, width=0.8)


def fig_1to1(df: pd.DataFrame, mode: str, out: Path) -> None:
    """Agreement plot: one series against the identity line, so no legend box."""
    t = THEMES[mode]
    agg_o, agg_r = df.ours.sum(), df.ref.sum()
    pct = (agg_o - agg_r) / abs(agg_r) * 100

    fig, ax = plt.subplots(figsize=(6.8, 7.0), dpi=200)
    fig.patch.set_facecolor(t["surface"])
    style(ax, t)

    lim = [
        min(df.ref_lo.min(), df.ours_lo.min()) - 1.5,
        max(df.ref_hi.max(), df.ours_hi.max()) + 1.5,
    ]
    ax.plot(lim, lim, ls=(0, (5, 4)), lw=1.0, color=t["ink_soft"], alpha=0.55, zorder=1)
    # Label the reference line in the empty lower-left corner, clear of the cluster.
    anchor = lim[0] + (lim[1] - lim[0]) * 0.11
    ax.annotate(
        "1:1  (exact agreement)",
        xy=(anchor, anchor),
        xytext=(11, -12),
        textcoords="offset points",
        color=t["ink_soft"],
        fontsize=8.5,
        rotation=45,
        rotation_mode="anchor",
    )

    # 2D 95% CI bars recede behind the points; the point carries the estimate.
    ax.errorbar(
        df.ref,
        df.ours,
        xerr=[df.ref - df.ref_lo, df.ref_hi - df.ref],
        yerr=[df.ours - df.ours_lo, df.ours_hi - df.ours],
        fmt="none",
        ecolor=t["ours"],
        elinewidth=1.0,
        alpha=0.32,
        capsize=0,
        zorder=2,
    )
    # A surface-coloured ring separates overlapping points in the dense cluster.
    ax.plot(
        df.ref,
        df.ours,
        "o",
        ms=5.2,
        mfc=t["ours"],
        mec=t["surface"],
        mew=0.7,
        ls="none",
        zorder=3,
    )

    ax.set_xlim(lim)
    ax.set_ylim(lim)
    ax.set_aspect("equal")
    ax.set_xlabel(
        "Forest Service published estimate (MMT C/yr)", color=t["ink_soft"], fontsize=9.5
    )
    ax.set_ylabel("This reproduction (MMT C/yr)", color=t["ink_soft"], fontsize=9.5)
    # Title sits above a three-line subtitle; pad clears the subtitle block.
    ax.set_title(
        "Reproduction vs. published federal estimate",
        color=t["ink"],
        fontsize=12.5,
        fontweight="bold",
        pad=52,
        loc="left",
    )
    ax.text(
        0.0,
        1.012,
        f"Forest-Land-Remaining-Forest-Land net flux, 2023 · {len(df)} states\n"
        f"Totals {agg_o:+.1f} vs {agg_r:+.1f} MMT C/yr ({pct:+.1f}%) · "
        f"{int(df.overlap.sum())}/{len(df)} state CIs overlap\n"
        f"Bars are 95% CIs on both axes · positive = sink",
        transform=ax.transAxes,
        color=t["ink_soft"],
        fontsize=8.5,
        linespacing=1.5,
        va="bottom",
    )
    fig.tight_layout()
    fig.savefig(out, facecolor=t["surface"], bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {out}")


def fig_by_state(df: pd.DataFrame, mode: str, out: Path) -> None:
    """Per-state view: two series, so a legend is always present."""
    t = THEMES[mode]
    d = df.sort_values("ours").reset_index(drop=True)
    y = range(len(d))
    off = 0.19

    fig, ax = plt.subplots(figsize=(7.4, 12.0), dpi=200)
    fig.patch.set_facecolor(t["surface"])
    style(ax, t)
    ax.axvline(0, color=t["ink_soft"], lw=0.8, alpha=0.45, zorder=1)

    for series, colour, label, shift, marker in (
        ("ours", t["ours"], "This reproduction", off, "o"),
        ("ref", t["ref"], "Forest Service published", -off, "s"),
    ):
        lo, hi = (f"{series}_lo", f"{series}_hi")
        ypos = [v + shift for v in y]
        ax.errorbar(
            d[series],
            ypos,
            xerr=[d[series] - d[lo], d[hi] - d[series]],
            fmt="none",
            ecolor=colour,
            elinewidth=1.1,
            alpha=0.45,
            capsize=0,
            zorder=2,
        )
        ax.plot(
            d[series],
            ypos,
            marker,
            ms=4.6,
            mfc=colour,
            mec=t["surface"],
            mew=0.6,
            ls="none",
            label=label,
            zorder=3,
        )

    ax.set_yticks(list(y))
    ax.set_yticklabels(d.state, fontsize=8.5)
    ax.set_ylim(-0.8, len(d) - 0.2)
    ax.set_xlabel("Net flux (MMT C/yr, positive = sink)", color=t["ink_soft"], fontsize=9.5)
    ax.set_title(
        "Every state, with 95% confidence intervals",
        color=t["ink"],
        fontsize=12.5,
        fontweight="bold",
        pad=40,
        loc="left",
    )
    ax.text(
        0.0,
        1.004,
        f"Forest-Land-Remaining-Forest-Land net flux, 2023\n"
        f"Sorted by this reproduction's estimate · {int(df.in_band.sum())}/{len(df)} "
        f"of our points fall inside the published 95% band",
        transform=ax.transAxes,
        color=t["ink_soft"],
        fontsize=8.5,
        linespacing=1.5,
        va="bottom",
    )
    leg = ax.legend(
        loc="upper left", frameon=True, fontsize=9.5, facecolor=t["surface"], edgecolor=t["grid"]
    )
    for txt in leg.get_texts():
        txt.set_color(t["ink_soft"])
    fig.tight_layout()
    fig.savefig(out, facecolor=t["surface"], bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {out}")


def main() -> None:
    df = load()
    here = Path(__file__).resolve().parent
    for mode in ("light", "dark"):
        suffix = "" if mode == "light" else "-dark"
        fig_1to1(df, mode, here / f"frf-vs-published-1to1{suffix}.png")
        fig_by_state(df, mode, here / f"frf-by-state{suffix}.png")


if __name__ == "__main__":
    main()
