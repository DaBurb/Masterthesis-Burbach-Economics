import sys
from pathlib import Path

# Extend sys.path to access config and shared modules
sys.path.append(str(Path(__file__).resolve().parents[2]))

import pandas as pd
import numpy as np
from tqdm import tqdm
from scipy.linalg import lu_factor, lu_solve

from config import (
    SYSTEMIC_PRICES_OUTPUTS,
    FIGARO_A_MATRIX_DIR,
    SYSTEMIC_UNWEIGHTED_IMPACTS_DIR,
)

def compute_unweighted_shocks(A: pd.DataFrame, year: int):
    
    # Load price volatility
    vol_path = SYSTEMIC_PRICES_OUTPUTS / "II_PI_volatility.csv"
    price_vol = pd.read_csv(vol_path, index_col=[0, 1])

    impacts = []

    # Prepare set for faster lookup
    available_sectors = set(A.index)

    # Initialize tqdm over price_vol index
    for sector in tqdm(price_vol.index, desc=f"Computing unweighted shocks {year}", ncols=100):
        exog_country, exog_sector = sector

        # Early skip: sector-country pair not found
        if (exog_country, exog_sector) not in available_sectors:
            continue

        shock = price_vol.loc[sector, "price_volatility"]

        # Early skip: no volatility
        if shock == 0:
            continue

        # Create masks for dropping the exogenous sector
        row_mask = ~((A.index.get_level_values("Country") == exog_country) &
                     (A.index.get_level_values("Sector") == exog_sector))
        col_mask = ~((A.columns.get_level_values("Country") == exog_country) &
                     (A.columns.get_level_values("Sector") == exog_sector))

        # Build endogenous system
        A_EE = A.loc[row_mask, col_mask].T  # Transpose to match A'

        # Define exogenous column mask (single sector)
        exog_col_mask = (
            (A.columns.get_level_values("Country") == exog_country) &
            (A.columns.get_level_values("Sector") == exog_sector)
        )

        A_XE = A.loc[row_mask, exog_col_mask].T  # Transpose to match A'

        # Ensure correct matrix shapes
        A_XE = A_XE.sum(axis=0).values.reshape(-1, 1)


        I = np.eye(A_EE.shape[0])

        try:
            A_EE_values = I - A_EE.values

            if np.isnan(A_EE_values).any() or np.isinf(A_EE_values).any():
                print(f"Skipping {sector}: matrix contains NaN or Inf")
                continue

            lu, piv = lu_factor(A_EE_values)
            dP = lu_solve((lu, piv), A_XE * shock)

        except np.linalg.LinAlgError:
            print(f"Skipping {sector}: singular matrix")
            continue


        impacts.append(pd.Series(dP.flatten(), index=A_EE.index, name=(exog_country, exog_sector)))

    # Combine results
    if impacts:
        df_out = pd.DataFrame(impacts)
        df_out = df_out.sort_index(axis=0).sort_index(axis=1)
    else:
        df_out = pd.DataFrame()

    # Save
    out_path = SYSTEMIC_UNWEIGHTED_IMPACTS_DIR / f"unweighted_shock_impacts_{year}.csv"
    df_out.to_csv(out_path)
    print(f"\n Saved unweighted shock impact matrix for {year} to {out_path}")
