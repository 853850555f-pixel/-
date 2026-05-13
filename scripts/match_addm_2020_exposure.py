import re

import pandas as pd


ADDM_REPORT_URL = "https://www.cdc.gov/mmwr/volumes/72/ss/ss7202a1.htm"
COUNTY_EXPOSURE_FILE = "county_exposure_2019_2021_mean_lead_pm25_with_acs.csv"


# Public ADDM tables identify several sites only as "part of" counties or as a
# county count without listing every county. Keep match_quality explicit so the
# exposure aggregation is not mistaken for exact surveillance boundaries.
ADDM_COUNTY_CROSSWALK = [
    {
        "site": "Arizona",
        "fips": "04013",
        "county_label": "Maricopa County, AZ",
        "match_quality": "county_approximate_subcounty",
        "boundary_note": "ADDM: part of one county in metropolitan Phoenix; approximated with Maricopa County.",
    },
    {
        "site": "Arkansas",
        "fips": "05001",
        "county_label": "Arkansas County, AR",
        "match_quality": "candidate_needs_verification",
        "boundary_note": "Candidate county for ADDM central Arkansas site; verify against ADDM site documentation before formal inference.",
    },
    {
        "site": "Arkansas",
        "fips": "05023",
        "county_label": "Cleburne County, AR",
        "match_quality": "candidate_needs_verification",
        "boundary_note": "Candidate county for ADDM central Arkansas site; verify against ADDM site documentation before formal inference.",
    },
    {
        "site": "Arkansas",
        "fips": "05025",
        "county_label": "Cleveland County, AR",
        "match_quality": "candidate_needs_verification",
        "boundary_note": "Candidate county for ADDM central Arkansas site; verify against ADDM site documentation before formal inference.",
    },
    {
        "site": "Arkansas",
        "fips": "05029",
        "county_label": "Conway County, AR",
        "match_quality": "candidate_needs_verification",
        "boundary_note": "Candidate county for ADDM central Arkansas site; verify against ADDM site documentation before formal inference.",
    },
    {
        "site": "Arkansas",
        "fips": "05045",
        "county_label": "Faulkner County, AR",
        "match_quality": "candidate_needs_verification",
        "boundary_note": "Candidate county for ADDM central Arkansas site; verify against ADDM site documentation before formal inference.",
    },
    {
        "site": "Arkansas",
        "fips": "05053",
        "county_label": "Grant County, AR",
        "match_quality": "candidate_needs_verification",
        "boundary_note": "Candidate county for ADDM central Arkansas site; verify against ADDM site documentation before formal inference.",
    },
    {
        "site": "Arkansas",
        "fips": "05059",
        "county_label": "Hot Spring County, AR",
        "match_quality": "candidate_needs_verification",
        "boundary_note": "Candidate county for ADDM central Arkansas site; verify against ADDM site documentation before formal inference.",
    },
    {
        "site": "Arkansas",
        "fips": "05063",
        "county_label": "Independence County, AR",
        "match_quality": "candidate_needs_verification",
        "boundary_note": "Candidate county for ADDM central Arkansas site; verify against ADDM site documentation before formal inference.",
    },
    {
        "site": "Arkansas",
        "fips": "05067",
        "county_label": "Jackson County, AR",
        "match_quality": "candidate_needs_verification",
        "boundary_note": "Candidate county for ADDM central Arkansas site; verify against ADDM site documentation before formal inference.",
    },
    {
        "site": "Arkansas",
        "fips": "05069",
        "county_label": "Jefferson County, AR",
        "match_quality": "candidate_needs_verification",
        "boundary_note": "Candidate county for ADDM central Arkansas site; verify against ADDM site documentation before formal inference.",
    },
    {
        "site": "Arkansas",
        "fips": "05079",
        "county_label": "Lincoln County, AR",
        "match_quality": "candidate_needs_verification",
        "boundary_note": "Candidate county for ADDM central Arkansas site; verify against ADDM site documentation before formal inference.",
    },
    {
        "site": "Arkansas",
        "fips": "05085",
        "county_label": "Lonoke County, AR",
        "match_quality": "candidate_needs_verification",
        "boundary_note": "Candidate county for ADDM central Arkansas site; verify against ADDM site documentation before formal inference.",
    },
    {
        "site": "Arkansas",
        "fips": "05095",
        "county_label": "Monroe County, AR",
        "match_quality": "candidate_needs_verification",
        "boundary_note": "Candidate county for ADDM central Arkansas site; verify against ADDM site documentation before formal inference.",
    },
    {
        "site": "Arkansas",
        "fips": "05097",
        "county_label": "Montgomery County, AR",
        "match_quality": "candidate_needs_verification",
        "boundary_note": "Candidate county for ADDM central Arkansas site; verify against ADDM site documentation before formal inference.",
    },
    {
        "site": "Arkansas",
        "fips": "05105",
        "county_label": "Perry County, AR",
        "match_quality": "candidate_needs_verification",
        "boundary_note": "Candidate county for ADDM central Arkansas site; verify against ADDM site documentation before formal inference.",
    },
    {
        "site": "Arkansas",
        "fips": "05117",
        "county_label": "Prairie County, AR",
        "match_quality": "candidate_needs_verification",
        "boundary_note": "Candidate county for ADDM central Arkansas site; verify against ADDM site documentation before formal inference.",
    },
    {
        "site": "Arkansas",
        "fips": "05119",
        "county_label": "Pulaski County, AR",
        "match_quality": "candidate_needs_verification",
        "boundary_note": "Candidate county for ADDM central Arkansas site; verify against ADDM site documentation before formal inference.",
    },
    {
        "site": "Arkansas",
        "fips": "05125",
        "county_label": "Saline County, AR",
        "match_quality": "candidate_needs_verification",
        "boundary_note": "Candidate county for ADDM central Arkansas site; verify against ADDM site documentation before formal inference.",
    },
    {
        "site": "Arkansas",
        "fips": "05127",
        "county_label": "Scott County, AR",
        "match_quality": "candidate_needs_verification",
        "boundary_note": "Candidate county for ADDM central Arkansas site; verify against ADDM site documentation before formal inference.",
    },
    {
        "site": "Arkansas",
        "fips": "05145",
        "county_label": "White County, AR",
        "match_quality": "candidate_needs_verification",
        "boundary_note": "Candidate county for ADDM central Arkansas site; verify against ADDM site documentation before formal inference.",
    },
    {
        "site": "Arkansas",
        "fips": "05147",
        "county_label": "Woodruff County, AR",
        "match_quality": "candidate_needs_verification",
        "boundary_note": "Candidate county for ADDM central Arkansas site; verify against ADDM site documentation before formal inference.",
    },
    {
        "site": "California",
        "fips": "06073",
        "county_label": "San Diego County, CA",
        "match_quality": "county_approximate_subcounty",
        "boundary_note": "ADDM: part of one county in metropolitan San Diego; approximated with San Diego County.",
    },
    {
        "site": "Georgia",
        "fips": "13089",
        "county_label": "DeKalb County, GA",
        "match_quality": "county_approximate_needs_verification",
        "boundary_note": "ADDM: two counties in metropolitan Atlanta; county list should be verified from site documentation.",
    },
    {
        "site": "Georgia",
        "fips": "13121",
        "county_label": "Fulton County, GA",
        "match_quality": "county_approximate_needs_verification",
        "boundary_note": "ADDM: two counties in metropolitan Atlanta; county list should be verified from site documentation.",
    },
    {
        "site": "Maryland",
        "fips": "24003",
        "county_label": "Anne Arundel County, MD",
        "match_quality": "county_approximate_needs_verification",
        "boundary_note": "ADDM: five counties in suburban Baltimore; county list should be verified from site documentation.",
    },
    {
        "site": "Maryland",
        "fips": "24005",
        "county_label": "Baltimore County, MD",
        "match_quality": "county_approximate_needs_verification",
        "boundary_note": "ADDM: five counties in suburban Baltimore; county list should be verified from site documentation.",
    },
    {
        "site": "Maryland",
        "fips": "24013",
        "county_label": "Carroll County, MD",
        "match_quality": "county_approximate_needs_verification",
        "boundary_note": "ADDM: five counties in suburban Baltimore; county list should be verified from site documentation.",
    },
    {
        "site": "Maryland",
        "fips": "24025",
        "county_label": "Harford County, MD",
        "match_quality": "county_approximate_needs_verification",
        "boundary_note": "ADDM: five counties in suburban Baltimore; county list should be verified from site documentation.",
    },
    {
        "site": "Maryland",
        "fips": "24027",
        "county_label": "Howard County, MD",
        "match_quality": "county_approximate_needs_verification",
        "boundary_note": "ADDM: five counties in suburban Baltimore; county list should be verified from site documentation.",
    },
    {
        "site": "Minnesota",
        "fips": "27003",
        "county_label": "Anoka County, MN",
        "match_quality": "candidate_subcounty_needs_verification",
        "boundary_note": "Candidate county for ADDM Twin Cities site; ADDM reports parts of three counties, so subcounty boundaries are required.",
    },
    {
        "site": "Minnesota",
        "fips": "27053",
        "county_label": "Hennepin County, MN",
        "match_quality": "candidate_subcounty_needs_verification",
        "boundary_note": "Candidate county for ADDM Twin Cities site; ADDM reports parts of three counties, so subcounty boundaries are required.",
    },
    {
        "site": "Minnesota",
        "fips": "27123",
        "county_label": "Ramsey County, MN",
        "match_quality": "candidate_subcounty_needs_verification",
        "boundary_note": "Candidate county for ADDM Twin Cities site; ADDM reports parts of three counties, so subcounty boundaries are required.",
    },
    {
        "site": "Missouri",
        "fips": "29071",
        "county_label": "Franklin County, MO",
        "match_quality": "county_approximate_needs_verification",
        "boundary_note": "ADDM: five counties in metropolitan St. Louis; county list should be verified from site documentation.",
    },
    {
        "site": "Missouri",
        "fips": "29099",
        "county_label": "Jefferson County, MO",
        "match_quality": "county_approximate_needs_verification",
        "boundary_note": "ADDM: five counties in metropolitan St. Louis; county list should be verified from site documentation.",
    },
    {
        "site": "Missouri",
        "fips": "29183",
        "county_label": "St. Charles County, MO",
        "match_quality": "county_approximate_needs_verification",
        "boundary_note": "ADDM: five counties in metropolitan St. Louis; county list should be verified from site documentation.",
    },
    {
        "site": "Missouri",
        "fips": "29189",
        "county_label": "St. Louis County, MO",
        "match_quality": "county_approximate_needs_verification",
        "boundary_note": "ADDM: five counties in metropolitan St. Louis; county list should be verified from site documentation.",
    },
    {
        "site": "Missouri",
        "fips": "29510",
        "county_label": "St. Louis City, MO",
        "match_quality": "county_approximate_needs_verification",
        "boundary_note": "ADDM: five counties in metropolitan St. Louis; county list should be verified from site documentation.",
    },
    {
        "site": "New Jersey",
        "fips": "34013",
        "county_label": "Essex County, NJ",
        "match_quality": "county_approximate_needs_verification",
        "boundary_note": "ADDM: two counties in New York metropolitan area; county list should be verified from site documentation.",
    },
    {
        "site": "New Jersey",
        "fips": "34039",
        "county_label": "Union County, NJ",
        "match_quality": "county_approximate_needs_verification",
        "boundary_note": "ADDM: two counties in New York metropolitan area; county list should be verified from site documentation.",
    },
    {
        "site": "Tennessee",
        "fips": "47021",
        "county_label": "Cheatham County, TN",
        "match_quality": "candidate_needs_verification",
        "boundary_note": "Candidate county for ADDM middle Tennessee site; verify against ADDM site documentation before formal inference.",
    },
    {
        "site": "Tennessee",
        "fips": "47037",
        "county_label": "Davidson County, TN",
        "match_quality": "candidate_needs_verification",
        "boundary_note": "Candidate county for ADDM middle Tennessee site; verify against ADDM site documentation before formal inference.",
    },
    {
        "site": "Tennessee",
        "fips": "47043",
        "county_label": "Dickson County, TN",
        "match_quality": "candidate_needs_verification",
        "boundary_note": "Candidate county for ADDM middle Tennessee site; verify against ADDM site documentation before formal inference.",
    },
    {
        "site": "Tennessee",
        "fips": "47119",
        "county_label": "Maury County, TN",
        "match_quality": "candidate_needs_verification",
        "boundary_note": "Candidate county for ADDM middle Tennessee site; verify against ADDM site documentation before formal inference.",
    },
    {
        "site": "Tennessee",
        "fips": "47125",
        "county_label": "Montgomery County, TN",
        "match_quality": "candidate_needs_verification",
        "boundary_note": "Candidate county for ADDM middle Tennessee site; verify against ADDM site documentation before formal inference.",
    },
    {
        "site": "Tennessee",
        "fips": "47147",
        "county_label": "Robertson County, TN",
        "match_quality": "candidate_needs_verification",
        "boundary_note": "Candidate county for ADDM middle Tennessee site; verify against ADDM site documentation before formal inference.",
    },
    {
        "site": "Tennessee",
        "fips": "47149",
        "county_label": "Rutherford County, TN",
        "match_quality": "candidate_needs_verification",
        "boundary_note": "Candidate county for ADDM middle Tennessee site; verify against ADDM site documentation before formal inference.",
    },
    {
        "site": "Tennessee",
        "fips": "47165",
        "county_label": "Sumner County, TN",
        "match_quality": "candidate_needs_verification",
        "boundary_note": "Candidate county for ADDM middle Tennessee site; verify against ADDM site documentation before formal inference.",
    },
    {
        "site": "Tennessee",
        "fips": "47187",
        "county_label": "Williamson County, TN",
        "match_quality": "candidate_needs_verification",
        "boundary_note": "Candidate county for ADDM middle Tennessee site; verify against ADDM site documentation before formal inference.",
    },
    {
        "site": "Tennessee",
        "fips": "47189",
        "county_label": "Wilson County, TN",
        "match_quality": "candidate_needs_verification",
        "boundary_note": "Candidate county for ADDM middle Tennessee site; verify against ADDM site documentation before formal inference.",
    },
    {
        "site": "Tennessee",
        "fips": "47169",
        "county_label": "Trousdale County, TN",
        "match_quality": "candidate_needs_verification",
        "boundary_note": "Candidate county for ADDM middle Tennessee site; verify against ADDM site documentation before formal inference.",
    },
    {
        "site": "Utah",
        "fips": "49011",
        "county_label": "Davis County, UT",
        "match_quality": "county_approximate_needs_verification",
        "boundary_note": "ADDM: three counties in northern Utah; county list should be verified from site documentation.",
    },
    {
        "site": "Utah",
        "fips": "49035",
        "county_label": "Salt Lake County, UT",
        "match_quality": "county_approximate_needs_verification",
        "boundary_note": "ADDM: three counties in northern Utah; county list should be verified from site documentation.",
    },
    {
        "site": "Utah",
        "fips": "49045",
        "county_label": "Tooele County, UT",
        "match_quality": "county_approximate_needs_verification",
        "boundary_note": "ADDM: three counties in northern Utah; county list should be verified from site documentation.",
    },
    {
        "site": "Wisconsin",
        "fips": "55059",
        "county_label": "Kenosha County, WI",
        "match_quality": "candidate_needs_verification",
        "boundary_note": "Candidate county for ADDM southeastern Wisconsin site; verify against ADDM site documentation before formal inference.",
    },
    {
        "site": "Wisconsin",
        "fips": "55079",
        "county_label": "Milwaukee County, WI",
        "match_quality": "candidate_needs_verification",
        "boundary_note": "Candidate county for ADDM southeastern Wisconsin site; verify against ADDM site documentation before formal inference.",
    },
    {
        "site": "Wisconsin",
        "fips": "55089",
        "county_label": "Ozaukee County, WI",
        "match_quality": "candidate_needs_verification",
        "boundary_note": "Candidate county for ADDM southeastern Wisconsin site; verify against ADDM site documentation before formal inference.",
    },
    {
        "site": "Wisconsin",
        "fips": "55101",
        "county_label": "Racine County, WI",
        "match_quality": "candidate_needs_verification",
        "boundary_note": "Candidate county for ADDM southeastern Wisconsin site; verify against ADDM site documentation before formal inference.",
    },
    {
        "site": "Wisconsin",
        "fips": "55127",
        "county_label": "Walworth County, WI",
        "match_quality": "candidate_needs_verification",
        "boundary_note": "Candidate county for ADDM southeastern Wisconsin site; verify against ADDM site documentation before formal inference.",
    },
    {
        "site": "Wisconsin",
        "fips": "55131",
        "county_label": "Washington County, WI",
        "match_quality": "candidate_needs_verification",
        "boundary_note": "Candidate county for ADDM southeastern Wisconsin site; verify against ADDM site documentation before formal inference.",
    },
    {
        "site": "Wisconsin",
        "fips": "55133",
        "county_label": "Waukesha County, WI",
        "match_quality": "candidate_needs_verification",
        "boundary_note": "Candidate county for ADDM southeastern Wisconsin site; verify against ADDM site documentation before formal inference.",
    },
    {
        "site": "Wisconsin",
        "fips": "55055",
        "county_label": "Jefferson County, WI",
        "match_quality": "candidate_needs_verification",
        "boundary_note": "Candidate county for ADDM southeastern Wisconsin site; verify against ADDM site documentation before formal inference.",
    },
]

SITES_NEEDING_COUNTY_LIST = {}


def parse_prevalence(value):
    match = re.search(r"[-+]?\d*\.?\d+", str(value))
    return float(match.group(0)) if match else None


def load_addm_tables():
    tables = pd.read_html(ADDM_REPORT_URL)
    site_info = tables[0].copy()
    prevalence = tables[1].copy()

    prevalence.columns = [
        "site",
        "asd_cases",
        "addm_age8_population",
        "asd_prevalence_per_1000_ci",
        "male_prevalence_per_1000_ci",
        "female_prevalence_per_1000_ci",
        "male_female_ratio_ci",
    ]
    prevalence = prevalence[prevalence["site"].ne("Total")].copy()
    prevalence["asd_prevalence_per_1000"] = prevalence["asd_prevalence_per_1000_ci"].map(parse_prevalence)
    prevalence["male_prevalence_per_1000"] = prevalence["male_prevalence_per_1000_ci"].map(parse_prevalence)
    prevalence["female_prevalence_per_1000"] = prevalence["female_prevalence_per_1000_ci"].map(parse_prevalence)
    prevalence["addm_year"] = 2020
    prevalence["addm_source"] = ADDM_REPORT_URL

    site_info = site_info.rename(
        columns={
            "Site": "site",
            "Surveillance area description": "surveillance_area_description",
            "Total population aged 8 yrs": "site_population_age8_from_table1",
        }
    )
    return prevalence.merge(
        site_info[["site", "surveillance_area_description", "site_population_age8_from_table1"]],
        on="site",
        how="left",
    )


def weighted_mean(df, value_col, weight_col):
    sub = df[[value_col, weight_col]].copy()
    sub[value_col] = pd.to_numeric(sub[value_col], errors="coerce")
    sub[weight_col] = pd.to_numeric(sub[weight_col], errors="coerce")
    sub = sub.dropna()
    sub = sub[sub[weight_col] > 0]
    if sub.empty:
        return None
    return (sub[value_col] * sub[weight_col]).sum() / sub[weight_col].sum()


def main():
    addm = load_addm_tables()
    crosswalk = pd.DataFrame(ADDM_COUNTY_CROSSWALK)
    crosswalk["fips"] = crosswalk["fips"].astype(str).str.zfill(5)
    crosswalk.to_csv("addm_2020_site_county_crosswalk.csv", index=False, encoding="utf-8-sig")

    exposure = pd.read_csv(COUNTY_EXPOSURE_FILE, dtype={"fips": str, "state_fips": str, "county_fips": str})
    exposure["fips"] = exposure["fips"].str.zfill(5)

    detail = crosswalk.merge(exposure, on="fips", how="left")
    detail.to_csv("addm_2020_county_exposure_detail.csv", index=False, encoding="utf-8-sig")

    rows = []
    for site, group in detail.groupby("site", dropna=False):
        qualities = sorted(group["match_quality"].dropna().unique())
        rows.append(
            {
                "site": site,
                "mapped_counties": len(group),
                "mapped_fips": ";".join(group["fips"].dropna().astype(str)),
                "mapped_county_labels": "; ".join(group["county_label"].dropna().astype(str)),
                "match_quality": ";".join(qualities),
                "county_rows_found_in_exposure": int(group["State Name"].notna().sum()),
                "counties_with_lead": int(group["Pb_PM25_2019_2021_mean_ngm3"].notna().sum()),
                "counties_with_pm25": int(group["PM25_2019_2021_mean_ugm3"].notna().sum()),
                "Pb_PM25_2019_2021_mean_ngm3_unweighted": group["Pb_PM25_2019_2021_mean_ngm3"].mean(),
                "Pb_PM25_2019_2021_mean_ngm3_pop_weighted": weighted_mean(group, "Pb_PM25_2019_2021_mean_ngm3", "total_population"),
                "PM25_2019_2021_mean_ugm3_unweighted": group["PM25_2019_2021_mean_ugm3"].mean(),
                "PM25_2019_2021_mean_ugm3_pop_weighted": weighted_mean(group, "PM25_2019_2021_mean_ugm3", "total_population"),
                "median_household_income_pop_weighted": weighted_mean(group, "median_household_income", "total_population"),
                "poverty_rate_pct_pop_weighted": weighted_mean(group, "poverty_rate_pct", "total_population"),
                "bachelor_or_higher_pct_pop_weighted": weighted_mean(group, "bachelor_or_higher_pct", "total_population"),
                "aggregation_note": "Population-weighted values use ACS 2022 total population as weights among nonmissing county exposure values.",
            }
        )

    for site, note in SITES_NEEDING_COUNTY_LIST.items():
        rows.append(
            {
                "site": site,
                "mapped_counties": 0,
                "mapped_fips": "",
                "mapped_county_labels": "",
                "match_quality": "needs_county_list",
                "county_rows_found_in_exposure": 0,
                "counties_with_lead": 0,
                "counties_with_pm25": 0,
                "Pb_PM25_2019_2021_mean_ngm3_unweighted": None,
                "Pb_PM25_2019_2021_mean_ngm3_pop_weighted": None,
                "PM25_2019_2021_mean_ugm3_unweighted": None,
                "PM25_2019_2021_mean_ugm3_pop_weighted": None,
                "median_household_income_pop_weighted": None,
                "poverty_rate_pct_pop_weighted": None,
                "bachelor_or_higher_pct_pop_weighted": None,
                "aggregation_note": note,
            }
        )

    site_exposure = pd.DataFrame(rows)
    matched = addm.merge(site_exposure, on="site", how="left")
    matched = matched.sort_values("site")
    matched.to_csv("addm_2020_exposure_matched.csv", index=False, encoding="utf-8-sig")
    addm.to_csv("addm_2020_site_prevalence.csv", index=False, encoding="utf-8-sig")

    summary = pd.DataFrame(
        [
            ["addm_sites", len(addm)],
            ["sites_with_any_county_mapping", int(matched["mapped_counties"].fillna(0).gt(0).sum())],
            ["sites_needing_county_list", int(matched["match_quality"].eq("needs_county_list").sum())],
            ["sites_with_lead_exposure", int(matched["counties_with_lead"].fillna(0).gt(0).sum())],
            ["sites_with_pm25_exposure", int(matched["counties_with_pm25"].fillna(0).gt(0).sum())],
            ["sites_with_both_exposures", int(matched[["counties_with_lead", "counties_with_pm25"]].fillna(0).gt(0).all(axis=1).sum())],
        ],
        columns=["metric", "value"],
    )
    summary.to_csv("addm_2020_exposure_match_summary.csv", index=False, encoding="utf-8-sig")

    print(summary.to_string(index=False))
    print("\nmatched preview:")
    print(matched[["site", "asd_prevalence_per_1000", "match_quality", "counties_with_lead", "counties_with_pm25", "Pb_PM25_2019_2021_mean_ngm3_pop_weighted", "PM25_2019_2021_mean_ugm3_pop_weighted"]].to_string(index=False))


if __name__ == "__main__":
    main()
