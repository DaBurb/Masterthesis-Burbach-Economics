import numpy as np
import pandas as pd


def extract_gross_output(df: pd.DataFrame) -> pd.Series:
    """
    Extract the gross output row labeled ('GO', 'GO') from a MultiIndexed DataFrame.

    Parameters:
        df (pd.DataFrame): Input-output DataFrame with MultiIndex on rows and columns.

    Returns:
        pd.Series: Gross output vector (column-wise sums).
    """
    if ('GO', 'GO') not in df.index:
        raise ValueError("Expected gross output row ('GO', 'GO') not found in input data.")

    return df.loc[('GO', 'GO')]


def calculate_technical_coefficients(Z: pd.DataFrame, X: pd.Series) -> pd.DataFrame:
    """
    Compute the technical coefficients matrix A = Z / X,
    where Z is the interindustry flow matrix and X is the gross output vector.

    Parameters:
        Z (pd.DataFrame): Interindustry matrix with MultiIndex on rows and columns.
        X (pd.Series): Gross output vector (Series with same column structure as Z).

    Returns:
        pd.DataFrame: Technical coefficient matrix A.
    """
    if not Z.columns.equals(X.index):
        raise ValueError("Column indices of Z and index of X do not match.")

    X_safe = X.replace(0, np.nan)
    A_values = Z.div(X_safe, axis=1)
    return A_values

def extract_final_demand_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract the final demand matrix (Y) by selecting all columns not part of the interindustry quadrant.

    Parameters:
        df (pd.DataFrame): FIGARO DataFrame with MultiIndex.

    Returns:
        pd.DataFrame: Final demand matrix (Y).
    """
    num_industries = df.index.get_level_values("Sector").nunique()
    interindustry_cols = df.columns.get_level_values("Sector").isin(df.index.get_level_values("Sector").unique())
    return df.loc[df.index.drop(("GO", "GO"), errors="ignore"), ~interindustry_cols]

def extract_interindustry_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract the interindustry matrix Z from the full price table,
    excluding the ('GO', 'GO') row.

    Parameters:
        df (pd.DataFrame): Full input-output matrix including gross output.

    Returns:
        pd.DataFrame: Interindustry matrix (Z).
    """
    return df.drop(index=('GO', 'GO'), errors='ignore')
