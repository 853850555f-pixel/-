"""Create report-ready figures for the PM2.5-ASD project."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf


OUT_DIR = Path("results/pm25_asd_city_results")
FIG_DIR = OUT_DIR / "report_figures"
ADDM_FILE = OUT_DIR / "addm_pm25_asd_city_analysis_dataset.csv"
SENS_FILE = OUT_DIR / "addm_pm25_asd_sensitivity_dataset.csv"
STATE_FILE = Path("data/analysis_state_asd_2022_exposure_2019_2021_with_covariates.csv")
CORR_FILE = OUT_DIR / "pm25_asd_correlations.csv"

ADDM_ASD = "asd_prevalence_per_1000"
ADDM_PM25 = "PM25_2019_2021_mean_ugm3_pop_weighted"
STATE_ASD = "ASD_2022_current_pct"
STATE_PM25 = "PM25_2019_2021_mean_ugm3"


plt.rcParams["font.family"] = ["DejaVu Sans", "Arial", "sans-serif"]
plt.rcParams["axes.spines.top"] = False
plt.rcParams["axes.spines.right"] = False


def savefig(name: str) -> None:
    plt.tight_layout()
    plt.savefig(FIG_DIR / name, dpi=300, bbox_inches="tight")
    plt.close()


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    addm = pd.read_csv(ADDM_FILE, encoding="utf-8-sig")
    sens = pd.read_csv(SENS_FILE, encoding="utf-8-sig")
    state = pd.read_csv(STATE_FILE, encoding="utf-8-sig")
    corr = pd.read_csv(CORR_FILE, encoding="utf-8-sig")
    for df, pm25, asd in [(addm, ADDM_PM25, ADDM_ASD), (sens, ADDM_PM25, ADDM_ASD)]:
        df[pm25] = pd.to_numeric(df[pm25], errors="coerce")
        df[asd] = pd.to_numeric(df[asd], errors="coerce")
    state[STATE_PM25] = pd.to_numeric(state[STATE_PM25], errors="coerce")
    state[STATE_ASD] = pd.to_numeric(state[STATE_ASD], errors="coerce")
    return addm, sens, state, corr


def figure_data_flow() -> None:
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.axis("off")
    boxes = [
        (0.03, 0.60, "CDC ADDM 2020\nASD prevalence\nage 8 children"),
        (0.03, 0.18, "EPA AQS 2019-2021\nCounty PM2.5 daily data\n3-year mean exposure"),
        (0.39, 0.39, "County / county-group\nspatial matching\npopulation-weighted PM2.5"),
        (0.73, 0.39, "Analysis dataset\n11 ADDM areas\n7-area sensitivity sample"),
    ]
    for x, y, text in boxes:
        rect = plt.Rectangle((x, y), 0.24, 0.22, facecolor="#EEF3F8", edgecolor="#2F5D8C", linewidth=1.4)
        ax.add_patch(rect)
        ax.text(x + 0.12, y + 0.11, text, ha="center", va="center", fontsize=11)
    arrows = [((0.27, 0.71), (0.39, 0.50)), ((0.27, 0.29), (0.39, 0.50)), ((0.63, 0.50), (0.73, 0.50))]
    for start, end in arrows:
        ax.annotate("", xy=end, xytext=start, arrowprops=dict(arrowstyle="->", lw=1.8, color="#555555"))
    ax.text(0.5, 0.94, "Figure 1. Data Selection and Matching Workflow", ha="center", fontsize=15, weight="bold")
    savefig("figure1_data_flow.png")


def figure_ranked_addm(addm: pd.DataFrame) -> None:
    d = addm[["site", ADDM_PM25, ADDM_ASD]].dropna().sort_values(ADDM_PM25)
    fig, ax1 = plt.subplots(figsize=(10, 6))
    y = np.arange(len(d))
    ax1.barh(y - 0.18, d[ADDM_PM25], height=0.35, color="#6A9BC9", label="PM2.5 (ug/m3)")
    ax1.set_xlabel("PM2.5 exposure (ug/m3)")
    ax1.set_yticks(y)
    ax1.set_yticklabels(d["site"])
    ax2 = ax1.twiny()
    ax2.barh(y + 0.18, d[ADDM_ASD], height=0.35, color="#D98C5F", label="ASD prevalence per 1,000")
    ax2.set_xlabel("ASD prevalence per 1,000")
    ax1.set_title("Figure 2. ADDM Areas Ranked by PM2.5 Exposure")
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="lower right")
    savefig("figure2_addm_ranked_pm25_asd.png")


def add_regression_line(ax: plt.Axes, d: pd.DataFrame, x: str, y: str, color: str) -> None:
    model = smf.ols(f"{y} ~ {x}", data=d).fit()
    xs = np.linspace(d[x].min(), d[x].max(), 100)
    ax.plot(xs, model.params["Intercept"] + model.params[x] * xs, color=color, lw=2.2)


def figure_main_scatter(addm: pd.DataFrame, corr: pd.DataFrame) -> None:
    d = addm[["site", ADDM_PM25, ADDM_ASD, "has_candidate_boundary"]].dropna()
    r = corr.loc[corr["sample"] == "addm_all_sites", "pearson_r"].iloc[0]
    p = corr.loc[corr["sample"] == "addm_all_sites", "pearson_p"].iloc[0]
    fig, ax = plt.subplots(figsize=(9, 6.2))
    colors = np.where(d["has_candidate_boundary"], "#AFAFAF", "#2F5D8C")
    ax.scatter(d[ADDM_PM25], d[ADDM_ASD], s=95, c=colors, alpha=0.92, edgecolors="white", linewidth=0.7)
    add_regression_line(ax, d, ADDM_PM25, ADDM_ASD, "#B33A3A")
    for _, row in d.iterrows():
        ax.annotate(row["site"], (row[ADDM_PM25], row[ADDM_ASD]), fontsize=8, xytext=(4, 3), textcoords="offset points")
    ax.text(0.03, 0.95, f"Pearson r = {r:.3f}\np = {p:.4f}\nn = {len(d)}", transform=ax.transAxes, va="top", fontsize=11, bbox=dict(boxstyle="round", facecolor="white", alpha=0.85, edgecolor="#CCCCCC"))
    ax.set_xlabel("2019-2021 mean PM2.5 exposure (ug/m3)")
    ax.set_ylabel("ADDM 2020 ASD prevalence per 1,000")
    ax.set_title("Figure 3. PM2.5 Exposure and ASD Prevalence in ADDM Areas")
    savefig("figure3_main_addm_scatter.png")


def figure_sensitivity_scatter(sens: pd.DataFrame, corr: pd.DataFrame) -> None:
    d = sens[["site", ADDM_PM25, ADDM_ASD]].dropna()
    r = corr.loc[corr["sample"] == "addm_exclude_candidate_boundaries", "pearson_r"].iloc[0]
    p = corr.loc[corr["sample"] == "addm_exclude_candidate_boundaries", "pearson_p"].iloc[0]
    fig, ax = plt.subplots(figsize=(9, 6.2))
    ax.scatter(d[ADDM_PM25], d[ADDM_ASD], s=105, c="#2F5D8C", alpha=0.92, edgecolors="white", linewidth=0.7)
    add_regression_line(ax, d, ADDM_PM25, ADDM_ASD, "#B33A3A")
    for _, row in d.iterrows():
        ax.annotate(row["site"], (row[ADDM_PM25], row[ADDM_ASD]), fontsize=8, xytext=(4, 3), textcoords="offset points")
    ax.text(0.03, 0.95, f"Pearson r = {r:.3f}\np = {p:.4f}\nn = {len(d)}", transform=ax.transAxes, va="top", fontsize=11, bbox=dict(boxstyle="round", facecolor="white", alpha=0.85, edgecolor="#CCCCCC"))
    ax.set_xlabel("2019-2021 mean PM2.5 exposure (ug/m3)")
    ax.set_ylabel("ADDM 2020 ASD prevalence per 1,000")
    ax.set_title("Figure 4. Sensitivity Analysis: Better-Matched ADDM Areas")
    savefig("figure4_sensitivity_scatter.png")


def figure_correlation_comparison(corr: pd.DataFrame) -> None:
    labels = ["ADDM\nall areas", "ADDM\nsensitivity", "State\nsupplement"]
    d = corr.set_index("sample").loc[
        ["addm_all_sites", "addm_exclude_candidate_boundaries", "state_supplement"]
    ]
    fig, ax = plt.subplots(figsize=(8, 5.6))
    bars = ax.bar(labels, d["pearson_r"], color=["#2F5D8C", "#3E7C59", "#8A8A8A"])
    ax.axhline(0, color="#333333", linewidth=0.8)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Pearson correlation (r)")
    ax.set_title("Figure 5. Correlation Strength Across Analysis Samples")
    for bar, p in zip(bars, d["pearson_p"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.03, f"p={p:.4f}", ha="center", fontsize=10)
    savefig("figure5_correlation_comparison.png")


def figure_state_scatter(state: pd.DataFrame, corr: pd.DataFrame) -> None:
    d = state[["State Name", STATE_PM25, STATE_ASD]].dropna()
    r = corr.loc[corr["sample"] == "state_supplement", "pearson_r"].iloc[0]
    p = corr.loc[corr["sample"] == "state_supplement", "pearson_p"].iloc[0]
    fig, ax = plt.subplots(figsize=(9, 6.2))
    ax.scatter(d[STATE_PM25], d[STATE_ASD], s=48, color="#476C9B", alpha=0.82, edgecolors="white", linewidth=0.5)
    add_regression_line(ax, d, STATE_PM25, STATE_ASD, "#B33A3A")
    ax.text(0.03, 0.95, f"Pearson r = {r:.3f}\np = {p:.4f}\nn = {len(d)}", transform=ax.transAxes, va="top", fontsize=11, bbox=dict(boxstyle="round", facecolor="white", alpha=0.85, edgecolor="#CCCCCC"))
    ax.set_xlabel("2019-2021 mean PM2.5 exposure (ug/m3)")
    ax.set_ylabel("NSCH 2022 current ASD prevalence (%)")
    ax.set_title("Figure 6. Supplemental State-Level PM2.5-ASD Association")
    savefig("figure6_state_supplement_scatter.png")


def write_figure_notes() -> None:
    notes = [
        ("figure1_data_flow.png", "图1 数据选择与匹配流程：展示 ADDM ASD 数据、EPA PM2.5 数据如何通过县/县组匹配形成分析样本。"),
        ("figure2_addm_ranked_pm25_asd.png", "图2 ADDM 地区描述图：按 PM2.5 暴露水平排序，同时展示各地区 ASD 患病率。"),
        ("figure3_main_addm_scatter.png", "图3 主结果散点图：11 个 ADDM 监测地区中，PM2.5 与 ASD 患病率呈显著正相关。"),
        ("figure4_sensitivity_scatter.png", "图4 敏感性分析散点图：排除边界不确定地区后，PM2.5-ASD 正相关仍明显。"),
        ("figure5_correlation_comparison.png", "图5 相关系数比较：比较 ADDM 主样本、敏感性样本和州级补充样本的相关强度。"),
        ("figure6_state_supplement_scatter.png", "图6 州级补充分析：51 个州级地区中，PM2.5 与 ASD 患病率呈较弱但显著的正相关。"),
    ]
    df = pd.DataFrame(notes, columns=["file", "caption_cn"])
    df.to_csv(FIG_DIR / "figure_captions.csv", index=False, encoding="utf-8-sig")
    md = "# 报告图表清单\n\n" + "\n".join([f"- `{f}`：{c}" for f, c in notes]) + "\n"
    (FIG_DIR / "图表清单.md").write_text(md, encoding="utf-8")


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    addm, sens, state, corr = load_data()
    figure_data_flow()
    figure_ranked_addm(addm)
    figure_main_scatter(addm, corr)
    figure_sensitivity_scatter(sens, corr)
    figure_correlation_comparison(corr)
    figure_state_scatter(state, corr)
    write_figure_notes()
    print(f"Figures written to {FIG_DIR}")


if __name__ == "__main__":
    main()
