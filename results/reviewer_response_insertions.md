# Reviewer response insertions

**Status:** draft language for Methods/Supplementary/Limitations; verify against final tables before submission.

## 1. Model priors and specification
We fitted negative binomial Bayesian disease-mapping models using INLA, with the expected number of reported cases modeled with a log population offset. The selected M6 model included fixed covariates, a classic BYM district-level spatial random effect, an RW1 temporal random effect, and an iid district-year interaction term. Penalized-complexity priors were specified for the BYM unstructured and spatial precisions and for the RW1 and iid precisions as `pc.prec` with parameters `(0.5, 0.01)`; fixed-effect priors were INLA defaults because no `control.fixed` option was specified in the archived code.

## 2. Elevated RR formula
For district-level elevated-risk classification, we used the posterior distribution of the first 223 rows of the classic BYM `idarea` random-effect block from the archived M6 INLA object. The posterior spatial relative risk was defined as `RR_i = exp(b_i)`, where `b_i` denotes that archived BYM `idarea` block. A district was classified as elevated only when the lower bound of the 95% credible interval for `RR_i` exceeded 1.

## 3. Posterior exceedance probability
No district met the 95% credible-interval elevated-risk criterion in the main 223-district M6 model. Exceedance screening identified 18 districts with Pr(RR>1)>0.8 and 2 districts with Pr(RR>1)>0.9; these, if discussed, should be described only as suggestive and not robust elevated-risk districts.

## 4. LISA multiple testing
Local Moran's I analyses were used descriptively to identify which districts contributed to annual global autocorrelation signals. We therefore report both unadjusted permutation p-values and Benjamini-Hochberg FDR-adjusted q-values, and we do not interpret unadjusted LISA clusters as formal high-risk designations.

## 5. EB-smoothed Moran sensitivity
Empirical Bayes-smoothed rates preserved the contrast between the early and contemporary periods: mean EB-smoothed Moran's I was 0.054 across 6 evaluable early-period years and 0.010 across 13 evaluable contemporary-period years. The 2002 signal remained positive under EB smoothing (I=0.200, p=<0.001), while the 2010 EB-smoothed Moran's I was not estimable because the EB-smoothed rates were constant across districts, consistent with low-count instability rather than a robust residual spatial cluster.

## 6. Island re-inclusion sensitivity
As a sensitivity analysis, all 229 districts were reintroduced using KNN K=4 adjacency and the M6 structure. The island-reincluded model yielded 0 elevated districts by the 95% credible-interval criterion. This analysis is interpreted as a connectivity sensitivity only; the main model remains the 223-district Queen-contiguity analysis.

## 7. Zero-inflation limitation/justification
Although zero district-years were common (88.7%), the final NB M6 model had no residual spatial autocorrelation by raw or Pearson residual Moran tests. Because the inferential target was persistent spatial risk rather than zero-count prediction, zero-inflated or hurdle models were not used as the primary analysis and are better framed as future predictive extensions.

## 8. Future work
Future work could evaluate predictive extensions such as zero-inflated or hurdle disease-mapping models and compare them prospectively with the NB-BYM-RW1-IID specification, particularly for very sparse notifiable disease data.
