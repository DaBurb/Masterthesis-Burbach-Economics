import numpy as np
import pandas as pd
from pathlib import Path
import os

def run_imported_gas_shock(
    A_matrix: pd.DataFrame,
    eu28_countries: list,
    shock_factor: float = 5.0,
    intra_eu: bool = False,
    output_path: Path = None,
    debug: bool = False,
    debug_path: Path = None
) -> pd.DataFrame:
    """
    Runs the imported gas price shock simulation, and optionally writes out
    the P_X shock‐multiplier vector for debugging.

    Parameters:
        A_matrix (pd.DataFrame): IO coefficient matrix.
        eu28_countries (list): List of EU28 country codes.
        shock_factor (float): Is interpreted as relative price change, so 0.05 means a 5% increase, 5 means a 500% increase.
        intra_eu (bool): Whether to include intra-EU gas imports.
        output_path (Path): Optional path to save result CSV.
        debug (bool): If True, write out the raw P_X vector.
        debug_path (Path): Where to write P_X. If None, defaults to output_path.parent/"P_X_debug.csv".

    Returns:
        pd.DataFrame: Price change per (Country, Sector).
    """
    energy_sectors = ["B_gas"]
    A_matrix = A_matrix.copy()
    A_matrix.index.names  = ["Country", "Sector"]
    A_matrix.columns.names = ["Country", "Sector"]

    # Non‐energy and energy index tuples
    all_index = list(A_matrix.index)
    N_indices = [
        (c, sec) for c, sec in all_index
        if c in eu28_countries and sec not in energy_sectors
    ]
    E_indices = [
        (c, sec) for c, sec in all_index
        if sec in energy_sectors
    ]

    # Submatrices
    A_EE = A_matrix.loc[N_indices, N_indices].values
    A_XE = A_matrix.loc[E_indices, N_indices].values

    # Build Leontief
    I_EE = np.eye(A_EE.shape[0])
    try:
        L_EE = np.linalg.inv(I_EE - A_EE.T)
    except np.linalg.LinAlgError:
        raise ValueError("Singular matrix encountered. Cannot compute Leontief inverse.")

    P_X = np.zeros((A_XE.shape[0], 1))
    for i, (supplier, sec) in enumerate(E_indices):
        if sec=="B_gas" and supplier not in eu28_countries:
            P_X[i,0] = shock_factor
    
    if intra_eu:
        for i, (buyer,sec) in enumerate(E_indices):
            if sec=="B_gas" and buyer in eu28_countries:
                for j, (supplier,sec2) in enumerate(E_indices):
                    if sec2=="B_gas" and supplier in eu28_countries and supplier!=buyer:
                        P_X[j,0] = shock_factor

    # compute delta_P_E
    delta_P_E = L_EE @ (A_XE.T @ P_X)

    result_df = pd.DataFrame(
        delta_P_E.flatten(),
        index=pd.MultiIndex.from_tuples(N_indices, names=["Country", "Sector"]),
        columns=["Price Change"]
    )

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        result_df.to_csv(output_path)
        print(f"Shock impacts saved to {output_path}")

    return result_df

def simulate_extra_vs_full_gas_shock(
    A_matrix: pd.DataFrame,
    eu28_countries: list,
    shock_factor: float = 5.0,
    output_dir: Path = None
):
    """
    Run two gas‐shock scenarios on A_matrix:
      1) Extra‐EU imports only (zero out intra‐EU + domestic B_gas flows)
      2) Extra + intra‐EU imports (zero out only domestic B_gas flows)

    Parameters
    ----------
    A_matrix      : IO coeff matrix (MultiIndex rows & cols)
    eu28_countries: list of ISO codes in the EU‐28
    shock_factor  : float, the P_X shock multiplier (e.g. 6.0)
    output_dir    : Path or None. If given, saves CSVs named:
                    'results_extra.csv', 'results_full.csv', 'results_intra.csv'

    Returns
    -------
    df_extra, df_full, df_intra  : DataFrames with index (Country, Sector) and
                                   column 'Price Change'
    """
    # Prepare the two matrices
    A_extra = A_matrix.copy()
    A_full  = A_matrix.copy()

    # 1) Zero out domestic B_gas flows in A_full
    for c in eu28_countries:
        row = (c, "B_gas")
        if row not in A_full.index:
            continue
        cols_dom = [col for col in A_full.columns if col[0]==c]
        A_full.loc[row, cols_dom] = 0.0

    # 2) In A_extra also zero out *all* intra‐EU B_gas flows
    for supplier, sec in A_extra.index:
        if sec!="B_gas" or supplier not in eu28_countries:
            continue
        cols_eu = [col for col in A_extra.columns if col[0] in eu28_countries]
        A_extra.loc[(supplier,sec), cols_eu] = 0.0

    # Run the two scenarios
    df_extra = run_imported_gas_shock(
        A_extra, eu28_countries,
        shock_factor=shock_factor,
        intra_eu=False
    )
    df_full  = run_imported_gas_shock(
        A_full, eu28_countries,
        shock_factor=shock_factor,
        intra_eu=True
    )

    # Compute pure intra‐EU contribution
    df_intra = df_full.copy()
    df_intra["Price Change"] = df_full["Price Change"] - df_extra["Price Change"]

    # Optional: save to CSV
    if output_dir is not None:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        df_extra.to_csv(output_dir / "results_extra.csv")
        df_full.to_csv (output_dir / "results_full.csv")
        df_intra.to_csv(output_dir / "results_intra.csv")
        print("Saved shocks to", output_dir)

    return df_extra, df_full, df_intra


def extract_price_shocks_from_A(
    A_matrix: pd.DataFrame,
    eu28_countries: list,
    shock_factor: float,
    intra_eu: bool
) -> pd.DataFrame:
    """
    Reconstruct the price shock vector applied in run_imported_gas_shock.
    
    Returns a DataFrame indexed by (Country, Sector) with a 'price_volatility' column.
    """
    energy_sector = "B_gas"
    P_X = pd.Series(1.0, index=A_matrix.index)

    for (supplier_country, sector) in A_matrix.index:
        if sector != energy_sector:
            continue

        if supplier_country not in eu28_countries:
            # Extra-EU gas supplier
            P_X[(supplier_country, sector)] = shock_factor

    if intra_eu:
        for (buyer_country, _) in A_matrix.columns:
            if buyer_country not in eu28_countries:
                continue

            for (supplier_country, sector) in A_matrix.index:
                if sector == energy_sector and supplier_country in eu28_countries and supplier_country != buyer_country:
                    P_X[(supplier_country, sector)] = shock_factor

    # Keep only non-default shock entries
    P_X = P_X[P_X != 1.0].rename("price_volatility").to_frame()
    return P_X
