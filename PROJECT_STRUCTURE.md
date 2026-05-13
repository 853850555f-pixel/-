# Project Structure

This workspace contains several analysis tracks developed during topic exploration. The current recommended report topic is:

> City/area-level PM2.5 exposure and child autism spectrum disorder risk.

The PM2.5-ASD track is the current mainline. Lead-ASD and NHANES lead-cognition scripts are retained as exploratory or backup work.

## Current Mainline: PM2.5-ASD City/Area Analysis

Run these scripts in this order if you need to reproduce the current report outputs.

### 1. `process_exposure_2019_2021.py`

Purpose: Clean and aggregate raw EPA PM2.5-bound lead and PM2.5 files for 2019-2021.

Main inputs:
- `lead 2019.xlsx`
- `lead 2020.xlsx`
- `lead 2021.xlsx`
- `daily_88101_2019.csv`
- `daily_88101_2020.csv`
- `daily_88101_2021.csv`
- `asd_state_2022_nsch.csv`

Main outputs:
- `lead_pm25_2019_2021_clean.csv`
- `lead_pm25_2019_2021_state_year.csv`
- `pm25_2019_2021_state_year.csv`
- `pm25_2019_2021_state_mean.csv`
- `state_exposure_2019_2021_mean_lead_pm25.csv`
- `analysis_state_asd_2022_exposure_2019_2021.csv`

Status: foundational preprocessing. Still useful because it prepares state-level PM2.5 and lead data.

### 2. `process_county_exposure_2019_2021.py`

Purpose: Build county-level 2019-2021 exposure tables from the cleaned EPA data.

Main inputs:
- `lead_pm25_2019_2021_clean.csv`
- `daily_88101_2019.csv`
- `daily_88101_2020.csv`
- `daily_88101_2021.csv`

Main outputs:
- `lead_pm25_2019_2021_county_year.csv`
- `pm25_2019_2021_county_year.csv`
- `county_exposure_2019_2021_mean_lead_pm25.csv`
- `county_exposure_2019_2021_summary.csv`

Status: required for ADDM-area PM2.5 aggregation.

### 3. `merge_county_acs_covariates_2022.py`

Purpose: Add ACS 2022 county-level demographic/SES covariates to county exposure data.

Main inputs:
- `county_exposure_2019_2021_mean_lead_pm25.csv`

Main outputs:
- `acs_2022_county_covariates.csv`
- `county_exposure_2019_2021_mean_lead_pm25_with_acs.csv`
- `county_acs_2022_merge_summary.csv`

Status: required for population-weighted ADDM-area aggregation.

### 4. `match_addm_2020_exposure.py`

Purpose: Match CDC ADDM 2020 surveillance areas to county/county-group exposure values.

Main inputs:
- `county_exposure_2019_2021_mean_lead_pm25_with_acs.csv`
- hard-coded ADDM 2020 site prevalence and county crosswalk in the script

Main outputs:
- `addm_2020_exposure_matched.csv`
- `addm_2020_county_exposure_detail.csv`
- `addm_2020_site_county_crosswalk.csv`
- `addm_2020_site_prevalence.csv`
- `addm_2020_exposure_match_summary.csv`

Status: required for the city/area PM2.5-ASD report.

Important note: Some ADDM sites only describe partial counties or county groups. The script keeps `match_quality` explicit so the report can discuss spatial boundary uncertainty.

### 5. `analyze_pm25_asd_city_focus.py`

Purpose: Current main analysis script for the report. It focuses on PM2.5, not lead.

Main inputs:
- `addm_2020_exposure_matched.csv`
- `analysis_state_asd_2022_exposure_2019_2021_with_covariates.csv`

Main outputs directory:
- `pm25_asd_city_results/`

Main outputs:
- `pm25_asd_correlations.csv`
- `pm25_asd_ols_results.csv`
- `pm25_asd_key_results.json`
- `addm_pm25_asd_city_analysis_dataset.csv`
- `addm_pm25_asd_sensitivity_dataset.csv`
- `addm_pm25_asd_scatter_city_focus.png`
- `addm_pm25_asd_scatter_sensitivity.png`
- `state_pm25_asd_scatter_supplement.png`
- `城市PM25_ASD结果摘要.md`

Status: main report analysis.

### 6. `make_pm25_asd_report_figures.py`

Purpose: Generate report/PPT-ready figures for the PM2.5-ASD topic.

Main inputs:
- `pm25_asd_city_results/addm_pm25_asd_city_analysis_dataset.csv`
- `pm25_asd_city_results/addm_pm25_asd_sensitivity_dataset.csv`
- `analysis_state_asd_2022_exposure_2019_2021_with_covariates.csv`
- `pm25_asd_city_results/pm25_asd_correlations.csv`

Main outputs directory:
- `pm25_asd_city_results/report_figures/`

Main outputs:
- `figure1_data_flow.png`
- `figure2_addm_ranked_pm25_asd.png`
- `figure3_main_addm_scatter.png`
- `figure4_sensitivity_scatter.png`
- `figure5_correlation_comparison.png`
- `figure6_state_supplement_scatter.png`
- `图表清单.md`
- `figure_captions.csv`

Status: final figure generation.

### 7. `make_pm25_asd_report_tables.py`

Purpose: Render report tables as PNG images.

Main inputs:
- `pm25_asd_city_results/pm25_asd_correlations.csv`
- `pm25_asd_city_results/pm25_asd_ols_results.csv`

Main outputs directory:
- `pm25_asd_city_results/report_tables/`

Main outputs:
- `table1_data_sources.png`
- `table2_descriptive_statistics.png`
- `table3_correlations.png`
- `table4_regression_results.png`
- `表格图片清单.md`
- `table_image_index.csv`

Status: final table image generation.

## Supporting State-Level PM2.5-ASD Scripts

These are useful for supplemental state-level analysis but are no longer the main narrative.

### `merge_acs_covariates_2022.py`

Purpose: Add ACS 2022 state-level covariates.

Main outputs:
- `acs_2022_state_covariates.csv`
- `analysis_state_asd_2022_exposure_2019_2021_with_covariates.csv`

Status: required for `analyze_pm25_asd_city_focus.py` state supplement.

### `analyze_asd_exposure_2019_2021.py`

Purpose: Original state-level analysis of lead, PM2.5, and ASD.

Main outputs:
- `analysis_results_2019_2021/`

Status: legacy exploratory analysis. It showed PM2.5 had a weak positive association with ASD, while lead was not significant.

### `analyze_asd_exposure_with_covariates.py`

Purpose: Original state-level OLS analysis with ACS covariates.

Main outputs:
- `analysis_results_2019_2021_covariates/`

Status: supplemental/legacy. Shows the PM2.5 coefficient remains positive but becomes weaker after SES adjustment.

### `prepare_county_asd_analysis_template.py`

Purpose: Prepare a county-level ASD analysis template if county ASD data becomes available.

Main outputs:
- `county_asd_2022_analysis_template.csv`
- `county_asd_2022_analysis_template_us50_dc.csv`

Status: not used in the current report because county-level ASD outcome data are missing.

## Legacy ADDM Lead/PM2.5 Script

### `analyze_addm_2020_exposure.py`

Purpose: Earlier ADDM analysis including both PM2.5-bound lead and PM2.5.

Main outputs:
- `analysis_results_addm_2020/`

Status: legacy. Useful for historical comparison, but the current report should use `analyze_pm25_asd_city_focus.py` because it focuses cleanly on PM2.5.

Key finding from legacy output:
- PM2.5 showed a strong positive ADDM-area association with ASD.
- PM2.5-bound lead did not show a significant association with ASD.

## Backup Topic: NHANES III Lead-Cognition

These scripts belong to the alternative topic on blood lead and child cognition. They are not part of the current PM2.5-ASD report.

### `prepare_nhanes3_lead_cognition.py`

Purpose: Download NHANES III fixed-width files and prepare a child blood lead-cognition CSV.

Main outputs:
- `nhanes3_lead_cognition/`
- `nhanes3_child_lead_cognition_analysis.csv`
- `nhanes3_lead_cognition_variable_dictionary.csv`

Status: backup topic only.

### `analyze_nhanes3_lead_cognition.py`

Purpose: Analyze blood lead and child cognitive scores in NHANES III.

Main outputs:
- `nhanes3_lead_cognition_results/`

Status: backup topic only.

## 2025 Exploratory Scripts

### `process_lead_2025.py`

### `process_state_exposure_2025.py`

Purpose: Early 2025 exposure-processing exploration.

Status: not used in the current report.

## Recommended Reproduction Commands

From `D:\VSCODE\认知心理学`, run:

```powershell
python process_exposure_2019_2021.py
python process_county_exposure_2019_2021.py
python merge_county_acs_covariates_2022.py
python merge_acs_covariates_2022.py
python match_addm_2020_exposure.py
python analyze_pm25_asd_city_focus.py
python make_pm25_asd_report_figures.py
python make_pm25_asd_report_tables.py
```

If the intermediate CSV files already exist, you usually only need:

```powershell
python analyze_pm25_asd_city_focus.py
python make_pm25_asd_report_figures.py
python make_pm25_asd_report_tables.py
```

## Current Report Outputs To Use

Use these files for the final PM2.5-ASD report:

- `pm25_asd_city_results/城市PM25_ASD结果摘要.md`
- `pm25_asd_city_results/报告图表与表格.md`
- `pm25_asd_city_results/report_figures/`
- `pm25_asd_city_results/report_tables/`

## Interpretation Guardrails

- Use PM2.5 as the main exposure. Do not make lead the central explanatory variable for ASD because lead-ASD results were not significant.
- Describe the ADDM analysis as city/metro-area or monitoring-area ecological analysis.
- Do not claim causality. Use wording such as "positive ecological association" or "exploratory association".
- Explicitly note limitations: small ADDM sample, approximate county matching, ecological design, and incomplete control for confounding.
