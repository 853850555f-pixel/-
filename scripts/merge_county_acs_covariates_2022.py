import json
import urllib.parse
import urllib.request

import pandas as pd


COUNTY_EXPOSURE_FILE = "county_exposure_2019_2021_mean_lead_pm25.csv"
ACS_COUNTY_FILE = "acs_2022_county_covariates.csv"
OUTPUT_FILE = "county_exposure_2019_2021_mean_lead_pm25_with_acs.csv"

ACS_URL = "https://api.census.gov/data/2022/acs/acs5/profile"
ACS_VARIABLES = {
    "NAME": "acs_county_name",
    "DP03_0062E": "median_household_income",
    "DP03_0128PE": "poverty_rate_pct",
    "DP02_0068PE": "bachelor_or_higher_pct",
    "DP05_0001E": "total_population",
}


def download_county_acs():
    params = {
        "get": ",".join(ACS_VARIABLES.keys()),
        "for": "county:*",
        "in": "state:*",
    }
    url = f"{ACS_URL}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url, timeout=120) as response:
        data = json.loads(response.read().decode("utf-8"))
    header, rows = data[0], data[1:]
    df = pd.DataFrame(rows, columns=header)
    df = df.rename(columns=ACS_VARIABLES)
    df = df.rename(columns={"state": "state_fips", "county": "county_fips"})
    df["state_fips"] = df["state_fips"].astype(str).str.zfill(2)
    df["county_fips"] = df["county_fips"].astype(str).str.zfill(3)
    df["fips"] = df["state_fips"] + df["county_fips"]

    for col in ["median_household_income", "poverty_rate_pct", "bachelor_or_higher_pct", "total_population"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["acs_year"] = 2022
    df["acs_source"] = "ACS 2022 5-year Data Profile"
    return df[
        [
            "fips",
            "state_fips",
            "county_fips",
            "acs_county_name",
            "median_household_income",
            "poverty_rate_pct",
            "bachelor_or_higher_pct",
            "total_population",
            "acs_year",
            "acs_source",
        ]
    ]


def main():
    exposure = pd.read_csv(COUNTY_EXPOSURE_FILE, dtype={"fips": str, "state_fips": str, "county_fips": str})
    exposure["fips"] = exposure["fips"].str.zfill(5)

    acs = download_county_acs()
    acs.to_csv(ACS_COUNTY_FILE, index=False, encoding="utf-8-sig")

    merged = exposure.merge(
        acs.drop(columns=["state_fips", "county_fips"]),
        on="fips",
        how="left",
    )
    merged.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    summary = pd.DataFrame(
        [
            ["exposure_counties", len(exposure)],
            ["acs_counties", len(acs)],
            ["merged_counties", len(merged)],
            ["missing_income", int(merged["median_household_income"].isna().sum())],
            ["missing_poverty", int(merged["poverty_rate_pct"].isna().sum())],
            ["missing_education", int(merged["bachelor_or_higher_pct"].isna().sum())],
        ],
        columns=["metric", "value"],
    )
    summary.to_csv("county_acs_2022_merge_summary.csv", index=False, encoding="utf-8-sig")

    print(summary.to_string(index=False))
    print("\ncounty ACS merged preview:")
    print(merged.head().to_string(index=False))


if __name__ == "__main__":
    main()
