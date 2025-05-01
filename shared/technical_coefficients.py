import numpy as np
import pandas as pd

def calculate_technical_coefficients(Z: pd.DataFrame, X: pd.Series) -> pd.DataFrame:
    """
    Calculate the technical coefficients matrix A from interindustry flows Z and gross output vector X.
    Normalizes Z column-wise by X.
    
    If X_j = 0, sets the corresponding A column to 0.

    Parameters:
        Z (pd.DataFrame): Interindustry flow matrix with MultiIndex on both axes.
        X (pd.Series): Gross output vector with the same index as Z's columns.

    Returns:
        pd.DataFrame: Technical coefficients matrix A (same shape as Z).
    """
    if not Z.columns.equals(X.index):
        raise ValueError("Mismatch: Z.columns and X.index must be identical for division.")

    # Replace 0 in gross output with np.nan to prevent division error
    X_safe = X.replace(0, np.nan)

    # Column-wise division: A_ij = Z_ij / X_j
    A = Z.div(X_safe, axis=1)

    # After division: if X_j was 0, set entire column in A to 0
    zero_gross_output = X[X == 0].index
    A.loc[:, zero_gross_output] = 0

    return A
