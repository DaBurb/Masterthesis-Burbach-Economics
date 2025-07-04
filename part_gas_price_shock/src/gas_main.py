# part_gas_price_shock/src/2_gas_main.py

import pandas as pd
from pathlib import Path
import sys

# Extend path to root to access config.py and shared modules
sys.path.append(str(Path(__file__).resolve().parents[2]))

from config import (
    EXIOBASE_PROCESSED_DIR,
    FIGARO_Z_MATRIX_DIR,
    FIGARO_Y_MATRIX_DIR,
    FIGARO_X_VECTOR_DIR,
    GAS_PRICE_SHOCK_OUTPUTS,
    GAS_FIGARO_MAPPING,
    GAS_PRICE_SHOCK_DATA,
    EU28_COUNTRIES    
)

from exiobase3_loader import load_and_process_exiobase
from b_sector_split import compute_b_gas_share_matrix, split_b_sector, apply_b_gas_weights, merge_countries
from shared.aggregation import aggregate_sectors, aggregate_output_vector
from shared.cpi_weights import calculate_cpi_weights
from shared.technical_coefficients import calculate_technical_coefficients
from cpi_weights import split_b_sector_rows_for_final_demand, compute_origin_specific_b_gas_shares, apply_b_gas_shares_to_Y, apply_cpi_weights_to_gas_price_shock
from shock_analysis import run_imported_gas_shock, simulate_extra_vs_full_gas_shock

# === Parameters === 
YEAR = 2021
figaro_Z_path = FIGARO_Z_MATRIX_DIR / f"Z_{YEAR}.csv"
figaro_X_path = FIGARO_X_VECTOR_DIR / f"X_{YEAR}.csv"
figaro_Y_path = FIGARO_Y_MATRIX_DIR / f"Y_{YEAR}.csv"
output_path_A_gas = GAS_PRICE_SHOCK_DATA  / "processed" / f"A_gas_{YEAR}.csv"
output_path_results = GAS_PRICE_SHOCK_OUTPUTS / f"results_{YEAR}.csv"

# === Load and aggregate FIGARO data ===
df_figaro_Z = pd.read_csv(figaro_Z_path, header=[0, 1], index_col=[0, 1])
df_figaro_Z = aggregate_sectors(df_figaro_Z, GAS_FIGARO_MAPPING, output_path=GAS_PRICE_SHOCK_DATA / "processed" / f"Z_aggregated_{YEAR}.csv")
df_figaro_Z = merge_countries(df_figaro_Z, countries_to_merge=["AR", "SA"], target="FIGW1")

df_figaro_X = pd.read_csv(
    figaro_X_path,
    index_col=["Country", "Sector"],  # index on those two columns
    dtype={"gross_output": float}
)

# exclude unwanted final-demand sectors
exclude_sectors = {"P3_S13","P3_S14","P3_S15","P51G","P5M"}
df_figaro_X = df_figaro_X[
    ~df_figaro_X.index.get_level_values("Sector").isin(exclude_sectors)
]

X_agg = aggregate_output_vector(
    df_figaro_X,
    sector_map=GAS_FIGARO_MAPPING,
    country_merge_map={"AR": "FIGW1", "SA": "FIGW1"}
)

# when writing a Series with a 2-level index, explicitly pass index_label
X_agg.to_csv(
    GAS_PRICE_SHOCK_DATA / f"X_aggregated_{YEAR}.csv",
    index_label=["Country", "Sector"]
)

# === Calculate technical coefficients matrix A from Z matrix ===
df_figaro_A = calculate_technical_coefficients(df_figaro_Z, X_agg)
df_figaro_A.index.names = ["Country", "Sector"]
df_figaro_A.columns.names = ["Country", "Sector"]
df_figaro_A.to_csv(GAS_PRICE_SHOCK_DATA / "processed" / f"A_{YEAR}.csv")
# Split B_gas and B_nongas rows/columns in FIGARO A matrix
df_figaro_split_A = split_b_sector(df_figaro_A)

print("Figaro A matrix loaded and processed. Shape:", df_figaro_split_A.shape)

# === Split B_gas and B_nongas rows/columns in FIGARO Z matrix ===
df_figaro_split_Z = split_b_sector(df_figaro_Z)
df_figaro_split_Z.index.names = ["Country", "Sector"]
df_figaro_split_Z.columns.names = ["Country", "Sector"]
df_figaro_split_Z.to_csv(GAS_PRICE_SHOCK_DATA / "processed" / f"Z_split_{YEAR}.csv")

print("Figaro Z matrix split into B_gas and B_nongas. Shape:", df_figaro_split_Z.shape)

# === Load and preprocess EXIOBASE Z and Y matrix ===
z_matrix_path, y_matrix_path = load_and_process_exiobase(YEAR)
df_exio_z = pd.read_csv(z_matrix_path, header=[0, 1], index_col=[0, 1])
df_exio_z.index.names = ["Country", "Sector"]
df_exio_z.columns.names = ["Country", "Sector"]

# === Compute gas share matrix from EXIOBASE ===
gas_share_matrix = compute_b_gas_share_matrix(df_exio_z)
gas_share_matrix.to_csv(GAS_PRICE_SHOCK_DATA /"processed" / "gas_share_matrix.csv")

print("Gas share matrix computed. Shape:", gas_share_matrix.shape)

# === Apply gas share weights to B_gas and B_nongas rows/columns ===
A_weighted = apply_b_gas_weights(df_figaro_split_A, gas_share_matrix)
A_weighted.to_csv(GAS_PRICE_SHOCK_DATA/ "processed" / f"A_gas_weighted_{YEAR}.csv")

print(A_weighted.head())

Z_weighted = apply_b_gas_weights(df_figaro_split_Z, gas_share_matrix)
Z_weighted.to_csv(GAS_PRICE_SHOCK_DATA / "processed" / f"Z_gas_weighted_{YEAR}.csv")

print(Z_weighted.head())

# === Run gas price shock analysis ===

# Results with domestic gas sector shocked
results_extra = run_imported_gas_shock(
    A_matrix=A_weighted,
    eu28_countries=EU28_COUNTRIES,
    shock_factor=5.0,
    intra_eu=False,
    output_path=GAS_PRICE_SHOCK_OUTPUTS / "results_extra_2021.csv",
    debug=True
)

results_intra_extra = run_imported_gas_shock(
    A_matrix=A_weighted,
    eu28_countries=EU28_COUNTRIES,
    shock_factor=5.0,
    intra_eu=True,
    output_path=GAS_PRICE_SHOCK_OUTPUTS / "results_intra_extra_2021.csv",
    debug=True
)

# Results with only imported gas sectors shocked
df_e, df_f, df_i = simulate_extra_vs_full_gas_shock(
    A_matrix=A_weighted,
    eu28_countries=EU28_COUNTRIES,
    shock_factor=5.0,
    output_dir=GAS_PRICE_SHOCK_OUTPUTS / "extra_vs_full_2021"
)

print("Gas price shock analysis completed.")

# === Calculate CPI weights ===

# === Load EXIOBASE demand matrix for CPI calculation ===
df_exio_Y = pd.read_csv(y_matrix_path, header=[0, 1], index_col=[0, 1])
df_exio_Y.index.names = ["Country", "Sector"]
df_exio_Y.columns.names = ["Country", "Sector"]

print(df_exio_Y)

# === Load and aggregate FIGARO data ===
df_figaro_Y = pd.read_csv(figaro_Y_path, header=[0, 1], index_col=[0, 1])
df_figaro_Y = aggregate_sectors(df_figaro_Y, GAS_FIGARO_MAPPING)
df_figaro_Y = merge_countries(df_figaro_Y, countries_to_merge=["AR", "SA"], target="FIGW1")
df_figaro_Y.index.names = ["Country", "Sector"]
df_figaro_Y.columns.names = ["Country", "Sector"]

print(df_figaro_Y.head())

# === Add B_gas and B_nongas rows to FIGARO Y matrix ===
figaro_Y_split = split_b_sector_rows_for_final_demand(df_figaro_Y, target_category="P3_S14")

print(figaro_Y_split.head())

# === Calculate shares for gas and non-gas sectors ===
gas_nongas_shares = compute_origin_specific_b_gas_shares(df_exio_Y, target_category="Final consumption expenditure by households")
gas_nongas_shares.to_csv(GAS_PRICE_SHOCK_DATA / "gas_nongas_shares.csv")

# === Apply Shares to FIGARO Y matrix ===
figaro_Y_gas = apply_b_gas_shares_to_Y(figaro_Y_split, gas_nongas_shares)
figaro_Y_gas.to_csv(GAS_PRICE_SHOCK_DATA / "processed" / f"Y_gas_{YEAR}.csv")


# === Calculate CPI weights for EU28 region ===
EU28_TAG = "eu28"
eu28_region_map = {country: "EU28" for country in EU28_COUNTRIES}
eu28_output_dir = GAS_PRICE_SHOCK_DATA / "cpi_weights" / EU28_TAG

cpi_weights_eu28 = calculate_cpi_weights(
    df=figaro_Y_gas,
    consumption_code="P3_S14",
    region_map=eu28_region_map,
    output_path=eu28_output_dir,
    filename=f"cpi_weights_{EU28_TAG}_{YEAR}.csv"
)

print(f"CPI weights for EU28 saved to {eu28_output_dir}")

# === Apply EU28 CPI weights ===

apply_cpi_weights_to_gas_price_shock(
    price_change_path=GAS_PRICE_SHOCK_OUTPUTS / "extra_vs_full_2021" / "results_extra.csv",
    cpi_weights_path=GAS_PRICE_SHOCK_DATA / "cpi_weights" / "eu28" / "cpi_weights_eu28_2021.csv",
    regions=["EU28", "ROW"],
    output_path=GAS_PRICE_SHOCK_OUTPUTS / "weighted_impacts" / "extra_cpi_applied_total_impact_eu28.csv"
)

apply_cpi_weights_to_gas_price_shock(
    price_change_path=GAS_PRICE_SHOCK_OUTPUTS / "extra_vs_full_2021" / "results_full.csv",
    cpi_weights_path=GAS_PRICE_SHOCK_DATA / "cpi_weights" / "eu28" / "cpi_weights_eu28_2021.csv",
    regions=["EU28", "ROW"],
    output_path=GAS_PRICE_SHOCK_OUTPUTS / "weighted_impacts" / "full_cpi_applied_total_impact_eu28.csv"
)

apply_cpi_weights_to_gas_price_shock(
    price_change_path=GAS_PRICE_SHOCK_OUTPUTS / "extra_vs_full_2021" / "results_intra.csv",
    cpi_weights_path=GAS_PRICE_SHOCK_DATA / "cpi_weights" / "eu28" / "cpi_weights_eu28_2021.csv",
    regions=["EU28", "ROW"],
    output_path=GAS_PRICE_SHOCK_OUTPUTS / "weighted_impacts" / "intra_cpi_applied_total_impact_eu28.csv"
)

apply_cpi_weights_to_gas_price_shock(
    price_change_path=GAS_PRICE_SHOCK_OUTPUTS / "results_extra_2021.csv",
    cpi_weights_path=GAS_PRICE_SHOCK_DATA / "cpi_weights" / "eu28" / "cpi_weights_eu28_2021.csv",
    regions=["EU28","ROW"],
    output_path=GAS_PRICE_SHOCK_OUTPUTS / "weighted_impacts" / "cpi_applied_total_impact_eu28_extra.csv"
)

apply_cpi_weights_to_gas_price_shock(
    price_change_path=GAS_PRICE_SHOCK_OUTPUTS / "results_intra_extra_2021.csv",
    cpi_weights_path=GAS_PRICE_SHOCK_DATA / "cpi_weights" / "eu28" / "cpi_weights_eu28_2021.csv",
    regions=["EU28", "ROW"],
    output_path=GAS_PRICE_SHOCK_OUTPUTS / "weighted_impacts" / "cpi_applied_total_impact_eu28_intra_extra.csv"
)


# === Compute country‐level CPI weights ===
country_tag    = "per_country"
country_outdir = GAS_PRICE_SHOCK_DATA / "cpi_weights" / country_tag

# region_map=None ⇒ one CPI‐weight column per country
cpi_weights_country = calculate_cpi_weights(
    df=figaro_Y_gas,
    consumption_code="P3_S14",
    region_map=None,
    output_path=country_outdir,
    filename=f"cpi_weights_{country_tag}_{YEAR}.csv"
)

print(f"CPI weights per country saved to {country_outdir}")

# Path to the just‐written CPI weights file
cpi_file = country_outdir / f"cpi_weights_{country_tag}_{YEAR}.csv"

# === Discover which country columns we actually have ===
import pandas as pd

# Read only the header row (single header)
cpi_cols = pd.read_csv(cpi_file, nrows=0).columns

# Get country codes, skipping index columns
per_country_list = [col for col in cpi_cols if not col.startswith('Unnamed:')]

# === Apply country‐level CPI weights to your shock results ===

YEAR = 2021  # Define the year for output filenames

apply_cpi_weights_to_gas_price_shock(
    price_change_path = GAS_PRICE_SHOCK_OUTPUTS / "extra_vs_full_2021"/ f"results_extra.csv",
    cpi_weights_path  = cpi_file,
    regions           = per_country_list,
    output_path       = GAS_PRICE_SHOCK_OUTPUTS / "weighted_impacts" /
                        f"extra_cpi_country_impacts_{YEAR}.csv"
)

apply_cpi_weights_to_gas_price_shock(
    price_change_path = GAS_PRICE_SHOCK_OUTPUTS / "extra_vs_full_2021"/ f"results_full.csv",
    cpi_weights_path  = cpi_file,
    regions           = per_country_list,
    output_path       = GAS_PRICE_SHOCK_OUTPUTS / "weighted_impacts" /
                        f"full_cpi_country_impacts_{YEAR}.csv"
)

apply_cpi_weights_to_gas_price_shock(
    price_change_path = GAS_PRICE_SHOCK_OUTPUTS / "extra_vs_full_2021"/ f"results_intra.csv",
    cpi_weights_path  = cpi_file,
    regions           = per_country_list,
    output_path       = GAS_PRICE_SHOCK_OUTPUTS / "weighted_impacts" /
                        f"intra_cpi_country_impacts_{YEAR}.csv"
)

apply_cpi_weights_to_gas_price_shock(
    price_change_path = GAS_PRICE_SHOCK_OUTPUTS / f"results_extra_{YEAR}.csv",
    cpi_weights_path  = cpi_file,
    regions           = per_country_list,
    output_path       = GAS_PRICE_SHOCK_OUTPUTS / "weighted_impacts" /
                        f"cpi_country_impacts_extra_{YEAR}.csv"
)

apply_cpi_weights_to_gas_price_shock(
    price_change_path = GAS_PRICE_SHOCK_OUTPUTS / f"results_intra_extra_{YEAR}.csv",
    cpi_weights_path  = cpi_file,
    regions           = per_country_list,
    output_path       = GAS_PRICE_SHOCK_OUTPUTS / "weighted_impacts" /
                        f"cpi_country_impacts_intra_extra_{YEAR}.csv"
)

