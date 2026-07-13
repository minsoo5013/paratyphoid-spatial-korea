#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(dplyr)
  library(INLA)
  library(readr)
  library(spdep)
})

set.seed(20260713)
INLA::inla.setOption(num.threads = "1:1")

repo_root <- normalizePath(getwd(), winslash = "/", mustWork = TRUE)
if (basename(repo_root) == "R") repo_root <- dirname(repo_root)
data_dir <- file.path(repo_root, "data")
results_dir <- file.path(repo_root, "results")
dir.create(results_dir, showWarnings = FALSE)

panel <- readr::read_csv(file.path(data_dir, "panel.csv"), show_col_types = FALSE) |>
  arrange(idarea, year)
lookup <- readr::read_csv(file.path(data_dir, "region_id_lookup.csv"), show_col_types = FALSE)
graph <- INLA::inla.read.graph(file.path(data_dir, "adjacency_queen.graph"))
edges <- readr::read_csv(file.path(data_dir, "adjacency_queen_edges.csv"), show_col_types = FALSE)

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
stopifnot(all(fixed_covariates %in% names(panel)))
stopifnot(nrow(panel) == 3121L, dplyr::n_distinct(panel$idarea) == 223L)

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

listw <- spdep::nb2listw(make_nb(edges, graph$n), style = "W", zero.policy = TRUE)
pc_bym <- list(
  prec.unstruct = list(prior = "pc.prec", param = c(0.5, 0.01)),
  prec.spatial = list(prior = "pc.prec", param = c(0.5, 0.01))
)
pc_prec <- list(prec = list(prior = "pc.prec", param = c(0.5, 0.01)))
base_formula <- paste(
  "cases ~", paste(fixed_covariates, collapse = " + "),
  "+ offset(log(population))"
)
formula_strings <- c(
  M1 = base_formula,
  M2 = paste0(base_formula, " + f(idarea, model='besag', graph=graph, scale.model=TRUE, hyper=pc_prec)"),
  M3 = paste0(base_formula, " + f(idarea, model='bym', graph=graph, scale.model=TRUE, hyper=pc_bym)"),
  M4 = paste0(base_formula, " + f(idarea, model='bym', graph=graph, scale.model=TRUE, hyper=pc_bym) + f(idarea_time, model='iid', hyper=pc_prec)"),
  M5 = paste0(base_formula, " + f(idarea, model='bym', graph=graph, scale.model=TRUE, hyper=pc_bym) + f(idtime, model='rw1', hyper=pc_prec)"),
  M6 = paste0(base_formula, " + f(idarea, model='bym', graph=graph, scale.model=TRUE, hyper=pc_bym) + f(idtime, model='rw1', hyper=pc_prec) + f(idarea_time, model='iid', hyper=pc_prec)")
)
model_labels <- tibble::tibble(
  model = names(formula_strings),
  structure = c(
    "NB, covariates only",
    "NB + ICAR",
    "NB + BYM",
    "NB + BYM + IID",
    "NB + BYM + RW1",
    "NB + BYM + RW1 + IID"
  )
)

fit_one <- function(model_name) {
  f <- as.formula(formula_strings[[model_name]])
  environment(f) <- environment()
  INLA::inla(
    f,
    family = "nbinomial",
    data = panel,
    control.compute = list(dic = TRUE, waic = TRUE, cpo = TRUE),
    control.predictor = list(link = 1),
    verbose = FALSE
  )
}

residual_moran <- function(fit) {
  area_resid <- panel |>
    mutate(
      fitted = as.numeric(fit$summary.fitted.values$mean),
      raw_residual = cases - fitted,
      pearson_residual = raw_residual / sqrt(pmax(fitted, 1e-9))
    ) |>
    group_by(idarea) |>
    summarise(
      raw_residual = sum(raw_residual),
      pearson_residual = mean(pearson_residual),
      .groups = "drop"
    ) |>
    arrange(idarea)
  raw <- spdep::moran.test(area_resid$raw_residual, listw, zero.policy = TRUE)
  pearson <- spdep::moran.test(area_resid$pearson_residual, listw, zero.policy = TRUE)
  tibble::tibble(
    resid_moran_raw = as.numeric(raw$estimate[["Moran I statistic"]]),
    p_raw = raw$p.value,
    resid_moran_pearson = as.numeric(pearson$estimate[["Moran I statistic"]]),
    p_pearson = pearson$p.value
  )
}

elevated_count <- function(fit, model_name) {
  if (model_name == "M1" || is.null(fit$summary.random$idarea)) return(NA_integer_)
  spatial <- fit$summary.random$idarea[seq_len(graph$n), , drop = FALSE]
  sum(exp(spatial$`0.025quant`) > 1, na.rm = TRUE)
}

fits <- lapply(names(formula_strings), fit_one)
names(fits) <- names(formula_strings)

comparison <- dplyr::bind_rows(lapply(names(fits), function(model_name) {
  fit <- fits[[model_name]]
  tibble::tibble(
    model = model_name,
    DIC = as.numeric(fit$dic$dic),
    WAIC = as.numeric(fit$waic$waic),
    elevated_districts = elevated_count(fit, model_name),
    mode_status = if (!is.null(fit$mode$mode.status)) as.character(fit$mode$mode.status) else NA_character_,
    CPO_failure_count = if (!is.null(fit$cpo$failure)) sum(fit$cpo$failure > 0, na.rm = TRUE) else NA_integer_
  ) |>
    bind_cols(residual_moran(fit))
})) |>
  left_join(model_labels, by = "model") |>
  select(
    model, structure, DIC, WAIC,
    resid_moran_raw, p_raw, resid_moran_pearson, p_pearson,
    elevated_districts, mode_status, CPO_failure_count
  )
readr::write_csv(comparison, file.path(results_dir, "model_comparison_recomputed.csv"))

m6 <- fits$M6
spatial_summary <- m6$summary.random$idarea[seq_len(graph$n), , drop = FALSE]
marginals <- m6$marginals.random$idarea[seq_len(graph$n)]
rr <- tibble::tibble(
  idarea = seq_len(graph$n),
  RR_median = exp(spatial_summary$`0.5quant`),
  RR_mean = exp(spatial_summary$mean),
  RR_CrI_lower = exp(spatial_summary$`0.025quant`),
  RR_CrI_upper = exp(spatial_summary$`0.975quant`),
  Pr_RR_gt_1 = vapply(marginals, function(m) 1 - INLA::inla.pmarginal(0, m), numeric(1))
) |>
  left_join(lookup, by = "idarea") |>
  mutate(
    elevated_95CrI_flag = RR_CrI_lower > 1,
    exceedance_0_8_flag = Pr_RR_gt_1 > 0.8,
    exceedance_0_9_flag = Pr_RR_gt_1 > 0.9
  ) |>
  select(idarea, region, everything())
readr::write_csv(rr, file.path(results_dir, "posterior_spatial_RR_exceedance_recomputed.csv"))

fixed <- m6$summary.fixed
fixed <- fixed[rownames(fixed) != "(Intercept)", , drop = FALSE]
fixed_out <- tibble::tibble(
  safe_name = rownames(fixed),
  beta_mean = fixed$mean,
  beta_sd = fixed$sd,
  beta_CrI_lower = fixed$`0.025quant`,
  beta_CrI_upper = fixed$`0.975quant`,
  IRR = exp(fixed$mean),
  IRR_CrI_lower = exp(fixed$`0.025quant`),
  IRR_CrI_upper = exp(fixed$`0.975quant`)
)
readr::write_csv(fixed_out, file.path(results_dir, "fixed_effects_M6_recomputed.csv"))

if (file.exists(file.path(results_dir, "model_comparison.csv"))) {
  locked <- readr::read_csv(file.path(results_dir, "model_comparison.csv"), show_col_types = FALSE)
  validation <- comparison |>
    select(model, DIC, WAIC, elevated_districts) |>
    left_join(
      locked |> select(model, locked_DIC = DIC, locked_WAIC = WAIC, locked_elevated_districts = elevated_districts),
      by = "model"
    ) |>
    mutate(
      delta_DIC = DIC - locked_DIC,
      delta_WAIC = WAIC - locked_WAIC,
      status = if_else(abs(delta_DIC) <= 0.05 & abs(delta_WAIC) <= 0.05, "PASS", "REVIEW")
    )
  readr::write_csv(validation, file.path(results_dir, "model_comparison_validation.csv"))
  if (any(validation$status != "PASS")) stop("INLA model-comparison values drifted from locked table.")
}

message("INLA model recomputation complete.")
