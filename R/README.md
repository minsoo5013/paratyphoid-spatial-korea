# R scripts

Scripts run in numbered order. Each is the **cleaned, public** version of the analysis
pipeline: exploratory variable-search loops are removed and the confirmed covariate set is
fixed and hard-coded, so a single run reproduces the reported model exactly.

| Script | Purpose | Key outputs |
|---|---|---|
| `00_setup.R` | packages, paths, seed (20260713), INLA options | — |
| `01_build_panel.R` | validate the included 223-district × year panel and adjacency files | `results/panel_validation.csv`, `results/adjacency_validation.csv` |
| `02_moran.R` | annual global Moran's I recomputation | `results/moran_annual_recomputed.csv`, `results/moran_annual_validation.csv` |
| `03_model_inla.R` | fit M1–M6; DIC/WAIC checks; posterior spatial RR = `exp(b_i)`; exceedance Pr(RR>1) | `results/model_comparison_recomputed.csv`, `results/posterior_spatial_RR_exceedance_recomputed.csv` |
| `04_sensitivity.R` | period-boundary, KNN adjacency, observation window, EB-smoothed Moran, LISA FDR validation | `results/sensitivity_validation.csv` |
| `05_figures.R` | validate included Figure 1/2 PNG files and figure scripts | `results/figure_validation.csv` |

## Public-release rules (must hold before commit)

1. **No automatic variable selection in the published scripts.** Forward selection / AUTO
   candidate screening is exploratory only and must not appear here. The confirmed covariate
   set is fixed and hard-coded.
2. **Final model is M6**: NB + classic BYM (not BYM2) + RW1 + IID; PC prior `pc.prec(0.5, 0.01)`
   on all four precisions; INLA defaults for fixed effects.
3. **Main adjacency = queen contiguity, 223 connected districts** (islands excluded);
   KNN is sensitivity only. This ordering must never be reversed.
4. Strip debug prints, commented-out dead code, and scratch paths. Keep only what is needed
   to reproduce the reported results.
5. Set `set.seed(20260713)` and INLA's seed where applicable so runs are deterministic.
