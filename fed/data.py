import json
from pathlib import Path
from urllib.request import urlopen

import pandas as pd


def load_gdp(raw_path):
    """Download World Bank GDP data once, then load the saved copy."""
    raw_path = Path(raw_path)

    if raw_path.exists():
        payload = json.loads(raw_path.read_text(encoding="utf-8"))
    else:
        url = (
            "https://api.worldbank.org/v2/country/"
            "GBR;USA;BRA;JPN;CHN;DEU;CHE/indicator/NY.GDP.MKTP.KD"
            "?date=2000:2022&format=json&per_page=1000"
        )

        with urlopen(url, timeout=60) as response:
            payload = json.load(response)

        if len(payload) != 2 or not isinstance(payload[1], list):
            raise ValueError("The API did not return the expected GDP data.")

        if int(payload[0]["pages"]) != 1:
            raise ValueError(
                "The response has multiple pages; increase per_page."
            )

        raw_path.parent.mkdir(parents=True, exist_ok=True)
        raw_path.write_text(
            json.dumps(payload, indent=2),
            encoding="utf-8",
        )

    return pd.DataFrame([
        {
            "country": row["country"]["value"],
            "country_code": row["countryiso3code"],
            "year": row["date"],
            "gdp": row["value"],
        }
        for row in payload[1]
    ])

# data cleaning


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
