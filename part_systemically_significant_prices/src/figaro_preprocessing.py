# figaro_preprocessing.py

import pandas as pd
import numpy as np

def add_cpi_weights(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate and add CPI weight columns per country based on household consumption columns.

    Parameters:
        df (pd.DataFrame): MultiIndexed DataFrame with (Country, Sector) rows and columns.

    Returns:
        pd.DataFrame: DataFrame with one new column per country for CPI weight.
    """
    consumption_code = "P3_S14"
    excluded_codes = ["D21X31", "OP_RES", "OP_NRES", "D1", "D29X39", "B2A3G", "GO"]

    weight_data = {}

    countries = df.columns.get_level_values("Country").unique()

    for country in countries:
        col = (country, consumption_code)
        if col not in df.columns:
            continue

        # Exclude rows where the sector is one of the specified codes
        valid_rows = [
            idx for idx in df.index
            if idx[0] == country and idx[1] not in excluded_codes
        ]
        total = df.loc[valid_rows, col].sum()
        weights = df[col] / total if total != 0 else 0
        weight_data[(country, "cpi_weight")] = weights

    for new_col, series in weight_data.items():
        df[new_col] = series

    df = df.sort_index(axis=1)
    return df
