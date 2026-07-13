#!/usr/bin/env Rscript

set.seed(20260713)

required_packages <- c("readr", "dplyr", "spdep", "INLA")
installed <- vapply(required_packages, requireNamespace, logical(1), quietly = TRUE)
if (!all(installed)) {
  stop(
    "Install required R package(s): ",
    paste(required_packages[!installed], collapse = ", ")
  )
}

INLA::inla.setOption(num.threads = "1:1")

repo_root <- normalizePath(getwd(), winslash = "/", mustWork = TRUE)
if (basename(repo_root) == "R") repo_root <- dirname(repo_root)
dir.create(file.path(repo_root, "results"), showWarnings = FALSE)

version_check <- data.frame(
  component = c("R", "INLA", "seed"),
  value = c(
    paste(R.version$major, R.version$minor, sep = "."),
    as.character(utils::packageVersion("INLA")),
    "20260713"
  )
)
readr::write_csv(version_check, file.path(repo_root, "results", "environment_check.csv"))
writeLines(capture.output(sessionInfo()), file.path(repo_root, "results", "sessionInfo.txt"))

message("Setup complete.")
