# shared/aggregation.py

import pandas as pd
from pathlib import Path
from typing import Optional

def aggregate_sectors(df: pd.DataFrame, mapping: dict, output_path: Optional[Path] = None) -> pd.DataFrame:
    """
    Rename and aggregate sector codes for both row and column MultiIndex levels.

    Parameters:
        df (pd.DataFrame): MultiIndexed DataFrame with (Country, Sector) on both axes.
        mapping (dict): Mapping from detailed to aggregated sector codes.
        output_path (Optional[Path]): If provided, saves the aggregated DataFrame.

    Returns:
        pd.DataFrame: Aggregated DataFrame with renamed sectors.
    """
    # Rename sector levels
    df.index = pd.MultiIndex.from_tuples(
    [(country, mapping.get(sector, sector)) for country, sector in df.index],
    names=["Country", "Sector"]
    )
    df.columns = pd.MultiIndex.from_tuples(
    [(country, mapping.get(sector, sector)) for country, sector in df.columns],
    names=["Country", "Sector"]
    )


    # Group by renamed sectors
    df = df.groupby(level=["Country", "Sector"]).sum()
    df = df.groupby(level=["Country", "Sector"], axis=1).sum()

    # Save if path provided
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path)

    return df
