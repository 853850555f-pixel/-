"""City/ADDM-area focused PM2.5 and ASD analysis.

This script reframes the project around PM2.5 exposure and child autism risk,
using CDC ADDM 2020 monitoring areas as the main city/metro-area dataset and
state-level NSCH 2022 as a supplemental ecological check.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats


OUT_DIR = Path("results/pm25_asd_city_results")
ADDM_FILE = Path("data/addm_2020_exposure_matched.csv")
STATE_FILE = Path("data/analysis_state_asd_2022_exposure_2019_2021_with_covariates.csv")

ADDM_ASD = "asd_prevalence_per_1000"
ADDM_PM25 = "PM25_2019_2021_mean_ugm3_pop_weighted"
STATE_ASD = "ASD_2022_current_pct"
STATE_PM25 = "PM25_2019_2021_mean_ugm3"


def corr_stats(df: pd.DataFrame, x: str, y: str) -> dict[str, float | int]:
    d = df[[x, y]].apply(pd.to_numeric, errors="coerce").dropna()
    pearson = stats.pearsonr(d[x], d[y]) if len(d) >= 3 else (np.nan, np.nan)
    spearman = stats.spearmanr(d[x], d[y]) if len(d) >= 3 else (np.nan, np.nan)
    return {
        "n": int(len(d)),
        "pearson_r": float(pearson.statistic),
        "pearson_p": float(pearson.pvalue),
        "spearman_r": float(spearman.statistic),
        "spearman_p": float(spearman.pvalue),
    }


def fit_simple_ols(df: pd.DataFrame, y: str, x: str, label: str) -> dict[str, float | str | int]:
    d = df[[y, x]].apply(pd.to_numeric, errors="coerce").dropna()
    model_plain = smf.ols(f"{y} ~ {x}", data=d).fit()
    model = smf.ols(f"{y} ~ {x}", data=d).fit(cov_type="HC3")
    ci_low, ci_high = model.conf_int().loc[x]
    return {
        "model": label,
        "n": int(model.nobs),
        "coef_pm25": float(model.params[x]),
        "std_error_ols": float(model_plain.bse[x]),
        "p_value_ols": float(model_plain.pvalues[x]),
        "std_error_hc3": float(model.bse[x]),
        "p_value_hc3": float(model.pvalues[x]),
        "ci_low": float(ci_low),
        "ci_high": float(ci_high),
        "r_squared": float(model.rsquared),
    }


def fit_state_adjusted(df: pd.DataFrame) -> dict[str, float | str | int]:
    cols = [
        STATE_ASD,
        STATE_PM25,
        "median_household_income",
        "poverty_rate_pct",
        "bachelor_or_higher_pct",
    ]
    d = df[cols].apply(pd.to_numeric, errors="coerce").dropna()
    formula = (
        f"{STATE_ASD} ~ {STATE_PM25} + median_household_income + "
        "poverty_rate_pct + bachelor_or_higher_pct"
    )
    model = smf.ols(formula, data=d).fit(cov_type="HC3")
    ci_low, ci_high = model.conf_int().loc[STATE_PM25]
    return {
        "model": "state_adjusted_ses",
        "n": int(model.nobs),
        "coef_pm25": float(model.params[STATE_PM25]),
        "std_error_ols": np.nan,
        "p_value_ols": np.nan,
        "std_error_hc3": float(model.bse[STATE_PM25]),
        "p_value_hc3": float(model.pvalues[STATE_PM25]),
        "ci_low": float(ci_low),
        "ci_high": float(ci_high),
        "r_squared": float(model.rsquared),
    }


def scatter_addm(df: pd.DataFrame, sample_col: str | None = None) -> None:
    d = df[["site", ADDM_ASD, ADDM_PM25, "has_candidate_boundary"]].copy()
    d[ADDM_ASD] = pd.to_numeric(d[ADDM_ASD], errors="coerce")
    d[ADDM_PM25] = pd.to_numeric(d[ADDM_PM25], errors="coerce")
    d = d.dropna(subset=[ADDM_ASD, ADDM_PM25])

    plt.figure(figsize=(8.5, 6))
    colors = np.where(d["has_candidate_boundary"], "#A6A6A6", "#2F5D8C")
    plt.scatter(d[ADDM_PM25], d[ADDM_ASD], s=85, c=colors, alpha=0.9, edgecolors="white", linewidth=0.7)
    fit = smf.ols(f"{ADDM_ASD} ~ {ADDM_PM25}", data=d).fit()
    x = np.linspace(d[ADDM_PM25].min(), d[ADDM_PM25].max(), 100)
    plt.plot(x, fit.params["Intercept"] + fit.params[ADDM_PM25] * x, color="#B33A3A", linewidth=2.2)
    for _, row in d.iterrows():
        plt.annotate(row["site"], (row[ADDM_PM25], row[ADDM_ASD]), fontsize=8, xytext=(4, 3), textcoords="offset points")
    plt.xlabel("2019-2021 mean PM2.5 exposure (ug/m3)")
    plt.ylabel("ADDM 2020 ASD prevalence per 1,000 children aged 8")
    plt.title("PM2.5 Exposure and ASD Prevalence Across ADDM Monitoring Areas")
    plt.tight_layout()
    plt.savefig(OUT_DIR / "addm_pm25_asd_scatter_city_focus.png", dpi=300)
    plt.close()

    if sample_col:
        exact = d[~d["has_candidate_boundary"]].copy()
        plt.figure(figsize=(8.5, 6))
        plt.scatter(exact[ADDM_PM25], exact[ADDM_ASD], s=90, c="#2F5D8C", alpha=0.9, edgecolors="white", linewidth=0.7)
        fit2 = smf.ols(f"{ADDM_ASD} ~ {ADDM_PM25}", data=exact).fit()
        x2 = np.linspace(exact[ADDM_PM25].min(), exact[ADDM_PM25].max(), 100)
        plt.plot(x2, fit2.params["Intercept"] + fit2.params[ADDM_PM25] * x2, color="#B33A3A", linewidth=2.2)
        for _, row in exact.iterrows():
            plt.annotate(row["site"], (row[ADDM_PM25], row[ADDM_ASD]), fontsize=8, xytext=(4, 3), textcoords="offset points")
        plt.xlabel("2019-2021 mean PM2.5 exposure (ug/m3)")
        plt.ylabel("ADDM 2020 ASD prevalence per 1,000 children aged 8")
        plt.title("Sensitivity Sample: PM2.5 and ASD in Better-Matched ADDM Areas")
        plt.tight_layout()
        plt.savefig(OUT_DIR / "addm_pm25_asd_scatter_sensitivity.png", dpi=300)
        plt.close()


def scatter_state(df: pd.DataFrame) -> None:
    d = df[["State Name", STATE_ASD, STATE_PM25]].copy()
    d[STATE_ASD] = pd.to_numeric(d[STATE_ASD], errors="coerce")
    d[STATE_PM25] = pd.to_numeric(d[STATE_PM25], errors="coerce")
    d = d.dropna()

    plt.figure(figsize=(8.5, 6))
    plt.scatter(d[STATE_PM25], d[STATE_ASD], s=45, color="#476C9B", alpha=0.8, edgecolors="white", linewidth=0.5)
    fit = smf.ols(f"{STATE_ASD} ~ {STATE_PM25}", data=d).fit()
    x = np.linspace(d[STATE_PM25].min(), d[STATE_PM25].max(), 100)
    plt.plot(x, fit.params["Intercept"] + fit.params[STATE_PM25] * x, color="#B33A3A", linewidth=2)
    plt.xlabel("2019-2021 mean PM2.5 exposure (ug/m3)")
    plt.ylabel("NSCH 2022 current ASD prevalence (%)")
    plt.title("Supplemental State-Level Check: PM2.5 and ASD Prevalence")
    plt.tight_layout()
    plt.savefig(OUT_DIR / "state_pm25_asd_scatter_supplement.png", dpi=300)
    plt.close()


def write_chinese_summary(summary: dict) -> None:
    text = f"""# 城市/地区 PM2.5 暴露与儿童自闭症风险：结果摘要

## 研究问题

本分析将题目聚焦为：城市或监测地区层面的长期 PM2.5 暴露是否与儿童自闭症谱系障碍（ASD）患病率更高有关。

## 主分析数据

- ASD 数据：CDC ADDM Network 2020，8岁儿童 ASD 患病率。
- 暴露数据：EPA 2019-2021 年 PM2.5 县级日均监测数据，按 ADDM 监测地区对应县聚合。
- 主样本：11 个 ADDM 监测地区。
- 暴露窗口：ASD 统计年前 1-3 年，即 2019-2021 年平均 PM2.5。

## 主结果

- 在全部 11 个 ADDM 地区中，PM2.5 与 ASD 患病率呈显著正相关。
- Pearson 相关：`r = {summary['addm_all_corr']['pearson_r']:.3f}`, `p = {summary['addm_all_corr']['pearson_p']:.4f}`。
- 简单 OLS 中，PM2.5 每升高 `1 ug/m3`，ADDM ASD 患病率平均升高 `{summary['addm_all_ols']['coef_pm25']:.2f}` / 1,000 名8岁儿童；常规 OLS `p = {summary['addm_all_ols']['p_value_ols']:.4f}`，小样本 HC3 稳健标准误下 `p = {summary['addm_all_ols']['p_value_hc3']:.4f}`。

## 边界敏感性分析

- 排除 ADDM 边界较不确定的候选地区后，剩余 7 个较好匹配地区。
- Pearson 相关：`r = {summary['addm_sensitivity_corr']['pearson_r']:.3f}`, `p = {summary['addm_sensitivity_corr']['pearson_p']:.4f}`。
- OLS 中，PM2.5 每升高 `1 ug/m3`，ASD 患病率平均升高 `{summary['addm_sensitivity_ols']['coef_pm25']:.2f}` / 1,000；常规 OLS `p = {summary['addm_sensitivity_ols']['p_value_ols']:.4f}`，小样本 HC3 稳健标准误下 `p = {summary['addm_sensitivity_ols']['p_value_hc3']:.4f}`。

## 州级补充结果

- 使用 NSCH 2022 州级 ASD 患病率和 2019-2021 年州级 PM2.5，PM2.5 与 ASD 患病率呈弱到中等正相关。
- Pearson 相关：`r = {summary['state_corr']['pearson_r']:.3f}`, `p = {summary['state_corr']['pearson_p']:.4f}`。
- 加入州级收入、贫困率和本科及以上比例后，PM2.5 系数方向仍为正，但统计显著性减弱：`b = {summary['state_adjusted_ols']['coef_pm25']:.3f}`, HC3 `p = {summary['state_adjusted_ols']['p_value_hc3']:.4f}`。

## 适合 PPT 的一句话结论

在 CDC ADDM 2020 监测地区中，2019-2021 年平均 PM2.5 暴露越高，8岁儿童 ASD 患病率越高；这一关系在排除边界不确定地区后仍然明显，但由于样本量较小且为生态层面分析，应解释为探索性关联而非因果证明。

## 机制解释

- PM2.5 可诱发氧化应激和神经炎症。
- 孕期或儿童早期空气污染暴露可能影响神经发育过程。
- ASD 与早期脑发育、突触形成、免疫炎症路径有关，因此 PM2.5 与 ASD 风险具有合理的生物学解释路径。

## 局限性

- ADDM 只有 11 个监测地区，统计功效有限。
- 部分 ADDM 监测地区是“部分县”或“多个县”，县级暴露聚合存在边界误差。
- 生态分析不能推断个体层面的因果关系。
- PM2.5 暴露窗口是 2019-2021 年，不能完全代表孕期或生命早期暴露。
"""
    (OUT_DIR / "城市PM25_ASD结果摘要.md").write_text(text, encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    addm = pd.read_csv(ADDM_FILE, encoding="utf-8-sig")
    state = pd.read_csv(STATE_FILE, encoding="utf-8-sig")

    addm["has_candidate_boundary"] = addm["match_quality"].fillna("").str.contains("candidate", case=False)
    addm_sens = addm[~addm["has_candidate_boundary"]].copy()

    addm_all_corr = corr_stats(addm, ADDM_PM25, ADDM_ASD)
    addm_sens_corr = corr_stats(addm_sens, ADDM_PM25, ADDM_ASD)
    state_corr = corr_stats(state, STATE_PM25, STATE_ASD)

    ols_rows = [
        fit_simple_ols(addm, ADDM_ASD, ADDM_PM25, "addm_all_sites"),
        fit_simple_ols(addm_sens, ADDM_ASD, ADDM_PM25, "addm_exclude_candidate_boundaries"),
        fit_simple_ols(state, STATE_ASD, STATE_PM25, "state_unadjusted"),
        fit_state_adjusted(state),
    ]
    ols = pd.DataFrame(ols_rows)
    ols.to_csv(OUT_DIR / "pm25_asd_ols_results.csv", index=False, encoding="utf-8-sig")

    corr = pd.DataFrame(
        [
            {"sample": "addm_all_sites", **addm_all_corr},
            {"sample": "addm_exclude_candidate_boundaries", **addm_sens_corr},
            {"sample": "state_supplement", **state_corr},
        ]
    )
    corr.to_csv(OUT_DIR / "pm25_asd_correlations.csv", index=False, encoding="utf-8-sig")

    addm.to_csv(OUT_DIR / "addm_pm25_asd_city_analysis_dataset.csv", index=False, encoding="utf-8-sig")
    addm_sens.to_csv(OUT_DIR / "addm_pm25_asd_sensitivity_dataset.csv", index=False, encoding="utf-8-sig")

    scatter_addm(addm, sample_col="has_candidate_boundary")
    scatter_state(state)

    summary = {
        "addm_all_corr": addm_all_corr,
        "addm_sensitivity_corr": addm_sens_corr,
        "state_corr": state_corr,
        "addm_all_ols": ols_rows[0],
        "addm_sensitivity_ols": ols_rows[1],
        "state_unadjusted_ols": ols_rows[2],
        "state_adjusted_ols": ols_rows[3],
    }
    (OUT_DIR / "pm25_asd_key_results.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_chinese_summary(summary)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
