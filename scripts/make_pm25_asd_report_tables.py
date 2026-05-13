"""Render PM2.5-ASD report tables as PNG images."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


OUT_DIR = Path("results/pm25_asd_city_results")
TABLE_DIR = OUT_DIR / "report_tables"


def render_table(df: pd.DataFrame, title: str, output_name: str, width: float = 12, row_height: float = 0.55) -> None:
    height = max(2.3, row_height * (len(df) + 2.2))
    fig, ax = plt.subplots(figsize=(width, height))
    ax.axis("off")
    ax.set_title(title, fontsize=16, weight="bold", pad=16)

    table = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        loc="center",
        cellLoc="center",
        colLoc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.45)

    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor("#D0D0D0")
        cell.set_linewidth(0.6)
        if row == 0:
            cell.set_facecolor("#2F5D8C")
            cell.set_text_props(color="white", weight="bold")
        elif row % 2 == 0:
            cell.set_facecolor("#F3F6FA")
        else:
            cell.set_facecolor("white")

    fig.tight_layout()
    fig.savefig(TABLE_DIR / output_name, dpi=300, bbox_inches="tight")
    plt.close(fig)


def table_1_data_sources() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ["ASD main", "CDC ADDM 2020", "asd_prevalence_per_1000", "ASD prevalence among age-8 children, per 1,000"],
            ["PM2.5 main", "EPA AQS 2019-2021", "PM25_2019_2021_mean_ugm3_pop_weighted", "Population-weighted ADDM-area PM2.5, ug/m3"],
            ["ASD supplement", "NSCH 2022", "ASD_2022_current_pct", "State-level current child ASD prevalence, %"],
            ["PM2.5 supplement", "EPA AQS 2019-2021", "PM25_2019_2021_mean_ugm3", "State-level mean PM2.5, ug/m3"],
            ["Covariates", "ACS 2022", "income, poverty, education", "State-level SES controls"],
        ],
        columns=["Type", "Source", "Variable", "Description"],
    )


def table_2_descriptives() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ["ADDM areas", "ASD prevalence per 1,000", 11, 28.018, 6.021, 23.100, 27.400, 44.900],
            ["ADDM areas", "PM2.5, ug/m3", 11, 8.503, 0.936, 7.547, 8.204, 10.883],
            ["State supplement", "ASD prevalence, %", 51, 3.351, 1.075, 1.100, 3.300, 5.700],
            ["State supplement", "PM2.5, ug/m3", 51, 7.442, 1.387, 2.930, 7.515, 10.613],
        ],
        columns=["Sample", "Variable", "N", "Mean", "SD", "Min", "Median", "Max"],
    )


def table_3_correlations() -> pd.DataFrame:
    corr = pd.read_csv(OUT_DIR / "pm25_asd_correlations.csv", encoding="utf-8-sig")
    labels = {
        "addm_all_sites": "ADDM all areas",
        "addm_exclude_candidate_boundaries": "ADDM sensitivity sample",
        "state_supplement": "State supplement",
    }
    out = corr.copy()
    out["sample"] = out["sample"].map(labels)
    for col in ["pearson_r", "pearson_p", "spearman_r", "spearman_p"]:
        out[col] = out[col].map(lambda x: f"{x:.4f}" if "p" in col else f"{x:.3f}")
    out = out.rename(
        columns={
            "sample": "Sample",
            "n": "N",
            "pearson_r": "Pearson r",
            "pearson_p": "Pearson p",
            "spearman_r": "Spearman r",
            "spearman_p": "Spearman p",
        }
    )
    return out[["Sample", "N", "Pearson r", "Pearson p", "Spearman r", "Spearman p"]]


def table_4_regressions() -> pd.DataFrame:
    reg = pd.read_csv(OUT_DIR / "pm25_asd_ols_results.csv", encoding="utf-8-sig")
    labels = {
        "addm_all_sites": "ADDM all areas",
        "addm_exclude_candidate_boundaries": "ADDM sensitivity sample",
        "state_unadjusted": "State unadjusted",
        "state_adjusted_ses": "State SES-adjusted",
    }
    out = reg.copy()
    out["model"] = out["model"].map(labels)
    out["coef_pm25"] = out["coef_pm25"].map(lambda x: f"{x:.3f}")
    out["p_value_ols"] = out["p_value_ols"].map(lambda x: "NA" if pd.isna(x) else f"{x:.4f}")
    out["p_value_hc3"] = out["p_value_hc3"].map(lambda x: f"{x:.4f}")
    out["r_squared"] = out["r_squared"].map(lambda x: f"{x:.3f}")
    out = out.rename(
        columns={
            "model": "Model",
            "n": "N",
            "coef_pm25": "PM2.5 coef.",
            "p_value_ols": "OLS p",
            "p_value_hc3": "HC3 p",
            "r_squared": "R2",
        }
    )
    return out[["Model", "N", "PM2.5 coef.", "OLS p", "HC3 p", "R2"]]


def write_index() -> None:
    rows = [
        ["table1_data_sources.png", "Data sources and variable definitions"],
        ["table2_descriptive_statistics.png", "Descriptive statistics"],
        ["table3_correlations.png", "PM2.5-ASD correlation results"],
        ["table4_regression_results.png", "PM2.5-ASD linear regression results"],
    ]
    pd.DataFrame(rows, columns=["file", "description"]).to_csv(TABLE_DIR / "table_image_index.csv", index=False, encoding="utf-8-sig")
    md = "# 表格图片清单\n\n" + "\n".join([f"- `{file}`：{desc}" for file, desc in rows]) + "\n"
    (TABLE_DIR / "表格图片清单.md").write_text(md, encoding="utf-8")


def main() -> None:
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    render_table(table_1_data_sources(), "Table 1. Data Sources and Variables", "table1_data_sources.png", width=15, row_height=0.6)
    render_table(table_2_descriptives(), "Table 2. Descriptive Statistics", "table2_descriptive_statistics.png", width=13, row_height=0.6)
    render_table(table_3_correlations(), "Table 3. PM2.5 and ASD Correlation Results", "table3_correlations.png", width=12, row_height=0.6)
    render_table(table_4_regressions(), "Table 4. PM2.5 and ASD Regression Results", "table4_regression_results.png", width=12, row_height=0.6)
    write_index()
    print(f"Table images written to {TABLE_DIR}")


if __name__ == "__main__":
    main()
