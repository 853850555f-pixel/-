import pandas as pd


LEAD_COUNTY_YEAR_FILE = "lead_pm25_2019_2021_county_year.csv"
PM25_FILES = ["daily_88101_2019.csv", "daily_88101_2020.csv", "daily_88101_2021.csv"]


def make_fips(series, width):
    return pd.to_numeric(series, errors="coerce").astype("Int64").astype(str).str.zfill(width)


def read_pm25():
    frames = []
    for file_name in PM25_FILES:
        df = pd.read_csv(file_name, dtype={"State Code": str, "County Code": str}, low_memory=False)
        df.columns = df.columns.str.strip()
        df["source_file"] = file_name
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def process_pm25_county():
    pm25 = read_pm25()
    pm25 = pm25[pm25["Parameter Name"].eq("PM2.5 - Local Conditions")].copy()
    pm25["Date Local"] = pd.to_datetime(pm25["Date Local"], errors="coerce", format="mixed")
    pm25["PM25_ugm3"] = pd.to_numeric(pm25["Arithmetic Mean"], errors="coerce").clip(lower=0)
    pm25["state_fips"] = make_fips(pm25["State Code"], 2)
    pm25["county_fips"] = make_fips(pm25["County Code"], 3)
    pm25["fips"] = pm25["state_fips"] + pm25["county_fips"]

    site_day = pm25.groupby(
        [
            "fips",
            "state_fips",
            "county_fips",
            "State Name",
            "County Name",
            "Site Num",
            "Latitude",
            "Longitude",
            "Date Local",
        ],
        dropna=False,
        as_index=False,
    )["PM25_ugm3"].mean()
    site_day["year"] = site_day["Date Local"].dt.year

    county_year = site_day.groupby(
        ["fips", "state_fips", "county_fips", "State Name", "County Name", "year"],
        dropna=False,
        as_index=False,
    )["PM25_ugm3"].mean()
    county_year = county_year.rename(columns={"PM25_ugm3": "PM25_county_year_ugm3"})

    county_mean = county_year.groupby(
        ["fips", "state_fips", "county_fips", "State Name", "County Name"],
        dropna=False,
        as_index=False,
    ).agg(
        PM25_2019_2021_mean_ugm3=("PM25_county_year_ugm3", "mean"),
        PM25_years_available=("year", "nunique"),
    )
    return pm25, county_year, county_mean


def process_lead_county():
    lead_year = pd.read_csv(LEAD_COUNTY_YEAR_FILE, dtype={"fips": str, "state_fips": str})
    lead_year["fips"] = lead_year["fips"].str.zfill(5)
    lead_year["state_fips"] = lead_year["state_fips"].str.zfill(2)
    lead_year["county_fips"] = lead_year["fips"].str[-3:]

    lead_mean = lead_year.groupby(
        ["fips", "state_fips", "county_fips", "State Name", "County Name"],
        dropna=False,
        as_index=False,
    ).agg(
        Pb_PM25_2019_2021_mean_ugm3=("Pb_PM25_county_year_ugm3", "mean"),
        Pb_PM25_2019_2021_mean_ngm3=("Pb_PM25_county_year_ngm3", "mean"),
        Pb_PM25_years_available=("year", "nunique"),
    )
    return lead_year, lead_mean


def merge_outer(left, right, on):
    merged = left.merge(right, on=on, how="outer", suffixes=("", "_pm25"))
    for col in ["State Name", "County Name", "state_fips", "county_fips"]:
        other = f"{col}_pm25"
        if other in merged.columns:
            merged[col] = merged[col].fillna(merged[other])
            merged = merged.drop(columns=[other])
    return merged


def main():
    lead_year, lead_mean = process_lead_county()
    pm25_raw, pm25_county_year, pm25_county_mean = process_pm25_county()

    yearly = merge_outer(lead_year, pm25_county_year, ["fips", "year"])
    mean = merge_outer(lead_mean, pm25_county_mean, ["fips"])

    asd_template = mean[["fips", "state_fips", "county_fips", "State Name", "County Name"]].copy()
    asd_template["ASD_year"] = 2022
    asd_template["ASD_rate"] = ""
    asd_template["ASD_cases"] = ""
    asd_template["child_population"] = ""
    asd_template["ASD_source"] = ""
    asd_template["notes"] = ""

    pm25_county_year.to_csv("pm25_2019_2021_county_year.csv", index=False, encoding="utf-8-sig")
    pm25_county_mean.to_csv("pm25_2019_2021_county_mean.csv", index=False, encoding="utf-8-sig")
    yearly.to_csv("county_exposure_2019_2021_yearly_lead_pm25.csv", index=False, encoding="utf-8-sig")
    mean.to_csv("county_exposure_2019_2021_mean_lead_pm25.csv", index=False, encoding="utf-8-sig")
    asd_template.to_csv("county_asd_2022_template.csv", index=False, encoding="utf-8-sig")

    summary = pd.DataFrame(
        [
            ["lead_county_year_rows", len(lead_year)],
            ["lead_counties", lead_mean["fips"].nunique()],
            ["pm25_raw_rows", len(pm25_raw)],
            ["pm25_county_year_rows", len(pm25_county_year)],
            ["pm25_counties", pm25_county_mean["fips"].nunique()],
            ["merged_counties", mean["fips"].nunique()],
            ["counties_with_lead", int(mean["Pb_PM25_2019_2021_mean_ngm3"].notna().sum())],
            ["counties_with_pm25", int(mean["PM25_2019_2021_mean_ugm3"].notna().sum())],
            ["counties_with_both", int(mean[["Pb_PM25_2019_2021_mean_ngm3", "PM25_2019_2021_mean_ugm3"]].notna().all(axis=1).sum())],
            ["pm25_date_min", pm25_raw["Date Local"].min()],
            ["pm25_date_max", pm25_raw["Date Local"].max()],
        ],
        columns=["metric", "value"],
    )
    summary.to_csv("county_exposure_2019_2021_summary.csv", index=False, encoding="utf-8-sig")

    print(summary.to_string(index=False))
    print("\ncounty exposure preview:")
    print(mean.head().to_string(index=False))


if __name__ == "__main__":
    main()
