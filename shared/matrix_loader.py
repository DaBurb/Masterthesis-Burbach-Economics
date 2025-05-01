import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))  # Adjust the path to include the parent directory

import pandas as pd
from config import (
    FIGARO_A_MATRIX_DIR,
    FIGARO_X_VECTOR_DIR,
    FIGARO_Y_MATRIX_DIR,
    FIGARO_Z_MATRIX_DIR,
    FIGARO_VA_MATRIX_DIR,
)

def load_A_matrix(year: int) -> pd.DataFrame:
    """
    Load the technical coefficient matrix A for a given year.

    Parameters:
        year (int): Year of the matrix.

    Returns:
        pd.DataFrame: A matrix with MultiIndex (Country, Sector) for both rows and columns.
    """
    path = FIGARO_A_MATRIX_DIR / f"A_{year}.csv"
    return pd.read_csv(path, index_col=[0, 1], header=[0, 1])


def load_X_vector(year: int) -> pd.Series:
    """
    Load the gross output vector X for a given year.

    Parameters:
        year (int): Year of the vector.

    Returns:
        pd.Series: X vector indexed by (Country, Sector).
    """
    path = FIGARO_X_VECTOR_DIR / f"X_{year}.csv"
    df = pd.read_csv(path, index_col=[0, 1])
    return df["gross_output"]


def load_Y_matrix(year: int) -> pd.DataFrame:
    """
    Load the final demand matrix Y for a given year.

    Parameters:
        year (int): Year of the matrix.

    Returns:
        pd.DataFrame: Y matrix with MultiIndex (Country, Sector).
    """
    path = FIGARO_Y_MATRIX_DIR / f"Y_{year}.csv"
    return pd.read_csv(path, index_col=[0, 1], header=[0, 1])


def load_Z_matrix(year: int) -> pd.DataFrame:
    """
    Load the interindustry flow matrix Z for a given year.

    Parameters:
        year (int): Year of the matrix.

    Returns:
        pd.DataFrame: Z matrix with MultiIndex (Country, Sector).
    """
    path = FIGARO_Z_MATRIX_DIR / f"Z_{year}.csv"
    return pd.read_csv(path, index_col=[0, 1], header=[0, 1])


def load_VA_matrix(year: int) -> pd.DataFrame:
    """
    Load the value added matrix VA for a given year.

    Parameters:
        year (int): Year of the matrix.

    Returns:
        pd.DataFrame: VA matrix with MultiIndex (Country, Sector).
    """
    path = FIGARO_VA_MATRIX_DIR / f"VA_{year}.csv"
    return pd.read_csv(path, index_col=[0, 1])
