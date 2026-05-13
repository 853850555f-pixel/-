# City PM2.5 Exposure and Child ASD Risk

This repository contains scripts, cleaned analysis datasets, and report-ready outputs for a course project on city/area-level PM2.5 exposure and child autism spectrum disorder (ASD) prevalence.

## Current Topic

City/area-level PM2.5 exposure and child ASD risk: an ecological analysis using CDC ADDM 2020 surveillance areas and EPA 2019-2021 PM2.5 monitoring data.

## Key Results

- In 11 CDC ADDM 2020 surveillance areas, 2019-2021 mean PM2.5 exposure was positively correlated with ASD prevalence among 8-year-old children.
- Main ADDM sample: Pearson `r = 0.752`, `p = 0.0076`.
- Boundary sensitivity sample: Pearson `r = 0.935`, `p = 0.0020`.
- State-level supplemental analysis: Pearson `r = 0.296`, `p = 0.0348`.

These are ecological associations and should not be interpreted as individual-level causal evidence.

## Main Files

- `PROJECT_STRUCTURE.md`: script architecture and reproduction order.
- `scripts/`: Python scripts used for preprocessing, analysis, figures, and table images.
- `data/`: small cleaned analysis datasets needed for final analysis reproduction.
- `results/`: final PM2.5-ASD result tables, figures, table images, and Chinese summaries.

## Reproduce Final Outputs

If the cleaned datasets in `data/` are present, run from the repository root:

```powershell
python scripts/analyze_pm25_asd_city_focus.py
python scripts/make_pm25_asd_report_figures.py
python scripts/make_pm25_asd_report_tables.py
```

Outputs will be written to `results/pm25_asd_city_results/`.

Note: the original EPA daily PM2.5 raw CSV files are not included because they are large. The final cleaned datasets and outputs are included.

## Limitations

- ADDM sample size is small.
- Several ADDM surveillance areas require approximate county/county-group matching.
- The design is ecological and cannot infer individual-level causality.
- PM2.5 exposure window does not perfectly represent prenatal or early-life exposure.
