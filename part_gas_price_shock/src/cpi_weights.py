import pandas as pd
import numpy as np

def split_b_sector_rows_for_final_demand(figaro_Y_df: pd.DataFrame, target_category: str = "P3_S14") -> pd.DataFrame:
    """
    Duplicates the 'B' row into 'B_gas' and 'B_nongas' in a FIGARO-style Y matrix and removes the original 'B' row.
    Optionally filters columns to the given target category (e.g., 'P3_S14' for households).

    Parameters:
        figaro_Y_df (pd.DataFrame): FIGARO Y matrix with (Country, Sector) index and (Country, Category) columns.
        target_category (str): Final demand category to retain (default 'P3_S14').

    Returns:
        pd.DataFrame: Modified Y matrix with 'B' row replaced by 'B_gas' and 'B_nongas', only for selected columns.
    """
    # Filter columns to the relevant category
    filtered_cols = [col for col in figaro_Y_df.columns if col[1] == target_category]
    df = figaro_Y_df[filtered_cols].copy()
    df.columns = pd.MultiIndex.from_tuples(filtered_cols, names=["Country", "Category"])

    # Identify and duplicate the 'B' row
    b_row_mask = df.index.get_level_values("Sector") == "B"
    b_rows = df[b_row_mask].copy()

    b_gas_rows = b_rows.copy()
    b_gas_rows.index = pd.MultiIndex.from_tuples(
        [(country, "B_gas") for country, _ in b_rows.index],
        names=df.index.names
    )

    b_nongas_rows = b_rows.copy()
    b_nongas_rows.index = pd.MultiIndex.from_tuples(
        [(country, "B_nongas") for country, _ in b_rows.index],
        names=df.index.names
    )

    # Drop original B row
    df_no_b = df[~b_row_mask]

    # Add duplicated B rows and sort
    df_extended = pd.concat([df_no_b, b_gas_rows, b_nongas_rows]).sort_index()

    return df_extended

def compute_origin_specific_b_gas_shares(exio_Y_df: pd.DataFrame, target_category: str = "Final consumption expenditure by households") -> pd.DataFrame:
    """
    Compute the share of B_gas and B_nongas in household consumption for each origin country,
    broken down by destination country (column).

    Parameters:
        exio_Y_df (pd.DataFrame): EXIO Y matrix with MultiIndex rows (origin_country, sector)
                                  and MultiIndex columns (dest_country, category)

    Returns:
        pd.DataFrame: DataFrame with MultiIndex (origin_country, sector) and
                      columns = dest_country, values = share of gas/nongas in that origin's B sector.
    """
    # 1. Keep only household consumption columns
    household_cols = [col for col in exio_Y_df.columns if col[1] == target_category]
    df = exio_Y_df[household_cols].copy()
    df.columns = [col[0] for col in df.columns]  # flatten: now just destination country

    # 2. Filter only B_gas and B_nongas
    b_mask = df.index.get_level_values("Sector").isin(["B_gas", "B_nongas"])
    df = df.loc[b_mask]

    # 3. Split into B_gas and B_nongas
    df_gas = df[df.index.get_level_values("Sector") == "B_gas"]
    df_nongas = df[df.index.get_level_values("Sector") == "B_nongas"]

    # 4. Align by origin country
    origins = df_gas.index.get_level_values("Country")
    df_total = df_gas.values + df_nongas.values

    # Avoid division by 0
    with np.errstate(divide='ignore', invalid='ignore'):
        gas_share = np.divide(df_gas.values, df_total, out=np.zeros_like(df_gas.values), where=(df_total != 0))
        nongas_share = np.divide(df_nongas.values, df_total, out=np.zeros_like(df_nongas.values), where=(df_total != 0))

    # 5. Reconstruct output DataFrame
    gas_share_df = pd.DataFrame(
        gas_share,
        index=df_gas.index,
        columns=df.columns
    )

    nongas_share_df = pd.DataFrame(
        nongas_share,
        index=df_nongas.index,
        columns=df.columns
    )

    # 6. Combine vertically
    result = pd.concat([gas_share_df, nongas_share_df]).sort_index()

    return result

def apply_b_gas_shares_to_Y(figaro_Y_split: pd.DataFrame, gas_nongas_shares: pd.DataFrame) -> pd.DataFrame:
    """
    Applies EXIOBASE-based gas/nongas shares to the 'B_gas' and 'B_nongas' rows
    in a FIGARO final demand (Y) matrix, using origin-destination-level shares.

    Parameters:
        figaro_Y_split (pd.DataFrame): FIGARO Y matrix with duplicated 'B' rows into 'B_gas' and 'B_nongas'.
                                       Index: (origin_country, sector), Columns: (destination_country, category)
        gas_nongas_shares (pd.DataFrame): Share matrix with origin (Country, Sector) as index,
                                     columns = destination country (1 level only).

    Returns:
        pd.DataFrame: Updated Y matrix with weighted B_gas and B_nongas rows.
    """
    df = figaro_Y_split.copy()

    for (origin_country, sector) in df.index:
        if sector not in ["B_gas", "B_nongas"]:
            continue
        if (origin_country, sector) not in gas_nongas_shares.index:
            continue

        for col in df.columns:
            dest_country = col[0]  # column = (dest_country, category)
            if dest_country not in gas_nongas_shares.columns:
                continue

            share = gas_nongas_shares.loc[(origin_country, sector), dest_country]
            df.loc[(origin_country, sector), col] *= share

    return df


import pandas as pd
from pathlib import Path
from typing import Optional

def apply_cpi_weights_to_gas_price_shock(
    price_change_path: Path,
    cpi_weights_path: Path,
    regions: list[str],
    output_path: Optional[Path] = None
) -> pd.DataFrame:
    """
    Applies CPI weights from multiple regions to a price change vector.

    Parameters:
        price_change_path (Path): Path to CSV with (Country, Sector) index and one column (e.g., 'Price Change').
        cpi_weights_path (Path): Path to CPI weights CSV with MultiIndex index and MultiIndex columns (Region, 'cpi_weight').
        regions (list[str]): List of region names to extract from CPI weights.
        output_path (Path | None): Optional path to save the result.

    Returns:
        pd.DataFrame: DataFrame with (Country, Sector) index and one column per region (e.g., 'EU28_impact').
    """
    # Load data
    price_changes = pd.read_csv(price_change_path, index_col=[0, 1])
    cpi_weights = pd.read_csv(cpi_weights_path, header=[0, 1], index_col=[0, 1])

    # Ensure price column is correctly named
    price_col = price_changes.columns[0]
    price_series = price_changes[price_col]

    result = pd.DataFrame(index=price_series.index)

    for region in regions:
        col = (region, "cpi_weight")
        if col not in cpi_weights.columns:
            raise ValueError(f"Region column {col} not found in CPI weights.")

        weights = cpi_weights[col].reindex(price_series.index).fillna(0.0)
        result[f"{region}"] = weights * price_series

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        result.to_csv(output_path)

    return result




