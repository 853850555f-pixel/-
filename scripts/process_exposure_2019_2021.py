import pandas as pd


LEAD_FILES = ["lead 2019.xlsx", "lead 2020.xlsx", "lead 2021.xlsx"]
PM25_FILES = ["daily_88101_2019.csv", "daily_88101_2020.csv", "daily_88101_2021.csv"]

ASD_2022_RATES = [
    ("01", "Alabama", 3.1),
    ("02", "Alaska", 4.4),
    ("04", "Arizona", 5.3),
    ("05", "Arkansas", 3.2),
    ("06", "California", 3.2),
    ("08", "Colorado", 2.7),
    ("09", "Connecticut", 2.9),
    ("10", "Delaware", 4.9),
    ("11", "District of Columbia", 3.0),
    ("12", "Florida", 5.6),
    ("13", "Georgia", 3.1),
    ("15", "Hawaii", 1.9),
    ("16", "Idaho", 2.3),
    ("17", "Illinois", 2.6),
    ("18", "Indiana", 3.7),
    ("19", "Iowa", 3.3),
    ("20", "Kansas", 3.0),
    ("21", "Kentucky", 4.0),
    ("22", "Louisiana", 4.4),
    ("23", "Maine", 3.7),
    ("24", "Maryland", 2.2),
    ("25", "Massachusetts", 4.7),
    ("26", "Michigan", 5.3),
    ("27", "Minnesota", 4.3),
    ("28", "Mississippi", 3.8),
    ("29", "Missouri", 3.0),
    ("30", "Montana", 3.5),
    ("31", "Nebraska", 1.8),
    ("32", "Nevada", 3.3),
    ("33", "New Hampshire", 2.3),
    ("34", "New Jersey", 3.3),
    ("35", "New Mexico", 3.7),
    ("36", "New York", 3.8),
    ("37", "North Carolina", 1.2),
    ("38", "North Dakota", 2.9),
    ("39", "Ohio", 2.7),
    ("40", "Oklahoma", 4.2),
    ("41", "Oregon", 3.3),
    ("42", "Pennsylvania", 4.7),
    ("44", "Rhode Island", 1.8),
    ("45", "South Carolina", 3.1),
    ("46", "South Dakota", 2.1),
    ("47", "Tennessee", 3.8),
    ("48", "Texas", 3.9),
    ("49", "Utah", 3.3),
    ("50", "Vermont", 2.3),
    ("51", "Virginia", 4.3),
    ("53", "Washington", 5.7),
    ("54", "West Virginia", 3.2),
    ("55", "Wisconsin", 1.1),
    ("56", "Wyoming", 2.0),
]


def make_fips(series, width):
    return pd.to_numeric(series, errors="coerce").astype("Int64").astype(str).str.zfill(width)


def read_lead():
    frames = []
    for file_name in LEAD_FILES:
        df = pd.read_excel(file_name)
        df.columns = df.columns.str.strip()
        df["source_file"] = file_name
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def process_lead():
    df = read_lead()
    lead = df[df["Parameter Name"].eq("Lead PM2.5 LC")].copy()
    lead["Date Local"] = pd.to_datetime(lead["Date Local"], errors="coerce", format="mixed")
    lead["Pb_PM25_ugm3"] = pd.to_numeric(lead["Arithmetic Mean"], errors="coerce")
    lead["Pb_PM25_ugm3_clean"] = lead["Pb_PM25_ugm3"].clip(lower=0)
    lead["Pb_PM25_ngm3_clean"] = lead["Pb_PM25_ugm3_clean"] * 1000

    lead["state_fips"] = make_fips(lead["State Code"], 2)
    lead["county_fips"] = make_fips(lead["County Code"], 3)
    lead["fips"] = lead["state_fips"] + lead["county_fips"]
    lead["year"] = lead["Date Local"].dt.year
    lead["month"] = lead["Date Local"].dt.month
    lead["year_month"] = lead["Date Local"].dt.to_period("M").astype(str)

    keep_cols = [
        "source_file",
        "fips",
        "state_fips",
        "county_fips",
        "State Code",
        "County Code",
        "State Name",
        "County Name",
        "City Name",
        "CBSA Name",
        "Site Num",
        "POC",
        "Latitude",
        "Longitude",
        "Date Local",
        "year",
        "month",
        "year_month",
        "Parameter Name",
        "Sample Duration",
        "Units of Measure",
        "Observation Count",
        "Observation Percent",
        "Pb_PM25_ugm3",
        "Pb_PM25_ugm3_clean",
        "Pb_PM25_ngm3_clean",
        "Method Code",
        "Method Name",
        "Local Site Name",
        "Address",
    ]
    df_clean = lead[[col for col in keep_cols if col in lead.columns]].copy()

    site_day = df_clean.groupby(
        [
            "fips",
            "state_fips",
            "county_fips",
            "State Name",
            "County Name",
            "City Name",
            "CBSA Name",
            "Site Num",
            "Latitude",
            "Longitude",
            "Date Local",
        ],
        dropna=False,
        as_index=False,
    )["Pb_PM25_ugm3_clean"].mean()
    site_day = site_day.rename(columns={"Pb_PM25_ugm3_clean": "Pb_PM25_site_day_ugm3"})
    site_day["Pb_PM25_site_day_ngm3"] = site_day["Pb_PM25_site_day_ugm3"] * 1000
    site_day["year"] = site_day["Date Local"].dt.year
    site_day["month"] = site_day["Date Local"].dt.month
    site_day["year_month"] = site_day["Date Local"].dt.to_period("M").astype(str)

    county_month = site_day.groupby(
        ["fips", "state_fips", "State Name", "County Name", "year_month"],
        dropna=False,
        as_index=False,
    )["Pb_PM25_site_day_ugm3"].mean()
    county_month = county_month.rename(columns={"Pb_PM25_site_day_ugm3": "Pb_PM25_county_month_ugm3"})
    county_month["Pb_PM25_county_month_ngm3"] = county_month["Pb_PM25_county_month_ugm3"] * 1000

    county_year = site_day.groupby(
        ["fips", "state_fips", "State Name", "County Name", "year"],
        dropna=False,
        as_index=False,
    )["Pb_PM25_site_day_ugm3"].mean()
    county_year = county_year.rename(columns={"Pb_PM25_site_day_ugm3": "Pb_PM25_county_year_ugm3"})
    county_year["Pb_PM25_county_year_ngm3"] = county_year["Pb_PM25_county_year_ugm3"] * 1000

    state_year = site_day.groupby(
        ["state_fips", "State Name", "year"],
        dropna=False,
        as_index=False,
    )["Pb_PM25_site_day_ugm3"].mean()
    state_year = state_year.rename(columns={"Pb_PM25_site_day_ugm3": "Pb_PM25_state_year_ugm3"})
    state_year["Pb_PM25_state_year_ngm3"] = state_year["Pb_PM25_state_year_ugm3"] * 1000

    state_window = state_year.groupby(
        ["state_fips", "State Name"],
        dropna=False,
        as_index=False,
    ).agg(
        Pb_PM25_2019_2021_mean_ugm3=("Pb_PM25_state_year_ugm3", "mean"),
        Pb_PM25_2019_2021_mean_ngm3=("Pb_PM25_state_year_ngm3", "mean"),
        Pb_PM25_years_available=("year", "nunique"),
    )

    return df, lead, df_clean, site_day, county_month, county_year, state_year, state_window


def read_pm25():
    frames = []
    for file_name in PM25_FILES:
        df = pd.read_csv(file_name, dtype={"State Code": str, "County Code": str}, low_memory=False)
        df.columns = df.columns.str.strip()
        df["source_file"] = file_name
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def process_pm25():
    pm25 = read_pm25()
    pm25 = pm25[pm25["Parameter Name"].eq("PM2.5 - Local Conditions")].copy()
    pm25["Date Local"] = pd.to_datetime(pm25["Date Local"], errors="coerce", format="mixed")
    pm25["PM25_ugm3"] = pd.to_numeric(pm25["Arithmetic Mean"], errors="coerce").clip(lower=0)
    pm25["state_fips"] = make_fips(pm25["State Code"], 2)
    pm25["county_fips"] = make_fips(pm25["County Code"], 3)
    pm25["fips"] = pm25["state_fips"] + pm25["county_fips"]

    site_day = pm25.groupby(
        ["state_fips", "State Name", "Site Num", "Latitude", "Longitude", "Date Local"],
        dropna=False,
        as_index=False,
    )["PM25_ugm3"].mean()
    site_day["year"] = site_day["Date Local"].dt.year

    state_year = site_day.groupby(
        ["state_fips", "State Name", "year"],
        dropna=False,
        as_index=False,
    )["PM25_ugm3"].mean()
    state_year = state_year.rename(columns={"PM25_ugm3": "PM25_state_year_ugm3"})

    state_window = state_year.groupby(
        ["state_fips", "State Name"],
        dropna=False,
        as_index=False,
    ).agg(
        PM25_2019_2021_mean_ugm3=("PM25_state_year_ugm3", "mean"),
        PM25_years_available=("year", "nunique"),
    )

    return pm25, site_day, state_year, state_window


def process_asd():
    asd = pd.DataFrame(ASD_2022_RATES, columns=["state_fips", "State Name", "ASD_2022_current_pct"])
    asd["ASD_2022_current_rate"] = asd["ASD_2022_current_pct"] / 100
    asd["ASD_year"] = 2022
    asd["ASD_source"] = "2022 NSCH, Indicator 2.8, age 3-17 years"
    return asd


def main():
    lead_raw, lead, lead_clean, lead_site_day, lead_county_month, lead_county_year, lead_state_year, lead_state_window = process_lead()
    pm25, pm25_site_day, pm25_state_year, pm25_state_window = process_pm25()
    asd = process_asd()

    exposure_year = lead_state_year.merge(
        pm25_state_year,
        on=["state_fips", "year"],
        how="outer",
        suffixes=("", "_pm25"),
    )
    exposure_year["State Name"] = exposure_year["State Name"].fillna(exposure_year["State Name_pm25"])
    exposure_year = exposure_year.drop(columns=["State Name_pm25"])

    exposure_window = lead_state_window.merge(
        pm25_state_window,
        on="state_fips",
        how="outer",
        suffixes=("", "_pm25"),
    )
    exposure_window["State Name"] = exposure_window["State Name"].fillna(exposure_window["State Name_pm25"])
    exposure_window = exposure_window.drop(columns=["State Name_pm25"])

    analysis = asd.merge(
        lead_state_window.drop(columns=["State Name"]),
        on="state_fips",
        how="left",
    ).merge(
        pm25_state_window.drop(columns=["State Name"]),
        on="state_fips",
        how="left",
    )

    lead_clean.to_csv("lead_pm25_2019_2021_clean.csv", index=False, encoding="utf-8-sig")
    lead_site_day.to_csv("lead_pm25_2019_2021_site_day.csv", index=False, encoding="utf-8-sig")
    lead_county_month.to_csv("lead_pm25_2019_2021_county_month.csv", index=False, encoding="utf-8-sig")
    lead_county_year.to_csv("lead_pm25_2019_2021_county_year.csv", index=False, encoding="utf-8-sig")
    lead_state_year.to_csv("lead_pm25_2019_2021_state_year.csv", index=False, encoding="utf-8-sig")
    lead_state_window.to_csv("lead_pm25_2019_2021_state_mean.csv", index=False, encoding="utf-8-sig")
    pm25_state_year.to_csv("pm25_2019_2021_state_year.csv", index=False, encoding="utf-8-sig")
    pm25_state_window.to_csv("pm25_2019_2021_state_mean.csv", index=False, encoding="utf-8-sig")
    exposure_year.to_csv("state_exposure_2019_2021_yearly_lead_pm25.csv", index=False, encoding="utf-8-sig")
    exposure_window.to_csv("state_exposure_2019_2021_mean_lead_pm25.csv", index=False, encoding="utf-8-sig")
    asd.to_csv("asd_state_2022_nsch.csv", index=False, encoding="utf-8-sig")
    analysis.to_csv("analysis_state_asd_2022_exposure_2019_2021.csv", index=False, encoding="utf-8-sig")

    summary = pd.DataFrame(
        [
            ["lead_raw_rows", len(lead_raw)],
            ["lead_rows", len(lead)],
            ["lead_site_day_rows", len(lead_site_day)],
            ["lead_county_month_rows", len(lead_county_month)],
            ["lead_county_year_rows", len(lead_county_year)],
            ["lead_state_year_rows", len(lead_state_year)],
            ["lead_states", lead["State Name"].nunique()],
            ["lead_negative_original_values", int((lead["Pb_PM25_ugm3"] < 0).sum())],
            ["lead_missing_original_values", int(lead["Pb_PM25_ugm3"].isna().sum())],
            ["lead_date_min", lead["Date Local"].min()],
            ["lead_date_max", lead["Date Local"].max()],
            ["pm25_rows", len(pm25)],
            ["pm25_state_year_rows", len(pm25_state_year)],
            ["pm25_states", pm25["State Name"].nunique()],
            ["pm25_date_min", pm25["Date Local"].min()],
            ["pm25_date_max", pm25["Date Local"].max()],
            ["asd_states", len(asd)],
            ["analysis_rows", len(analysis)],
            ["analysis_missing_lead", int(analysis["Pb_PM25_2019_2021_mean_ugm3"].isna().sum())],
            ["analysis_missing_pm25", int(analysis["PM25_2019_2021_mean_ugm3"].isna().sum())],
        ],
        columns=["metric", "value"],
    )
    summary.to_csv("state_asd_exposure_2019_2021_summary.csv", index=False, encoding="utf-8-sig")

    print(summary.to_string(index=False))
    print("\nanalysis preview:")
    print(analysis.head().to_string(index=False))


if __name__ == "__main__":
    main()
