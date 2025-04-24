import sys
from pathlib import Path

# Add the root project directory to the system path
sys.path.append(str(Path(__file__).resolve().parents[2]))

import numpy as np
import pandas as pd
from pathlib import Path
from config import SEA_PROCESSED_DIR
from sea_loader import load_sea_data

# SEA to FIGARO country code mapping
SEA_TO_FIGARO = {
    # EU + OECD + Other WIOD countries
    "AUS": "AU", "AUT": "AT", "BEL": "BE", "BGR": "BG", "BRA": "BR",
    "CAN": "CA", "CHE": "CH", "CHN": "CN", "CYP": "CY", "CZE": "CZ",
    "DEU": "DE", "DNK": "DK", "ESP": "ES", "EST": "EE", "FIN": "FI",
    "FRA": "FR", "GBR": "GB", "GRC": "GR", "HRV": "HR", "HUN": "HU",
    "IDN": "ID", "IND": "IN", "IRL": "IE", "ITA": "IT", "JPN": "JP",
    "KOR": "KR", "LTU": "LT", "LUX": "LU", "LVA": "LV", "MEX": "MX",
    "MLT": "MT", "NLD": "NL", "NOR": "NO", "POL": "PL", "PRT": "PT",
    "ROU": "RO", "RUS": "RU", "SVK": "SK", "SVN": "SI", "SWE": "SE",
    "TUR": "TR", "USA": "US", "ZAF": "ZA", "ARG": "AR", "SAU": "SA",
}

EXCLUDED_COUNTRIES = {"TWN"}
ADDITIONAL_COUNTRIES = ["SA", "ZA", "AR", "FIGW1"]


def calculate_percentage_price_changes(price_data, year_columns):
    pct_price_changes = price_data[['country', 'variable', 'code']].copy()
    for i in range(1, len(year_columns)):
        cur, prev = year_columns[i], year_columns[i - 1]
        pct_price_changes[f'{cur}_pct_change'] = (
            (price_data[cur] - price_data[prev]) / price_data[prev]
        ) * 100
    return pct_price_changes


def calculate_price_volatility(df, variable):
    df = df[df['variable'] == variable]
    year_cols = df.columns[4:]
    pct_changes = calculate_percentage_price_changes(df, year_cols)
    change_cols = [col for col in pct_changes.columns if col.endswith('_pct_change')]
    pct_changes['mean_pct_change'] = pct_changes[change_cols].mean(axis=1)
    pct_changes['price_volatility'] = np.sqrt(
        ((pct_changes[change_cols].sub(pct_changes['mean_pct_change'], axis=0)) ** 2).mean(axis=1)
    )
    return pct_changes[['country', 'code', 'price_volatility']]


def map_and_adjust_volatility(vol_df):
    vol_df['country'] = vol_df['country'].replace(SEA_TO_FIGARO)
    vol_df = vol_df[~vol_df['country'].isin(EXCLUDED_COUNTRIES)]

    sectors = vol_df['code'].unique()
    for country in ADDITIONAL_COUNTRIES:
        for sector in sectors:
            vol_df = pd.concat([
                vol_df,
                pd.DataFrame({'country': [country], 'code': [sector], 'price_volatility': [0]})
            ], ignore_index=True)

    vol_df['sector'] = vol_df['country'] + "_" + vol_df['code']
    return vol_df[['sector', 'price_volatility']].sort_values(by='sector').reset_index(drop=True)

def convert_to_multiindex(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converts a DataFrame with a combined 'sector' column (e.g., 'AR_C10-C12')
    into a MultiIndexed DataFrame with levels ['Country', 'Sector'].

    Parameters:
        df (pd.DataFrame): DataFrame with 'sector' column.

    Returns:
        pd.DataFrame: MultiIndexed DataFrame with ('Country', 'Sector').
    """
    countries = []
    sectors = []

    for label in df['sector']:
        if "_" not in label:
            raise ValueError(f"Label '{label}' cannot be split at '_'.")
        country, sector = label.split("_", 1)
        countries.append(country)
        sectors.append(sector)

    df.index = pd.MultiIndex.from_arrays([countries, sectors], names=["Country", "Sector"])
    return df.drop(columns=["sector"])


def process_sea_ii_volatility() -> pd.DataFrame:
    df = load_sea_data(sheet_name="DATA")
    volatility = calculate_price_volatility(df, "II_PI")
    adjusted = map_and_adjust_volatility(volatility)
    final = convert_to_multiindex(adjusted)  # ← new step here

    SEA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    output_path = SEA_PROCESSED_DIR / "II_PI_volatility.csv"
    final.to_csv(output_path)
    print(f"II_PI volatility saved to: {output_path}")
    return final

