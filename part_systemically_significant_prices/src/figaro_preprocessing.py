# figaro_preprocessing.py

import pandas as pd
import numpy as np

AGGREGATION_SCHEMES = {
    "N": ["N77", "N78", "N79", "N80T82"],
    "Q": ["Q86", "Q87_88"],
    "R_S": ["R90T92", "R93", "S94", "S95", "S96"],
}


def aggregate_sectors(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rename and aggregate sectors in both rows and columns using a predefined mapping.
    This avoids manual slicing and guarantees dimensional alignment.
    
    Parameters:
        df (pd.DataFrame): MultiIndexed DataFrame with (Country, Sector) rows and columns.
    
    Returns:
        pd.DataFrame: Aggregated DataFrame.
    """
    aggregation_mapping = {
        "N77": "N", "N78": "N", "N79": "N", "N80-N82": "N",
        "Q86": "Q", "Q87_Q88": "Q",
        "R90-R92": "R_S", "R93": "R_S", "S94": "R_S", "S95": "R_S", "S96": "R_S"
    }

    # Rename sectors in index
    new_index = [
        (country, aggregation_mapping.get(sector, sector)) for country, sector in df.index
    ]
    df.index = pd.MultiIndex.from_tuples(new_index, names=["Country", "Sector"])

    # Rename sectors in columns
    new_columns = [
        (country, aggregation_mapping.get(sector, sector)) for country, sector in df.columns
    ]
    df.columns = pd.MultiIndex.from_tuples(new_columns, names=["Country", "Sector"])

    # Aggregate renamed entries
    df = df.groupby(level=["Country", "Sector"]).sum()
    df = df.groupby(level=["Country", "Sector"], axis=1).sum()

    return df

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
