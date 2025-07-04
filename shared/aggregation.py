# shared/aggregation.py

import pandas as pd
from pathlib import Path
from typing import Dict, Optional

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



import pandas as pd
from typing import Dict, Optional, Union

def aggregate_output_vector(
    X: Union[pd.DataFrame, pd.Series],
    sector_map: Dict[str, str],
    country_merge_map: Optional[Dict[str, str]] = None
) -> pd.Series:
    """
    Aggregates a gross output vector over sectors and optionally merges countries.

    Parameters:
        X (pd.DataFrame or pd.Series):
            Either a DataFrame with exactly one column or a Series,
            both indexed by a MultiIndex (Country, Sector).
        sector_map (dict): Mapping from original to aggregated sectors.
        country_merge_map (dict, optional): Mapping from old country codes to merged ones.

    Returns:
        pd.Series: Aggregated gross output with MultiIndex (Country, Sector).
    """
    # turn it into a Series
    if isinstance(X, pd.DataFrame):
        if X.shape[1] != 1:
            raise ValueError("Expected X to have exactly one column")
        s = X.iloc[:, 0].copy()
    else:
        s = X.copy()

    # check index
    if not isinstance(s.index, pd.MultiIndex) or s.index.nlevels != 2:
        raise ValueError("X must be indexed by a MultiIndex (Country, Sector)")

    # apply country / sector mapping
    countries = list(s.index.get_level_values(0))
    sectors   = list(s.index.get_level_values(1))

    if country_merge_map:
        countries = [country_merge_map.get(c, c) for c in countries]
    sectors = [sector_map.get(sec, sec) for sec in sectors]

    s.index = pd.MultiIndex.from_arrays(
        [countries, sectors],
        names=["Country", "Sector"]
    )

    # group and sum
    return s.groupby(level=["Country", "Sector"]).sum()



