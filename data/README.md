# Bundled data — provenance and columns

Three tables. One holds our estimates; two are published federal references we
compare against. All flux values are **MMT C per year** (million metric tons of
carbon), not CO₂ equivalent.

Sign conventions differ between our file and the two reference files. This is the
most common way to get a wrong answer from these tables — see the README's
[Sign and units](../README.md#sign-and-units-read-this-before-using-the-numbers)
section before joining them to anything.

---

## `forest_carbon_flux_ci.csv` — our estimates

Per-state Forest Land Remaining Forest Land net carbon flux for 2023, with 95%
confidence intervals from a stratified bootstrap over FIA plots. 48 rows, one per
contiguous state. **Positive = sink.**

| Column | Meaning |
|---|---|
| `state` | Two-letter state abbreviation |
| `state_name` | Full state name — the join key against the Walters table |
| `evalid` | The FIA evaluation identifier the estimate was computed from. This pins the estimate to a specific inventory cycle and plot set |
| `point_mmt_c` | Point estimate of annual net flux, MMT C/yr, positive = sink |
| `ci_lower_mmt_c`, `ci_upper_mmt_c` | Bounds of the 95% confidence interval |
| `ci_half_width_mmt_c` | Half-width of that interval, for convenience |
| `n_pairs` | Number of remeasured plot pairs behind the estimate. Flux requires two measurements of the same plot, so this is smaller than the state's total plot count |
| `n_iter`, `seed` | Bootstrap iteration count and random seed — fixed, so the interval is reproducible rather than re-randomised each run |
| `perturb_litter`, `perturb_soc` | Whether published parameter uncertainty for the forest-floor and soil-organic-carbon pool models was propagated into the interval (1 = yes for all rows here) |
| `forest_carbon_version` | Version string of the estimator build that produced the row. The estimator itself is being prepared for release as part of `pyfia` — see the main README |

Because `n_iter` and `seed` are fixed and recorded, and `evalid` names the input,
each row is a re-runnable claim rather than a one-off number.

**What the interval does and does not cover:** plot sampling uncertainty, plus
published parameter uncertainty for the litter and soil organic carbon pool
models. It does **not** include tree-biomass model (NSVB) parameter uncertainty,
which drives most of the flux. Treat the widths as a lower bound.

---

## `walters_2026_frf_net_flux_2023.csv` — primary federal reference

State-level Forest Land Remaining Forest Land net flux for 2023 with published
95% bounds, from the Forest Service data archive that underlies the national
inventory. **Negative = sink** (opposite of our file).

| Column | Meaning |
|---|---|
| `State` | Full state name |
| `2023 Flux Estimate (MMT CO2 Eq.)` | Point estimate. **Despite the header, the values are MMT C, not CO₂ equivalent** |
| `Lower Bound (MMT CO2 Eq.)`, `Upper Bound (MMT CO2 Eq.)` | 95% bounds; same unit mislabel |
| `Lower Bound (Percent)`, `Upper Bound (Percent)` | The same bounds as percentages of the estimate |

> **The header mislabel is in the source archive, not introduced here.** Confirmed
> against Walters' main flux table: Alabama reads −55.56 in CO₂e there, and
> −55.56 × 12/44 = −15.15, which matches this file's Alabama value. No CO₂→C
> conversion is applied to these columns anywhere in this repository.

Because our file is positive = sink and this one is negative = sink, converting
between them flips the sign **and** swaps which bound is upper versus lower. The
notebooks do this explicitly; if you do it yourself, do not forget the swap.

This table covers more geography than we do (including Alaska, Hawaii, and the
territories). The notebooks inner-join on state name, which drops the rows we do
not estimate.

Source: Walters et al. 2026, https://doi.org/10.2737/RDS-2026-0031

---

## `epa_a208_2022.csv` — secondary federal reference

EPA's published Annex 3.13 Table A-208 state-level flux for **2022** — one year
earlier than everything else here. **Negative = sink.**

| Column | Meaning |
|---|---|
| `state`, `state_name` | State identifiers |
| `flux_mmt_c_2022` | Point estimate for 2022 |
| `lower_bound_mmt_c`, `upper_bound_mmt_c` | 95% bounds |
| `lower_bound_pct`, `upper_bound_pct` | The same bounds as percentages |

This is a **cross-check against a different reference year**, so the comparison to
it (+5.9%) is not the headline agreement figure and should never be described as a
difference "versus Walters." Most of that gap is the one-year offset: the 2023
federal total is roughly 14 MMT C above the 2022 figure.

Source: U.S. EPA, *Inventory of U.S. Greenhouse Gas Emissions and Sinks*,
Annex 3.13, Table A-208.

---

## Licensing

Our estimates are CC BY 4.0. The two federal tables are U.S. Government works,
redistributed unmodified except for reshaping into CSV. See
[`../LICENSE-data`](../LICENSE-data).
