# Data

## Included
- `panel.csv` — derived district-year analytic dataset (223 connected districts × 2011–2024),
  de-identified and population-aggregated. Columns: district code, year, case count,
  population (offset), and the pre-specified area-level covariates.
- `annual_panel_2001_2024.csv` — derived annual case/rate panel for the 223-district
  spatial-autocorrelation analysis.
- `region_id_lookup.csv` — mapping between the model index (`idarea`) and public district
  names.
- `adjacency_queen.graph` and `adjacency_queen_edges.csv` — queen-contiguity neighbour
  structure for the 223 connected districts.
- `adjacency_knn_k4_223.graph` / `adjacency_knn_k4_223_edges.csv` and
  `adjacency_knn_k4_229.graph` / `adjacency_knn_k4_229_edges.csv` — KNN K = 4 sensitivity
  adjacency structures.

## Not redistributed here
- Administrative boundary geometries (district polygons) are obtained from their original
  public providers and are **not** included. The tabular model and Moran analyses can be
  reproduced from the included derived panels and graph files; the map PNGs are included
  under `figures/`.

## Sources
- Case counts: Korea Disease Control and Prevention Agency (KDCA) Infectious Disease Portal
  — https://dportal.kdca.go.kr/
- Population & administrative covariates: Korean Statistical Information Service (KOSIS)
  — https://kosis.kr/  and related public agencies.

Only de-identified, population-level aggregated data are used.

> Map lines delineate study areas and do not necessarily depict accepted national boundaries.
