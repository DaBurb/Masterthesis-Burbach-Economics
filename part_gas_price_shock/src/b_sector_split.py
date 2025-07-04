# part_gas_price_shock/src/b_sector_split.py

import pandas as pd
import numpy as np


def compute_b_gas_share_matrix(exio_Z_df: pd.DataFrame) -> pd.DataFrame:
    """
    Given a full EXIOBASE Z matrix with B_gas and B_nongas sectors already split,
    this function returns a gas share matrix representing the normalized share
    structure for splitting sector B in another dataset.

    The output matrix contains:
    - Row-wise shares in off-diagonal rows
    - Column-wise shares in off-diagonal columns
    - B quadrant normalized values per country-pair
    """

    # Step 1: Start with full matrix of ones
    gas_share_matrix = pd.DataFrame(1.0, index=exio_Z_df.index, columns=exio_Z_df.columns)

    row_sectors = ["B_gas", "B_nongas"]
    col_sectors = ["B_gas", "B_nongas"]

    # Step 2: Row-wise shares (outside B quadrant)
    energy_rows = exio_Z_df.index.get_level_values(1).isin(row_sectors)
    non_b_cols = ~exio_Z_df.columns.get_level_values(1).isin(col_sectors)
    energy_data = exio_Z_df.loc[energy_rows, non_b_cols]
    total_energy_row = energy_data.groupby(level=0).sum()
    total_energy_row_safe = total_energy_row.copy()
    total_energy_row_safe[total_energy_row_safe.sum(axis=1) == 0] = 1
    row_shares = energy_data.div(total_energy_row_safe, level=0).fillna(0)
    gas_share_matrix.loc[energy_rows, non_b_cols] = row_shares.values

    # Step 3: Column-wise shares (non-B rows to B columns)
    non_b_rows = ~exio_Z_df.index.get_level_values(1).isin(row_sectors)
    energy_cols_mask = exio_Z_df.columns.get_level_values(1).isin(col_sectors)

    for idx in exio_Z_df.index[non_b_rows]:
        b_gas = exio_Z_df.loc[[idx], exio_Z_df.columns[energy_cols_mask & (exio_Z_df.columns.get_level_values(1) == "B_gas")]]
        b_nongas = exio_Z_df.loc[[idx], exio_Z_df.columns[energy_cols_mask & (exio_Z_df.columns.get_level_values(1) == "B_nongas")]]

        total = b_gas.values + b_nongas.values
        total[total == 0] = 1  # Prevent division by zero

        share_gas = b_gas.values / total
        share_nongas = b_nongas.values / total

        for col, val in zip(b_gas.columns, share_gas.flatten()):
            gas_share_matrix.loc[idx, col] = val
        for col, val in zip(b_nongas.columns, share_nongas.flatten()):
            gas_share_matrix.loc[idx, col] = val


    # Step 4: B quadrant normalization
    for sup_country in exio_Z_df.index.get_level_values(0).unique():
        for con_country in exio_Z_df.columns.get_level_values(0).unique():
            row_idx = (exio_Z_df.index.get_level_values(0) == sup_country) & \
                      (exio_Z_df.index.get_level_values(1).isin(row_sectors))
            col_idx = (exio_Z_df.columns.get_level_values(0) == con_country) & \
                      (exio_Z_df.columns.get_level_values(1).isin(col_sectors))
            block = exio_Z_df.loc[row_idx, col_idx]
            total = block.values.sum()
            if total > 0:
                norm_block = block / total
            else:
                norm_block = block * 0
                try:
                    norm_block.loc[(sup_country, "B_nongas"), (con_country, "B_nongas")] = 1
                    norm_block.loc[(sup_country, "B_gas"), (con_country, "B_gas")] = 0
                except KeyError:
                    continue
            gas_share_matrix.loc[row_idx, col_idx] = norm_block.values

    return gas_share_matrix


def split_b_sector(figaro_df: pd.DataFrame) -> pd.DataFrame:
    """
    Splits all rows and columns of sector 'B' into 'B_gas' and 'B_nongas'.
    Duplicates values, then removes the original 'B' rows and columns.

    Parameters:
        figaro_df (pd.DataFrame): IO matrix with (Country, Sector) on both axes.

    Returns:
        pd.DataFrame: Matrix with 'B_gas' and 'B_nongas' replacing 'B'.
    """

    def update_sector(index, new_label):
        return pd.MultiIndex.from_tuples(
            [(country, new_label if sector == "B" else sector) for country, sector in index],
            names=index.names
        )

    def update_column(columns, new_label):
        return pd.MultiIndex.from_tuples(
            [(country, new_label if sector == "B" else sector) for country, sector in columns],
            names=columns.names
        )

    # === Step 1: Duplicate B-sector rows ===
    b_rows = figaro_df.loc[figaro_df.index.get_level_values("Sector") == "B"].copy()
    b_gas_rows = b_rows.copy()
    b_nongas_rows = b_rows.copy()
    b_gas_rows.index = update_sector(b_rows.index, "B_gas")
    b_nongas_rows.index = update_sector(b_rows.index, "B_nongas")

    # === Step 2: Remove B-sector rows ===
    non_b_rows = figaro_df.loc[figaro_df.index.get_level_values("Sector") != "B"]

    # === Step 3: Add duplicated B-sector rows ===
    df_rows_extended = pd.concat([non_b_rows, b_gas_rows, b_nongas_rows]).sort_index()

    # === Step 4: Duplicate B-sector columns ===
    b_cols = df_rows_extended.loc[:, df_rows_extended.columns.get_level_values("Sector") == "B"].copy()
    b_gas_cols = b_cols.copy()
    b_nongas_cols = b_cols.copy()
    b_gas_cols.columns = update_column(b_cols.columns, "B_gas")
    b_nongas_cols.columns = update_column(b_cols.columns, "B_nongas")

    # === Step 5: Remove B-sector columns ===
    non_b_cols = df_rows_extended.loc[:, df_rows_extended.columns.get_level_values("Sector") != "B"]

    # === Step 6: Add duplicated B-sector columns ===
    df_figaro_updated = pd.concat([non_b_cols, b_gas_cols, b_nongas_cols], axis=1).sort_index(axis=1)

    # === Final formatting ===
    df_figaro_updated.index.names = ["Country", "Sector"]
    df_figaro_updated.columns.names = ["Country", "Sector"]

    return df_figaro_updated


def apply_b_gas_weights(figaro_df: pd.DataFrame, weights_df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply gas weights to Figaro DataFrame for both rows and columns.
    - Weights are applied to B_gas/B_nongas rows first.
    - When applying to columns, skip B_gas/B_nongas rows (to avoid double weighting).
    - Handles aggregate sector C25-33 for ["C25", "C26", "C27", "C28", "C29", "C30", "C31_32", "C33"].

    Args:
        figaro_df (pd.DataFrame): Figaro technical coefficient matrix (MultiIndex).
        weights_df (pd.DataFrame): Weight matrix (MultiIndex).

    Returns:
        pd.DataFrame: Weighted Figaro DataFrame.
    """
    # Copy to avoid modifying original
    df = figaro_df.copy()
    disagg_sectors = ["C25", "C26", "C27", "C28", "C29", "C30", "C31_32", "C33"]
    agg_sector = "C25-C33"

    # --- Apply row weights to B_gas/B_nongas rows ---
    for row_country, row_sector in df.index:
        if row_sector in ["B_gas", "B_nongas"]:
            for col_country, col_sector in df.columns:
                # Use aggregate weight for disaggregated sectors if available
                weight_col_sector = (
                    agg_sector if col_sector in disagg_sectors and (col_country, agg_sector) in weights_df.columns
                    else col_sector
                )
                if (row_country, row_sector) in weights_df.index and (col_country, weight_col_sector) in weights_df.columns:
                    weight = weights_df.loc[(row_country, row_sector), (col_country, weight_col_sector)]
                    df.loc[(row_country, row_sector), (col_country, col_sector)] *= weight

    # --- Apply column weights to B_gas/B_nongas columns, skipping B_gas/B_nongas rows ---
    for col_country, col_sector in df.columns:
        if col_sector in ["B_gas", "B_nongas"]:
            for row_country, row_sector in df.index:
                if row_sector in ["B_gas", "B_nongas"]:
                    continue  # Skip, already weighted
                # Use aggregate weight for disaggregated sectors if available
                weight_row_sector = (
                    agg_sector if row_sector in disagg_sectors and (row_country, agg_sector) in weights_df.index
                    else row_sector
                )
                if (row_country, weight_row_sector) in weights_df.index and (col_country, col_sector) in weights_df.columns:
                    weight = weights_df.loc[(row_country, weight_row_sector), (col_country, col_sector)]
                    df.loc[(row_country, row_sector), (col_country, col_sector)] *= weight

    return df


import pandas as pd
from typing import List

def merge_countries(df: pd.DataFrame, countries_to_merge: List[str], target: str = "FIGW1") -> pd.DataFrame:
    """
    Relabels rows and columns so that any country in countries_to_merge is replaced by target.
    Then groups by the MultiIndex to sum the duplicated entries.

    Parameters:
        df (pd.DataFrame): DataFrame with MultiIndex for both rows and columns.
        countries_to_merge (List[str]): List of country codes to merge (e.g., ['AR', 'SA']).
        target (str): Target country code to absorb the values (default 'FIGW1').

    Returns:
        pd.DataFrame: Modified DataFrame with countries merged.
    """
    assert isinstance(df.index, pd.MultiIndex)
    assert isinstance(df.columns, pd.MultiIndex)

    # Save original names
    row_index_names = df.index.names
    col_index_names = df.columns.names

    # Replace countries in row index
    new_row_index = [
        (target if country in countries_to_merge else country, sector)
        for country, sector in df.index
    ]
    df.index = pd.MultiIndex.from_tuples(new_row_index, names=row_index_names)

    # Replace countries in column index
    new_col_index = [
        (target if country in countries_to_merge else country, sector)
        for country, sector in df.columns
    ]
    df.columns = pd.MultiIndex.from_tuples(new_col_index, names=col_index_names)

    # Group by both row and column indices
    df = df.groupby(level=row_index_names).sum()
    df = df.groupby(axis=1, level=col_index_names).sum()

    return df
