# M6 model specification

**Status:** reviewer-response support; approved-to-proceed M6, not a forced manuscript rewrite.

## Likelihood and linear predictor
- Likelihood: INLA `family = "nbinomial"`.
- INLA reports the NB hyperparameter as `size for the nbinomial observations (1/overdispersion)`.
- Offset: `log(population)`.

`log(mu_it) = log(pop_it) + alpha + X_it beta + spatial_i + temporal_t + interaction_it`

Archived M6 formula:

```r
cases ~ elderly_t3_z + urban_population_z + sex_ratio_z + longterm_hospital_z + clinic_z + general_hospital_z + family_medicine_clinic_z + physicians_per_1000_z + offset(log(population)) + f(idarea, model='bym', graph=graph, scale.model=TRUE, hyper=pc_bym) + f(idtime, model='rw1', hyper=pc_prec) + f(idarea_time, model='iid', hyper=pc_prec)
```

## Random effects and priors
- Spatial effect: classic BYM (`model='bym'`), not BYM2.
- Structured and unstructured BYM hyperpriors in archived code:

```r
pc_bym <- list(
  prec.unstruct = list(prior = "pc.prec", param = c(0.5, 0.01)),
  prec.spatial = list(prior = "pc.prec", param = c(0.5, 0.01))
)
```

- RW1 temporal precision prior/hyperprior: `prec = list(prior = "pc.prec", param = c(0.5, 0.01))`.
- IID space-time precision prior/hyperprior: `prec = list(prior = "pc.prec", param = c(0.5, 0.01))`.
- Fixed-effect priors: no `control.fixed` was specified in archived code; INLA defaults were used.

## INLA controls
- INLA version: 25.10.19.
- Seed in confirmatory run: 20260713.
- `inla.setOption(num.threads = "1:1")`.
- `control.compute = list(dic = TRUE, waic = TRUE, cpo = TRUE)`.
- `control.predictor = list(link = 1)`.

## Fit criteria and residual Moran's I
- M6 DIC: 2474.664.
- M6 WAIC: 2475.955.
- Raw residual Moran's I: -0.0096 (p=0.546).
- Pearson residual Moran's I: -0.0104 (p=0.554).
- Residual Moran's I was calculated after aggregating district-level residuals over 2011-2024 and testing against the same spatial weights.

## Hyperparameter posterior summaries
| hyperparameter | mean | q025 | q500 | q975 |
|---|---:|---:|---:|---:|
| size for the nbinomial observations (1/overdispersion) | 0.8867 | 0.5651 | 0.8684 | 1.3132 |
| Precision for idarea (iid component) | 4263.4080 | 16.6579 | 365.8482 | 27628.5000 |
| Precision for idarea (spatial component) | 32.0956 | 5.6657 | 21.6701 | 124.5061 |
| Precision for idtime | 31.1510 | 6.9041 | 24.7346 | 94.0544 |
| Precision for idarea_time | 140117.6000 | 5.3533 | 297.0969 | 289338.7000 |

## Posterior spatial RR definition used for elevated-district flag
- Archived code uses the first 223 rows of `fit$summary.random$idarea` from the classic BYM random-effect block.
- The elevated flag is based on `exp(0.025quant) > 1` for this first BYM `idarea` block.
- The archived code does **not** compute a fixed-effect included total latent RR and does **not** explicitly add the two BYM blocks as `exp(u_i + v_i)`.

Baseline extraction code lines:

```r
spatial_summary <- spatial_summary[seq_len(nrow(shape)), , drop = FALSE]
    posterior_RR = exp(.data$spatial_log_mean),
    posterior_RR_CrI_lower = exp(.data$spatial_log_CrI_lower),
    cluster_class = case_when(
      .data$posterior_RR_CrI_lower > 1 ~ "elevated",
  spatial_random$cluster_class == "elevated"
  spatial_random$cluster_class == "lower"
```

Confirmatory elevated-count code lines:

```r
  spatial_summary <- spatial_summary[seq_len(223), , drop = FALSE]
  sum(exp(spatial_summary$`0.025quant`) > 1, na.rm = TRUE)
```
