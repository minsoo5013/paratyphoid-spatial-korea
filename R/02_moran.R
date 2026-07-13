#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(dplyr)
  library(readr)
  library(spdep)
})

repo_root <- normalizePath(getwd(), winslash = "/", mustWork = TRUE)
if (basename(repo_root) == "R") repo_root <- dirname(repo_root)
data_dir <- file.path(repo_root, "data")
results_dir <- file.path(repo_root, "results")
dir.create(results_dir, showWarnings = FALSE)

annual <- readr::read_csv(file.path(data_dir, "annual_panel_2001_2024.csv"), show_col_types = FALSE)
edges <- readr::read_csv(file.path(data_dir, "adjacency_queen_edges.csv"), show_col_types = FALSE)

make_nb <- function(edges, n) {
  neighbours <- vector("list", n)
  split_edges <- split(edges$to, edges$from)
  for (i in seq_len(n)) {
    neighbours[[i]] <- as.integer(split_edges[[as.character(i)]])
    if (length(neighbours[[i]]) == 0) neighbours[[i]] <- integer(0)
  }
  class(neighbours) <- "nb"
  attr(neighbours, "region.id") <- as.character(seq_len(n))
  attr(neighbours, "type") <- "edge_list"
  attr(neighbours, "sym") <- TRUE
  neighbours
}

nb <- make_nb(edges, max(annual$idarea))
listw <- spdep::nb2listw(nb, style = "W", zero.policy = TRUE)

annual_moran <- annual |>
  arrange(year, idarea) |>
  group_by(year) |>
  group_modify(\(.x, .y) {
    stopifnot(all(.x$idarea == seq_len(max(.x$idarea))))
    test <- spdep::moran.test(.x$crude_rate, listw, zero.policy = TRUE)
    tibble::tibble(
      districts = nrow(.x),
      total_cases = sum(.x$cases),
      total_population = sum(.x$population),
      crude_incidence_per_100k = sum(.x$cases) / sum(.x$population) * 100000,
      zero_district_pct = mean(.x$cases == 0) * 100,
      moran_i = as.numeric(test$estimate[["Moran I statistic"]]),
      expected_i = as.numeric(test$estimate[["Expectation"]]),
      variance = as.numeric(test$estimate[["Variance"]]),
      p_value = test$p.value,
      significant_p05 = test$p.value < 0.05
    )
  }) |>
  ungroup()

readr::write_csv(annual_moran, file.path(results_dir, "moran_annual_recomputed.csv"))

if (file.exists(file.path(results_dir, "moran_annual.csv"))) {
  locked <- readr::read_csv(file.path(results_dir, "moran_annual.csv"), show_col_types = FALSE)
  validation <- annual_moran |>
    select(year, moran_i, p_value, total_cases) |>
    inner_join(
      locked |> select(year, locked_moran_i = moran_i, locked_p_value = p_value, locked_total_cases = total_cases),
      by = "year"
    ) |>
    mutate(
      delta_moran_i = moran_i - locked_moran_i,
      delta_p_value = p_value - locked_p_value,
      delta_cases = total_cases - locked_total_cases,
      status = if_else(abs(delta_moran_i) <= 1e-10 & delta_cases == 0, "PASS", "REVIEW")
    )
  readr::write_csv(validation, file.path(results_dir, "moran_annual_validation.csv"))
  if (any(validation$status != "PASS")) stop("Annual Moran's I drifted from locked table.")
}

message("Annual Moran's I recomputation complete.")
