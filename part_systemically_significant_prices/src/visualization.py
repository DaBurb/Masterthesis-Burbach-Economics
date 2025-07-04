import sys
from pathlib import Path

# Extend sys.path to access config and shared modules
sys.path.append(str(Path(__file__).resolve().parents[2]))

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from config import (
    SYSTEMIC_PRICES_OUTPUTS,
    SYSTEMIC_A_MATRIX_DIR,
    SYSTEMIC_CPI_WEIGHTS_DIR,
)

def plot_systemic_volatility_scatter(year: int, vol_df: pd.DataFrame = None, country: str = None):
    # Load volatility data if not provided
    if vol_df is None:
        volatility_path = SYSTEMIC_PRICES_OUTPUTS / "volatility" / "II_PI_volatility.csv"
        vol_df = pd.read_csv(volatility_path)

    # Ensure consistent format
    if "price_volatility" in vol_df.columns:
        vol_df = vol_df.rename(columns={"price_volatility": "Volatility"})
    if not isinstance(vol_df.index, pd.MultiIndex):
        vol_df = vol_df.set_index(["Country", "Sector"])

    # Load A matrix
    A_path = SYSTEMIC_A_MATRIX_DIR / f"A_{year}.csv"
    A = pd.read_csv(A_path, header=[0, 1], index_col=[0, 1])
    A.columns.names = ["Country", "Sector"]
    forward_linkages_full = A.sum(axis=1).rename("ForwardLinkages")

    # Iterate over available CPI weight folders
    for region_folder in SYSTEMIC_CPI_WEIGHTS_DIR.glob("*"):
        if not region_folder.is_dir():
            continue

        region = region_folder.name
        cpi_path = region_folder / f"cpi_weights_{region}_{year}.csv"
        if not cpi_path.exists():
            print(f"Missing CPI weight file for region: {region}")
            continue

        print(f"Generating scatter plot for region: {region}")

        cpi = pd.read_csv(cpi_path, header=[0, 1], index_col=[0, 1])
        cpi.columns.names = ["Country", "Sector"]
        cpi_weights_full = cpi.sum(axis=1).rename("CPIWeight")

        # === Apply optional country filtering ===
        if country is not None:
            vol_df_country = vol_df.loc[vol_df.index.get_level_values("Country") == country]
            forward_linkages = forward_linkages_full.loc[forward_linkages_full.index.get_level_values("Country") == country]
            cpi_weights = cpi_weights_full.loc[cpi_weights_full.index.get_level_values("Country") == country]
        else:
            vol_df_country = vol_df
            forward_linkages = forward_linkages_full
            cpi_weights = cpi_weights_full

        # Merge
        common_index = vol_df_country.index.intersection(forward_linkages.index).intersection(cpi_weights.index)
        df = pd.concat([
            vol_df_country.loc[common_index],
            forward_linkages.loc[common_index],
            cpi_weights.loc[common_index]
        ], axis=1)

        # Skip empty plots
        if df.empty:
            print(f"Skipping region {region}: no overlapping data.")
            continue

        df["Systemic"] = (
            (df["Volatility"] > df["Volatility"].mean()) &
            (df["ForwardLinkages"] > df["ForwardLinkages"].mean())
        )

        # Plot
        plt.figure(figsize=(10, 7))
        sns.scatterplot(
            data=df.reset_index(),
            x="ForwardLinkages",
            y="Volatility",
            size="CPIWeight",
            hue="Systemic",
            palette={True: 'purple', False: 'grey'},
            alpha=0.7,
            edgecolor='black',
            sizes=(20, 400),
            legend="brief"
        )

        for _, row in df.reset_index().iterrows():
            plt.text(
                row["ForwardLinkages"], row["Volatility"], row["Sector"],
                fontsize=7, ha="center", va="center"
            )


        plt.axhline(df["Volatility"].mean(), color='grey', linestyle='--', linewidth=1)
        plt.axvline(df["ForwardLinkages"].mean(), color='grey', linestyle='--', linewidth=1)
        title = f"Systemic Sectors: Volatility vs Forward Linkages ({region.upper()}, {year})"
        if country:
            title += f" - {country}"
        plt.title(title)
        plt.xlabel("Forward Linkages (row sum of A)")
        plt.ylabel("Volatility (std dev of II_PI)")
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()
        plt.show()

