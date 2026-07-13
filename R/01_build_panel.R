#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(dplyr)
  library(INLA)
  library(readr)
})

repo_root <- normalizePath(getwd(), winslash = "/", mustWork = TRUE)
if (basename(repo_root) == "R") repo_root <- dirname(repo_root)
data_dir <- file.path(repo_root, "data")
results_dir <- file.path(repo_root, "results")
dir.create(results_dir, showWarnings = FALSE)

panel <- readr::read_csv(file.path(data_dir, "panel.csv"), show_col_types = FALSE)
annual <- readr::read_csv(file.path(data_dir, "annual_panel_2001_2024.csv"), show_col_types = FALSE)
queen <- INLA::inla.read.graph(file.path(data_dir, "adjacency_queen.graph"))
queen_edges <- readr::read_csv(file.path(data_dir, "adjacency_queen_edges.csv"), show_col_types = FALSE)

fixed_covariates <- c(
  "elderly_t3_z",
  "urban_population_z",
  "sex_ratio_z",
  "longterm_hospital_z",
  "clinic_z",
  "general_hospital_z",
  "family_medicine_clinic_z",
  "physicians_per_1000_z"
)

panel_validation <- tibble::tibble(
  check = c(
    "model_panel_rows",
    "model_panel_districts",
    "model_panel_year_min",
    "model_panel_year_max",
    "model_panel_cases",
    "missing_cases",
    "missing_population",
    "nonpositive_population",
    "fixed_covariates_present"
  ),
  value = c(
    nrow(panel),
    dplyr::n_distinct(panel$idarea),
    min(panel$year),
    max(panel$year),
    sum(panel$cases),
    sum(is.na(panel$cases)),
    sum(is.na(panel$population)),
    sum(panel$population <= 0, na.rm = TRUE),
    as.integer(all(fixed_covariates %in% names(panel)))
  ),
  expected = c(3121, 223, 2011, 2024, 462, 0, 0, 0, 1)
) |>
  mutate(status = if_else(value == expected, "PASS", "FAIL"))

annual_validation <- tibble::tibble(
  check = c("annual_rows", "annual_districts", "year_min", "year_max", "total_cases"),
  value = c(
    nrow(annual),
    dplyr::n_distinct(annual$idarea),
    min(annual$year),
    max(annual$year),
    sum(annual$cases)
  ),
  expected = c(5352, 223, 2001, 2024, 1139)
) |>
  mutate(status = if_else(value == expected, "PASS", "FAIL"))

adjacency_validation <- tibble::tibble(
  check = c("queen_nodes", "queen_directed_edges", "queen_isolates"),
  value = c(queen$n, nrow(queen_edges), sum(queen$nnbs == 0)),
  expected = c(223, nrow(queen_edges), 0)
) |>
  mutate(status = if_else(value == expected, "PASS", "FAIL"))

readr::write_csv(panel_validation, file.path(results_dir, "panel_validation.csv"))
readr::write_csv(annual_validation, file.path(results_dir, "annual_panel_validation.csv"))
readr::write_csv(adjacency_validation, file.path(results_dir, "adjacency_validation.csv"))

if (any(panel_validation$status != "PASS") ||
    any(annual_validation$status != "PASS") ||
    any(adjacency_validation$status != "PASS")) {
  stop("Panel or adjacency validation failed.")
}

message("Panel and adjacency validation complete.")
