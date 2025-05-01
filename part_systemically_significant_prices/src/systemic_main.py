# part_systemically_significant_prices/src/systemic_main.py

import sys
from pathlib import Path
import pandas as pd

# Extend sys.path to access config and shared modules
sys.path.append(str(Path(__file__).resolve().parents[2]))

from config import (
    SYSTEMIC_PRICES_OUTPUTS, SYSTEMIC_PRICES_DATA,
    FIGARO_FULL_MATRIX_DIR, SYSTEMIC_FULL_MATRIX_DIR,
    SYSTEMIC_Z_MATRIX_DIR, SYSTEMIC_A_MATRIX_DIR, SYSTEMIC_X_VECTOR_DIR, SYSTEMIC_Y_MATRIX_DIR, SYSTEMIC_CPI_WEIGHTS_DIR
)

from shared.data_loader import load_figaro_processed
from shared.technical_coefficients import (
    calculate_technical_coefficients,
)
from shared.aggregation import aggregate_sectors
from shared.cpi_weights import calculate_cpi_weights
from shared.extraction import extract_Z_matrix, extract_X_vector, extract_Y_matrix, extract_VA_matrix
from shared.preprocessing import add_gross_output_row
from sea_loader import download_sea_file
from sea_processing import process_sea_ii_volatility
from analyze_unweighted_shocks import compute_unweighted_shocks



# Aggregation mapping used in this part
AGGREGATION_MAPPING_FIGARO_SYSTEMIC = {
    "N77": "N", "N78": "N", "N79": "N", "N80-N82": "N",
    "Q86": "Q", "Q87_Q88": "Q",
    "R90-R92": "R_S", "R93": "R_S", "S94": "R_S", "S95": "R_S", "S96": "R_S"
}

FINAL_DEMAND_CODES = [
    "P3_S13", "P3_S14", "P3_S15", "P51G", "P5M",
    "P3_S1", "P3_S2", "P3_S3", "P3_S4", "P3_S5",
    "P3_S6", "P3_S7", "P3_S8", "P3_S9", "P3_S10",
    "P3_S11", "P3_S12"
]


def main():
    print("=== Systemically Significant Prices: Full Pipeline ===")

    # Step 1: Download and process WIOD SEA volatility data
    download_sea_file()
    sea_vol_df = process_sea_ii_volatility()
    sea_vol_df.to_csv(SYSTEMIC_PRICES_OUTPUTS / "II_PI_volatility.csv")

    # Step 2: Detect available preprocessed FIGARO matrices
    year_files = FIGARO_FULL_MATRIX_DIR.glob("figaro_matrix_*.csv")
    available_years = sorted({
        int(f.stem.split("_")[-1]) for f in year_files if f.stem.split("_")[-1].isdigit()
    })

    if not available_years:
        raise RuntimeError("No processed FIGARO files found.")

    # Step 3: Load all full matrices
    figaro_data = load_figaro_processed(available_years)

    for year in available_years:
        print(f"\n--- Processing FIGARO year: {year} ---")
        df = figaro_data[year]

        # Step 4: Sector aggregation (systemic-specific)
        aggregated_path = SYSTEMIC_PRICES_DATA / f"figaro_aggregated_{year}.csv"
        df = aggregate_sectors(df, AGGREGATION_MAPPING_FIGARO_SYSTEMIC, output_path=aggregated_path)

        from shared.preprocessing import add_gross_output_row

        # Fix missing MultiIndex level names (due to CSV reload or pandas transformations)
        df.index.names = ["Country", "Sector"]
        df.columns.names = ["Country", "Sector"]

        # Step 5a: Individual country CPI weights
        df_cpi_weights_individual = calculate_cpi_weights(df)
        df_cpi_weights_individual.to_csv(SYSTEMIC_CPI_WEIGHTS_DIR / f"cpi_weights_individual_{year}.csv")

        # Step 5b: EU28 region CPI weights
        EU28_COUNTRIES = {
            "AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "EL", "ES", "FI", "FR",
            "HR", "HU", "IE", "IT", "LT", "LU", "LV", "MT", "NL", "PL", "PT", "RO",
            "SE", "SI", "SK", "GB"
        }
        region_map_eu28 = {c: "EU28" for c in EU28_COUNTRIES}

        df_cpi_weights_eu28 = calculate_cpi_weights(df, region_map=region_map_eu28)
        df_cpi_weights_eu28.to_csv(SYSTEMIC_CPI_WEIGHTS_DIR / f"cpi_weights_eu28_{year}.csv")


        # Make sure df.index is really a MultiIndex with correct names
        if not isinstance(df.index, pd.MultiIndex):
            print("⚠️ Rebuilding index as MultiIndex manually.")
            df.index = pd.MultiIndex.from_tuples(df.index, names=["Country", "Sector"])

        df.index.names = ["Country", "Sector"]  # Reinforce
        df.columns.names = ["Country", "Sector"]


        # Ensure the DataFrame is sorted
        df = df.sort_index()

        # Step 6: Extract matrices
        Z = extract_Z_matrix(df)
        X = extract_X_vector(df, FINAL_DEMAND_CODES)
        Y = extract_Y_matrix(df)
        VA = extract_VA_matrix(df)
        A = calculate_technical_coefficients(Z, X)

        # Step 7: Finalize MultiIndex level names before saving
        df.index.names = ["Country", "Sector"]
        df.columns.names = ["Country", "Sector"]
        Z.index.names = ["Country", "Sector"]
        Z.columns.names = ["Country", "Sector"]
        A.index.names = ["Country", "Sector"]
        A.columns.names = ["Country", "Sector"]
        X.index.names = ["Country", "Sector"]
        Y.index.names = ["Country", "Sector"]
        Y.columns.names = ["Country", "Sector"]

        # Step 8: Save outputs
        df.to_csv(SYSTEMIC_FULL_MATRIX_DIR / f"figaro_aggregated_{year}.csv")
        Z.to_csv(SYSTEMIC_Z_MATRIX_DIR / f"Z_{year}.csv")
        A.to_csv(SYSTEMIC_A_MATRIX_DIR / f"A_{year}.csv")
        X.to_frame(name="gross_output").to_csv(SYSTEMIC_X_VECTOR_DIR / f"X_{year}.csv")
        Y.to_csv(SYSTEMIC_Y_MATRIX_DIR / f"Y_{year}.csv")

        # Step 9: Calculate unweighted shock impacts
        compute_unweighted_shocks(A, year)

    print("\n=== All FIGARO years processed successfully ===")


if __name__ == "__main__":
    main()
