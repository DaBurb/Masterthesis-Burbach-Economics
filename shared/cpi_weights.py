import pandas as pd
import numpy as np
import os
import re
import sys
from tqdm import tqdm
from typing import Optional, Literal, Union
from pathlib import Path
# Extend sys.path to access config and shared modules
sys.path.append(str(Path(__file__).resolve().parents[1]))

def calculate_cpi_weights(
    df: pd.DataFrame,
    consumption_code: str = "P3_S14",
    region_map: Optional[dict[str, str]] = None,
    output_path: Optional[str] = None,
    filename: str = "cpi_weights.csv"
) -> pd.DataFrame:
    """
    Compute and optionally save CPI weights based on household consumption, per country or region.

    Parameters:
        df (pd.DataFrame): MultiIndexed DataFrame with (Country, Sector) on both axes.
        consumption_code (str): Column-sector code for household consumption (default: "P3_S14").
        region_map (dict[str, str] | None): Mapping from countries to region names. If None, compute weights per country.
        output_path (str | None): Optional path to save result as CSV. If None, result is not saved.
        filename (str): Filename for output CSV (default: 'cpi_weights.csv').

    Returns:
        pd.DataFrame: DataFrame with CPI weights per region in columns (region, 'cpi_weight'),
                      excluding rows like ('GO', ...) and ('W2', ...).
    """
    assert isinstance(df.index, pd.MultiIndex), "df.index must be MultiIndex"
    assert isinstance(df.columns, pd.MultiIndex), "df.columns must be MultiIndex"

    df = df.fillna(0.0)
    result = pd.DataFrame(index=df.index)
    countries = df.columns.get_level_values("Country").unique()

    if region_map:
        region_groups = {}
        for country in countries:
            region = region_map.get(country, "ROW")
            region_groups.setdefault(region, []).append(country)
    else:
        region_groups = {country: [country] for country in countries}

    valid_rows = df.index[
        (~df.index.get_level_values("Country").isin(["GO", "W2"]))
    ]

    for region_name, region_countries in region_groups.items():
        region_cols = [(c, consumption_code) for c in region_countries if (c, consumption_code) in df.columns]
        if not region_cols:
            continue

        region_total = df.loc[valid_rows, region_cols].sum(axis=1).sum()
        region_share = (
            df.loc[valid_rows, region_cols].sum(axis=1) / region_total
            if region_total > 0
            else pd.Series(0.0, index=valid_rows)
        )

        weight_col = pd.Series(0.0, index=df.index)
        weight_col.loc[valid_rows] = region_share
        result[(region_name, "cpi_weight")] = weight_col

    result = result.loc[valid_rows]
    result.columns = pd.MultiIndex.from_tuples(result.columns) # type: ignore[arg-type]

    # Save result if requested
    if output_path is not None:
        Path(output_path).mkdir(parents=True, exist_ok=True)
        result.to_csv(Path(output_path) / filename)

    return result



def apply_all_available_cpi_weights(
    year: int,
    unweighted_impacts_path: Path,
    price_volatility_path: Path,
    cpi_weights_root: Path,
    output_dir: Path,
    region_maps: dict[str, dict[str, str]],
    output_prefix: str = "weighted_impacts"
) -> None:
    """
    Apply CPI weights for all specified regional aggregation schemes and compute weighted shock impacts.

    Parameters:
        year (int): The year to process.
        unweighted_impacts_path (Path): Path to the CSV file containing unweighted shock propagation results.
        price_volatility_path (Path): Path to the CSV file containing sectoral price volatility values.
        cpi_weights_root (Path): Root directory where regional CPI weight folders are located.
        output_dir (Path): Directory where computed weighted impact results will be saved.
        region_maps (dict): A dictionary mapping region tags (e.g. "individual", "eu28") to country-to-region maps.
        output_prefix (str): Prefix for output file names. Default is "weighted_impacts".
    """

    # Load required input data
    price_volatility = pd.read_csv(price_volatility_path, index_col=[0, 1])
    unweighted = pd.read_csv(unweighted_impacts_path, header=[0, 1], index_col=[0, 1])

    # Iterate through each available regional weighting scheme
    for region_tag, region_map in region_maps.items():
        weight_file = cpi_weights_root / region_tag / f"cpi_weights_{region_tag}_{year}.csv"
        if not weight_file.exists():
            print(f"Missing CPI weight file for region tag: {region_tag}")
            continue

        print(f"Processing CPI-weighted impacts for region tag: {region_tag}")
        cpi_weights = pd.read_csv(weight_file, header=[0, 1], index_col=[0, 1])

        results = []

        # Loop over all exogenous sectors (rows of unweighted impacts)
        for exo_sector in tqdm(unweighted.index, desc=f"Processing {region_tag} {year}", unit="sector"):
            country, sector = exo_sector

            # Skip if no volatility data is available for this sector
            if (country, sector) not in price_volatility.index:
                print(f"Missing price volatility for sector: ({country}, {sector})")
                continue

            try:
                # Select the correct CPI weight column for the current country
                if region_tag == "individual":
                    weight_col = (country, "cpi_weight")
                else:
                    region = region_map.get(country, "ROW")
                    weight_col = (region, "cpi_weight")

                # Retrieve the price shock and compute direct impact
                price_shock = price_volatility.loc[(country, sector)].values[0]
                direct = cpi_weights.loc[(country, sector), weight_col] * price_shock

                # Retrieve all propagated impacts caused by this exogenous sector
                propagated = unweighted.loc[(country, sector)]

                # Step 1: Build a DataFrame from propagated index
                prop_index = pd.DataFrame(propagated.index.tolist(), columns=["Country", "Sector"])

                # Step 2: Determine the correct CPI weight column for each country
                if region_tag == "individual":
                    prop_index["Region"] = prop_index["Country"]
                else:
                    prop_index["Region"] = prop_index["Country"].map(region_map).fillna("ROW")

                # Step 3: Build lookup keys
                row_tuples = list(zip(prop_index["Country"], prop_index["Sector"]))
                col_tuples = list(zip(prop_index["Region"], ["cpi_weight"] * len(prop_index)))

                # Step 4: Retrieve weights with element-wise pairing
                weight_values = [
                    cpi_weights.loc[row, col]
                    for row, col in zip(row_tuples, col_tuples)
                ]

                # Step 5: Construct aligned weight vector
                weight_vector = pd.Series(weight_values, index=propagated.index)



                # Compute the indirect impact by excluding self-impact and summing all weighted values
                indirect = (weight_vector * propagated).drop(index=(country, sector), errors="ignore").sum()

                # Store result for current exogenous sector
                results.append({
                    "Country": country,
                    "Sector": sector,
                    "Direct Impact": direct,
                    "Indirect Impact": indirect,
                    "Total Impact": direct + indirect
                })

            except KeyError as e:
                print(f"Error while processing sector ({country}, {sector}): {e}")
                continue

        # Export results to CSV
        out_df = pd.DataFrame(results)
        out_path = output_dir / f"{output_prefix}_{region_tag}_{year}.csv"
        out_df.to_csv(out_path, index=False)
        print(f"Saved weighted impact results to: {out_path}")



def new_apply_all_available_cpi_weights(
    year: int,
    unweighted_impacts_path: Path,
    price_volatility_path: Path,
    cpi_weights_root: Path,
    output_dir: Path,
    output_prefix: str = "weighted_impacts"
) -> None:
    """
    Compute CPI-weighted shock impacts for each available regional CPI weighting scheme.

    Parameters:
        year (int): Year of data.
        unweighted_impacts_path (Path): Path to unweighted shock impacts (MultiIndex row/column).
        price_volatility_path (Path): Path to sector-level price volatility (MultiIndex index).
        cpi_weights_root (Path): Directory containing subfolders per region tag (e.g. eu28, north_south).
        output_dir (Path): Output directory for saving results.
        output_prefix (str): Filename prefix for output CSVs.
    """

    # Load inputs
    price_volatility = pd.read_csv(price_volatility_path, index_col=[0, 1])
    unweighted = pd.read_csv(unweighted_impacts_path, header=[0, 1], index_col=[0, 1])

    for region_tag_dir in cpi_weights_root.glob("*"):
        if not region_tag_dir.is_dir():
            continue

        region_tag = region_tag_dir.name
        weight_file = region_tag_dir / f"cpi_weights_{region_tag}_{year}.csv"
        if not weight_file.exists():
            print(f"Skipping {region_tag} (missing CPI weight file).")
            continue

        print(f"Processing CPI-weighted impacts for: {region_tag}")
        cpi_weights = pd.read_csv(weight_file, header=[0, 1], index_col=[0, 1])

        # Determine all regions to process, excluding ROW
        all_regions = cpi_weights.columns.get_level_values(0).unique()
        regions = [r for r in all_regions if r != "ROW"]

        results = []

        for exo_sector in tqdm(unweighted.index, desc=f"{region_tag} {year}", unit="sector"):
            if exo_sector not in price_volatility.index:
                continue

            price_shock = price_volatility.loc[exo_sector].values[0]
            propagated = unweighted.loc[exo_sector]

            for region in regions:
                try:
                    # Direct impact from price volatility on weighted own-sector
                    direct = cpi_weights.loc[exo_sector, (region, "cpi_weight")] * price_shock

                    # Indirect impact from propagated effects weighted by target sector weights
                    weights = cpi_weights.loc[propagated.index, (region, "cpi_weight")]
                    indirect = (weights * propagated).drop(index=exo_sector, errors="ignore").sum()

                    results.append({
                        "Country": exo_sector[0],
                        "Sector": exo_sector[1],
                        "Region": region,
                        "Direct Impact": direct,
                        "Indirect Impact": indirect,
                        "Total Impact": direct + indirect
                    })

                except KeyError as e:
                    print(f"Skipping region {region} or sector {exo_sector} due to missing data: {e}")
                    continue

        # Save result
        df_out = pd.DataFrame(results)
        out_file = output_dir / f"{output_prefix}_{region_tag}_{year}.csv"
        df_out.to_csv(out_file, index=False)
        print(f"Saved: {out_file}")