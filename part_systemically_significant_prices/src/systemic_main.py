# systemic_main.py

import sys
from pathlib import Path
import pandas as pd

# Extend sys.path to access config and shared modules
sys.path.append(str(Path(__file__).resolve().parents[2]))

from config import SYSTEMIC_PRICES_OUTPUTS, FIGARO_FULL_MATRIX_DIR,FIGARO_VA_MATRIX_DIR, FIGARO_X_VECTOR_DIR,FIGARO_Y_MATRIX_DIR, FIGARO_Z_MATRIX_DIR, FIGARO_A_MATRIX_DIR
from shared.data_loader import load_figaro_processed
from sea_loader import download_sea_file
from sea_processing import process_sea_ii_volatility
from figaro_preprocessing import aggregate_sectors, add_cpi_weights
from technical_coefficients import (
    extract_interindustry_matrix,
    extract_gross_output,
    calculate_technical_coefficients,
    extract_final_demand_matrix
)


def main():
    print("=== Systemically Significant Prices: Full Pipeline ===")

    # Step 1: Ensure SEA data is downloaded and processed
    download_sea_file()
    sea_vol_df = process_sea_ii_volatility()
    sea_vol_df.to_csv(SYSTEMIC_PRICES_OUTPUTS / "II_PI_volatility.csv")

    # Step 2: Identify all processed FIGARO years
    year_files = FIGARO_FULL_MATRIX_DIR.glob("figaro_matrix_*.csv")
    available_years = sorted({
        int(f.stem.split("_")[-1]) for f in year_files
        if f.stem.split("_")[-1].isdigit()
    })

    if not available_years:
        raise RuntimeError("No processed FIGARO files found in the expected directory.")

    # Step 3: Load all years from processed FIGARO
    figaro_data = load_figaro_processed(available_years)

    for year in available_years:
        print(f"\n--- Processing FIGARO year: {year} ---")
        df = figaro_data[year]

        # Step 4: Sector aggregation (systemic-specific)
        df = aggregate_sectors(df)

        # Step 5: Add CPI weights per country
        df = add_cpi_weights(df)

        # Step 6: Extract matrices
        Z = extract_interindustry_matrix(df)
        X = extract_gross_output(df)
        A = calculate_technical_coefficients(Z, X)
        Y = extract_final_demand_matrix(df)

        # Step 7: Save results
        df.to_csv(FIGARO_FULL_MATRIX_DIR / f"figaro_aggregated_with_cpi_{year}.csv")
        Z.to_csv(FIGARO_Z_MATRIX_DIR / f"Z_{year}.csv")
        A.to_csv(FIGARO_A_MATRIX_DIR / f"A_{year}.csv")
        X.to_frame(name="gross_output").to_csv(FIGARO_X_VECTOR_DIR / f"X_{year}.csv")
        Y.to_csv(FIGARO_Y_MATRIX_DIR / f"Y_{year}.csv")


    print("\n=== All years processed successfully ===")


if __name__ == "__main__":
    main()
