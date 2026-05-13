import json
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd


BASE_ANALYSIS_FILE = "analysis_state_asd_2022_exposure_2019_2021.csv"
ACS_OUTPUT_FILE = "acs_2022_state_covariates.csv"
MERGED_OUTPUT_FILE = "analysis_state_asd_2022_exposure_2019_2021_with_covariates.csv"
TEMPLATE_FILE = "acs_2022_state_covariates_template.csv"

ACS_URL = "https://api.census.gov/data/2022/acs/acs5/profile"
ACS_VARIABLES = {
    "NAME": "acs_state_name",
    "DP03_0062E": "median_household_income",
    "DP03_0128PE": "poverty_rate_pct",
    "DP02_0068PE": "bachelor_or_higher_pct",
    "DP05_0001E": "total_population",
}
ACS_KEEP_COLUMNS = ["state_fips", *ACS_VARIABLES.values(), "acs_year", "acs_source"]


def download_acs():
    params = {
        "get": ",".join(ACS_VARIABLES.keys()),
        "for": "state:*",
    }
    url = f"{ACS_URL}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url, timeout=60) as response:
        data = json.loads(response.read().decode("utf-8"))
    header, rows = data[0], data[1:]
    df = pd.DataFrame(rows, columns=header)
    df = df.rename(columns=ACS_VARIABLES)
    df = df.rename(columns={"state": "state_fips"})
    df["state_fips"] = df["state_fips"].astype(str).str.zfill(2)

    numeric_cols = [col for col in df.columns if col not in ["state_fips", "acs_state_name"]]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["acs_year"] = 2022
    df["acs_source"] = "ACS 2022 5-year Data Profile"
    return df


def write_template(base):
    template = base[["state_fips", "State Name"]].copy()
    template["median_household_income"] = ""
    template["poverty_rate_pct"] = ""
    template["bachelor_or_higher_pct"] = ""
    template["total_population"] = ""
    template["acs_year"] = 2022
    template["acs_source"] = "ACS 2022 5-year Data Profile"
    template.to_csv(TEMPLATE_FILE, index=False, encoding="utf-8-sig")


def load_or_download_acs(base):
    acs_path = Path(ACS_OUTPUT_FILE)
    if acs_path.exists():
        acs = pd.read_csv(acs_path, dtype={"state_fips": str})
        acs["state_fips"] = acs["state_fips"].str.zfill(2)
        if "acs_year" not in acs.columns:
            acs["acs_year"] = 2022
        if "acs_source" not in acs.columns:
            acs["acs_source"] = "ACS 2022 5-year Data Profile"
        missing_cols = [col for col in ACS_KEEP_COLUMNS if col not in acs.columns]
        if missing_cols:
            raise ValueError(f"Existing {ACS_OUTPUT_FILE} is missing columns: {missing_cols}")
        acs = acs[ACS_KEEP_COLUMNS].copy()
        acs.to_csv(ACS_OUTPUT_FILE, index=False, encoding="utf-8-sig")
        return acs, "existing_file"

    try:
        acs = download_acs()
        acs.to_csv(ACS_OUTPUT_FILE, index=False, encoding="utf-8-sig")
        return acs, "downloaded"
    except Exception as exc:
        write_template(base)
        raise RuntimeError(
            "Could not download ACS data from the Census API. "
            f"A fillable template was written to {TEMPLATE_FILE}. "
            f"Original error: {exc}"
        ) from exc


def main():
    base = pd.read_csv(BASE_ANALYSIS_FILE, dtype={"state_fips": str})
    base["state_fips"] = base["state_fips"].str.zfill(2)

    acs, source = load_or_download_acs(base)
    merged = base.merge(acs.drop(columns=["acs_state_name"], errors="ignore"), on="state_fips", how="left")
    merged.to_csv(MERGED_OUTPUT_FILE, index=False, encoding="utf-8-sig")

    summary = pd.DataFrame(
        [
            ["acs_source_mode", source],
            ["base_rows", len(base)],
            ["acs_rows", len(acs)],
            ["merged_rows", len(merged)],
            ["missing_income", int(merged["median_household_income"].isna().sum())],
            ["missing_poverty", int(merged["poverty_rate_pct"].isna().sum())],
            ["missing_education", int(merged["bachelor_or_higher_pct"].isna().sum())],
        ],
        columns=["metric", "value"],
    )
    summary.to_csv("acs_2022_merge_summary.csv", index=False, encoding="utf-8-sig")

    print(summary.to_string(index=False))
    print(f"\nWrote {MERGED_OUTPUT_FILE}")


if __name__ == "__main__":
    main()
