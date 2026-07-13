#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(dplyr)
  library(readr)
})

repo_root <- normalizePath(getwd(), winslash = "/", mustWork = TRUE)
if (basename(repo_root) == "R") repo_root <- dirname(repo_root)
results_dir <- file.path(repo_root, "results")

cutpoint <- readr::read_csv(file.path(results_dir, "cutpoint_sensitivity.csv"), show_col_types = FALSE)
model_summary <- readr::read_csv(file.path(results_dir, "model_sensitivity_summary.csv"), show_col_types = FALSE)
island_knn <- readr::read_csv(file.path(results_dir, "island_reincluded_KNN_sensitivity_summary.csv"), show_col_types = FALSE)
lisa <- readr::read_csv(file.path(results_dir, "LISA_FDR_sensitivity_summary.csv"), show_col_types = FALSE)
eb <- readr::read_csv(file.path(results_dir, "EB_smoothed_Moran_period_summary.csv"), show_col_types = FALSE)
zero <- readr::read_csv(file.path(results_dir, "zero_inflation_diagnostic.csv"), show_col_types = FALSE)

zero_value <- function(metric_name) {
  zero |> filter(metric == metric_name) |> pull(value) |> as.numeric()
}

validation <- tibble::tibble(
  check = c(
    "cutpoint_direction_consistent_all",
    "model_sensitivity_elevated_zero_all",
    "island_knn_elevated_zero",
    "lisa_fdr_zero_all",
    "early_eb_mean_moran_greater_than_contemporary",
    "observed_zero_pct_close_to_locked",
    "predicted_zero_pct_close_to_locked"
  ),
  value = c(
    as.integer(all(cutpoint$direction_consistent)),
    as.integer(all(model_summary$elevated_cluster_count == 0)),
    as.integer(island_knn$elevated_district_count[1] == 0),
    as.integer(all(lisa$FDR_0_05_significant_clusters == 0)),
    as.integer(
      eb$mean_EB_Moran_I[eb$period == "early_2001_2010"] >
        eb$mean_EB_Moran_I[eb$period == "contemporary_2011_2024"]
    ),
    zero_value("observed_zero_proportion"),
    zero_value("mean_predicted_zero_probability")
  ),
  expected = c(1, 1, 1, 1, 1, 0.887, 0.882),
  tolerance = c(0, 0, 0, 0, 0, 0.01, 0.01)
) |>
  mutate(status = if_else(abs(value - expected) <= tolerance, "PASS", "REVIEW"))

readr::write_csv(validation, file.path(results_dir, "sensitivity_validation.csv"))
if (any(validation$status != "PASS")) stop("Sensitivity validation flagged a drift.")

message("Sensitivity validation complete.")
