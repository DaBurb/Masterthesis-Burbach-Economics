import pandas as pd

# This list must match the codes used in your final demand columns
FINAL_DEMAND_CODES = {"P3_S13", "P3_S14", "P3_S15", "P51G", "P5M"}
VALUE_ADDED_CODES = {"D21X31", "OP_RES", "OP_NRES", "D1", "D29X39", "B2A3G"}


def extract_Z_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts interindustry matrix Z, excluding final demand columns and
    value added or gross output rows. Assumes aggregation has been applied.
    """
    row_mask = ~df.index.get_level_values("Country").isin(["W2", "GO"])
    col_mask = (~df.columns.get_level_values("Sector").isin(FINAL_DEMAND_CODES)) & \
               (~df.columns.get_level_values("Country").isin(["W2"])) & \
               (~df.columns.get_level_values("Sector").str.contains("cpi_weight"))

    return df.loc[row_mask, col_mask]


def extract_Y_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts final demand matrix Y, based on known final demand sector codes.
    Assumes rows are industries and columns are (country, sector) pairs.
    """
    col_mask = df.columns.get_level_values("Sector").isin(FINAL_DEMAND_CODES)
    row_mask = ~df.index.get_level_values("Country").isin(["GO"])
    return df.loc[row_mask, col_mask]


def extract_X_vector(df: pd.DataFrame, final_demand_codes: set) -> pd.Series:
    """
    Extract the gross output vector (X), filtered to exclude final demand columns.

    Parameters:
        df (pd.DataFrame): Aggregated DataFrame with ('GO', 'GO') row and full column MultiIndex.
        final_demand_codes (set): Set of final demand sector codes to exclude.

    Returns:
        pd.Series: Gross output vector for industry sectors only.
    """
    go_row = df.loc[("GO", "GO")]
    industry_cols = [
        col for col in df.columns
        if col[1] not in final_demand_codes
    ]
    return go_row[industry_cols]

def extract_VA_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts the value added matrix (VA) using the W2 country marker for rows.

    Parameters:
        df (pd.DataFrame): MultiIndexed DataFrame.

    Returns:
        pd.DataFrame: Value added matrix filtered by Country == "W2".
    """
    return df[df.index.get_level_values("Country") == "W2"]