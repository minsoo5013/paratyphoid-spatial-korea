#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(readr)
})

repo_root <- normalizePath(getwd(), winslash = "/", mustWork = TRUE)
if (basename(repo_root) == "R") repo_root <- dirname(repo_root)
fig_dir <- file.path(repo_root, "figures")
results_dir <- file.path(repo_root, "results")

required <- file.path(
  fig_dir,
  c(
    "Figure1_period_maps.png",
    "Figure_1.tiff",
    "Figure1_period_maps.py",
    "Figure1_caption.txt",
    "Figure1_data_used.csv",
    "Figure2_moran_cases.png",
    "Figure_2.tiff",
    "Figure2_moran_cases.py",
    "Figure2_caption.txt"
  )
)
exists_flag <- file.exists(required)
validation <- data.frame(
  file = basename(required),
  exists = exists_flag,
  bytes = ifelse(exists_flag, file.info(required)$size, NA_real_),
  status = ifelse(exists_flag & file.info(required)$size > 0, "PASS", "FAIL")
)
readr::write_csv(validation, file.path(results_dir, "figure_validation.csv"))

if (any(validation$status != "PASS")) stop("Figure validation failed.")

message("Figure validation complete.")
