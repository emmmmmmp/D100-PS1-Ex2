import pandas as pd


def clean_gdp(data):
    """Keep valid, unique country-year observations for 2000-2022."""
    result = data[
        ["country", "country_code", "year", "gdp"]
    ].copy()

    result["year"] = pd.to_numeric(result["year"], errors="coerce")
    result["gdp"] = pd.to_numeric(result["gdp"], errors="coerce")

    result = result.dropna(
        subset=["country", "country_code", "year", "gdp"]
    )

    result = result.loc[
        result["year"].between(2000, 2022)
    ].copy()

    result["year"] = result["year"].astype(int)
    result = result.drop_duplicates()

    if result.duplicated(["country_code", "year"]).any():
        raise ValueError(
            "Conflicting GDP values for the same country and year."
        )

    return result.sort_values(
        ["country", "year"]
    ).reset_index(drop=True)


def summarise_gdp(data):
    """Compare each country's real GDP in 2000 and 2022."""
    wide = data.pivot(
        index="country",
        columns="year",
        values="gdp",
    )

    summary = pd.DataFrame({
        "GDP_2000_trillion": wide[2000] / 1e12,
        "GDP_2022_trillion": wide[2022] / 1e12,
        "change_percent": (wide[2022] / wide[2000] - 1) * 100,
    })

    return summary.sort_values(
        "change_percent",
        ascending=False,
    )
