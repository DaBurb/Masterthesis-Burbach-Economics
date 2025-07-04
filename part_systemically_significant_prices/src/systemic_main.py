# part_systemically_significant_prices/src/systemic_main.py

import sys
from pathlib import Path
import pandas as pd

# Extend sys.path to access config and shared modules
sys.path.append(str(Path(__file__).resolve().parents[2]))

from config import (
    SYSTEMIC_PRICES_OUTPUTS, SYSTEMIC_PRICES_DATA,
    FIGARO_FULL_MATRIX_DIR, SYSTEMIC_FULL_MATRIX_DIR,
    SYSTEMIC_Z_MATRIX_DIR, SYSTEMIC_A_MATRIX_DIR, SYSTEMIC_X_VECTOR_DIR, SYSTEMIC_Y_MATRIX_DIR, SYSTEMIC_CPI_WEIGHTS_DIR,
    SYSTEMIC_UNWEIGHTED_IMPACTS_DIR, SYSTEMIC_WEIGHTED_IMPACTS_DIR,
    EU28_COUNTRIES, IPSEN_REGION_MAP, EU_NORTH_SOUTH_MAP, EU_WEST_EAST_MAP, CLUSTER_REGION_MAP_2019
)

from shared.data_loader import load_figaro_processed
from shared.technical_coefficients import (
    calculate_technical_coefficients,
)
from shared.aggregation import aggregate_sectors
from shared.cpi_weights import calculate_cpi_weights, new_apply_all_available_cpi_weights
from shared.extraction import extract_Z_matrix, extract_X_vector, extract_Y_matrix, extract_VA_matrix
from shared.preprocessing import add_gross_output_row
from sea_loader import download_sea_file
from sea_processing import process_sea_ii_volatility
from analyze_unweighted_shocks import compute_unweighted_shocks
from visualization import plot_systemic_volatility_scatter



# Aggregation mapping used in this part
AGGREGATION_MAPPING_FIGARO_SYSTEMIC = {
    "N77": "N", "N78": "N", "N79": "N", "N80-N82": "N",
    "Q86": "Q", "Q87_Q88": "Q",
    "R90-R92": "R_S", "R93": "R_S", "S94": "R_S", "S95": "R_S", "S96": "R_S"
}

FINAL_DEMAND_CODES = {
    "P3_S13", "P3_S14", "P3_S15", "P51G", "P5M",
}


def main():
    print("=== Systemically Significant Prices: Full Pipeline ===")

    # Step 1: Download and process WIOD SEA volatility data
    download_sea_file()
    sea_vol_df = process_sea_ii_volatility()
    sea_vol_df.to_csv(SYSTEMIC_PRICES_OUTPUTS / "volatility" / "II_PI_volatility.csv")

    # Step 2: Detect available preprocessed FIGARO matrices
    year_files = FIGARO_FULL_MATRIX_DIR.glob("figaro_matrix_*.csv")
    available_years = sorted({
        int(f.stem.split("_")[-1]) for f in year_files if f.stem.split("_")[-1].isdigit()
    })

    if not available_years:
        raise RuntimeError("No processed FIGARO files found.")

    # Step 4: Load all full matrices
    figaro_data = load_figaro_processed(available_years)

    for year in available_years:
        print(f"\n--- Processing FIGARO year: {year} ---")
        df = figaro_data[year]

        # Step 5: Sector aggregation (systemic-specific)
        df = aggregate_sectors(df, AGGREGATION_MAPPING_FIGARO_SYSTEMIC)

        # Fix missing MultiIndex level names (due to CSV reload or pandas transformations)
        df.index.names = ["Country", "Sector"]
        df.columns.names = ["Country", "Sector"]

        # Make sure df.index is really a MultiIndex with correct names
        if not isinstance(df.index, pd.MultiIndex):
            print("Rebuilding index as MultiIndex manually.")
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

        # Step 8b: CPI weights (aggregated sectors)
        print(f"Calculating CPI weights for {year}...")

        REGION_MAP_EU28 = {c: "EU28" for c in EU28_COUNTRIES}

        calculate_cpi_weights(df, output_path=SYSTEMIC_CPI_WEIGHTS_DIR / "individual", filename=f"cpi_weights_individual_{year}.csv")
        calculate_cpi_weights(df, region_map=REGION_MAP_EU28, output_path=SYSTEMIC_CPI_WEIGHTS_DIR / "eu28", filename=f"cpi_weights_eu28_{year}.csv")
        calculate_cpi_weights(df, region_map=IPSEN_REGION_MAP, output_path=SYSTEMIC_CPI_WEIGHTS_DIR / "ipsen", filename=f"cpi_weights_ipsen_{year}.csv")
        calculate_cpi_weights(df, region_map=EU_NORTH_SOUTH_MAP, output_path=SYSTEMIC_CPI_WEIGHTS_DIR / "north_south", filename=f"cpi_weights_north_south_{year}.csv")
        calculate_cpi_weights(df, region_map=EU_WEST_EAST_MAP, output_path=SYSTEMIC_CPI_WEIGHTS_DIR / "west_east", filename=f"cpi_weights_west_east_{year}.csv")
        calculate_cpi_weights(df, region_map=CLUSTER_REGION_MAP_2019, output_path=SYSTEMIC_CPI_WEIGHTS_DIR / "cluster", filename=f"cpi_weights_cluster_{year}.csv")


        # Step 9: Calculate unweighted shock impacts (only if not yet saved)
        unweighted_path = SYSTEMIC_UNWEIGHTED_IMPACTS_DIR / f"unweighted_shock_impacts_{year}.csv"

        if unweighted_path.exists():
            print(f"Skipping unweighted shocks for {year} (already exists).")
        else:
            print(f"Calculating unweighted shocks for {year} ...")
            compute_unweighted_shocks(A, year)

        # Step 10: Apply CPI weights to compute weighted impacts
        WEIGHT_SCENARIOS = {
            "individual": SYSTEMIC_CPI_WEIGHTS_DIR / "individual" / f"cpi_weights_individual_{year}.csv",
            "eu28": SYSTEMIC_CPI_WEIGHTS_DIR / "eu28" / f"cpi_weights_eu28_{year}.csv",
            "ipsen": SYSTEMIC_CPI_WEIGHTS_DIR / "ipsen" / f"cpi_weights_ipsen_{year}.csv",
            "north_south": SYSTEMIC_CPI_WEIGHTS_DIR / "north_south" / f"cpi_weights_north_south_{year}.csv",
            "west_east": SYSTEMIC_CPI_WEIGHTS_DIR / "west_east" / f"cpi_weights_west_east_{year}.csv",
            "cluster": SYSTEMIC_CPI_WEIGHTS_DIR / "cluster" / f"cpi_weights_cluster_{year}.csv"
        }

        new_apply_all_available_cpi_weights(
            year=year,
            unweighted_impacts_path=SYSTEMIC_UNWEIGHTED_IMPACTS_DIR / f"unweighted_shock_impacts_{year}.csv",
            price_volatility_path=SYSTEMIC_PRICES_OUTPUTS / "volatility" / "II_PI_volatility.csv",
            cpi_weights_root=SYSTEMIC_CPI_WEIGHTS_DIR,
            output_dir=SYSTEMIC_WEIGHTED_IMPACTS_DIR,
            output_prefix="weighted_impacts"
        )


    print("\n=== All FIGARO years processed successfully ===")


if __name__ == "__main__":
    main()
