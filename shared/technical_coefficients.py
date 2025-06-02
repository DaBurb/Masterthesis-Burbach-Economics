import numpy as np
import pandas as pd

def calculate_technical_coefficients(Z: pd.DataFrame, X: pd.Series) -> pd.DataFrame:
    """
    Calculate the technical coefficients matrix A = Z / X,
    where each column j is divided by X_j.
    
    If X_j = 0, the entire column j in A is set to 0.

    Parameters:
        Z (pd.DataFrame): Interindustry flow matrix with MultiIndex columns and rows.
        X (pd.Series): Gross output vector with the same index as Z.columns.

    Returns:
        pd.DataFrame: Technical coefficients matrix A.
    """
    if not Z.columns.equals(X.index):
        raise ValueError("Mismatch: Z.columns and X.index must be identical.")

    A = Z.copy()

    for col in Z.columns:
        x_val = X[col]
        if x_val == 0 or np.isclose(x_val, 0.0):
            A[col] = 0.0
        else:
            A[col] = Z[col] / x_val

    # Final cleanup to ensure no NaNs
    A = A.fillna(0.0)

    return A
