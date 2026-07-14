# Changing spatial patterns of paratyphoid fever in South Korea, 2001–2024

Analysis code and derived data for the study:

> Lee, M., Kim, S. *Changing spatial patterns of paratyphoid fever after a major waterborne outbreak in South Korea, 2001–2024.*

This repository reproduces the spatial-autocorrelation description and the Bayesian
spatiotemporal model used in the manuscript. It is released for reproducibility;
the archived release is (or will be) assigned a DOI through Zenodo.

## Study summary

Nationwide district-level notification data (2001–2024) were analysed across 223
connected districts (six island districts with no contiguous neighbour under queen
contiguity were excluded). Global and local Moran's I were tracked annually, an early
period (2001–2010) and a contemporary modelling period (2011–2024) were defined, and a
negative-binomial Bayesian spatiotemporal model was fitted for the contemporary period.

## Repository layout

```
R/          analysis scripts (numbered in execution order)
data/       derived district-year analytic datasets + adjacency
figures/    publication figure PNG/TIFF files, captions, Figure 1 plotting data, and figure scripts
results/    model-comparison, posterior, and sensitivity summary tables
```

## Environment

| Component | Version / setting |
|---|---|
| R | see `sessionInfo()` in `results/sessionInfo.txt` |
| R-INLA | 25.10.19 |
| Random seed | 20260713 |
| Adjacency (main) | queen contiguity (`sf` / `spdep::poly2nb`), 223 connected districts |
| Adjacency (sensitivity) | k-nearest-neighbour (K = 4) on the full 229 districts |

INLA is not on CRAN; install from the INLA repository:

```r
install.packages(
  "INLA",
  repos = c(getOption("repos"), INLA = "https://inla.r-inla-download.org/R/stable"),
  dep = TRUE
)
```

## Model specification (final model, M6)

Negative-binomial likelihood with:

- **BYM** convolution (structured Besag ICAR + unstructured IID spatial) — *classic BYM, not BYM2*
- **RW1** temporal trend (year)
- **IID** space–time interaction
- Population offset (`log(population)`), pre-specified area-level covariates as fixed effects

Priors: penalised-complexity prior `pc.prec(0.5, 0.01)` on each of the four precisions
(structured spatial, unstructured spatial, RW1, IID); INLA defaults for fixed effects.

Model selection among M1–M6 is reported in `results/` (DIC / WAIC). "Elevated" districts
are defined as those whose lower 95% credible-interval bound for the posterior spatial
relative risk `exp(b_i)` (the combined BYM convolution term, first 223 rows of the area
index) exceeds 1.

## Reproducing the analysis

```bash
Rscript R/00_setup.R          # packages, paths, seed
Rscript R/01_build_panel.R    # validate derived district-year panels + adjacency
Rscript R/02_moran.R          # annual global/local Moran's I
Rscript R/03_model_inla.R     # M1–M6 fit, posterior RR, exceedance checks
Rscript R/04_sensitivity.R    # period boundary, KNN, window, EB Moran, LISA FDR checks
Rscript R/05_figures.R        # validate included PNG figures and figure scripts
```

(Scripts are provided by the analysis pipeline; see `R/README.md`.)

## Data

The paratyphoid notification counts are publicly available from the Korea Disease Control
and Prevention Agency Infectious Disease Portal (https://dportal.kdca.go.kr/); population
and administrative covariates are from the Korean Statistical Information Service
(https://kosis.kr/) and related public agencies. Only de-identified, population-level
aggregated data are used. The derived district-year analytic datasets and adjacency graphs
needed to reproduce the tabular analyses are included under `data/`. Administrative
boundary geometries are obtained from their original public providers and are not
redistributed here; see `data/README.md`.

> Map lines delineate study areas and do not necessarily depict accepted national boundaries.

## Ethics

Approved by the Institutional Review Board of Hongik University (approval no.
7002340-202511-HR-012). The requirement for individual informed consent was waived because
the data were anonymised and aggregated at the population level.

## Citation

See `CITATION.cff`. Once a release DOI is minted, cite the specific version DOI.

## License

Code: MIT (see `LICENSE`). Derived data files under `data/` are released under
CC-BY-4.0 unless a redistributed source imposes other terms (see `data/README.md`).
