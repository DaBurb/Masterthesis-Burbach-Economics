import pandas as pd
from typing import Optional

def calculate_cpi_weights(
    df: pd.DataFrame,
    consumption_code: str = "P3_S14",
    region_map: Optional[dict[str, str]] = None
) -> pd.DataFrame:
    """
    Compute CPI weights based on household consumption, either per country or per region.

    Parameters:
        df (pd.DataFrame): MultiIndexed DataFrame with (Country, Sector) on both axes.
        consumption_code (str): Column-sector code for household consumption (default: "P3_S14").
        region_map (dict[str, str] | None): Mapping from countries to region names. If None, compute individual weights.

    Returns:
        pd.DataFrame: DataFrame with CPI weights per region in columns (region, 'cpi_weight'),
                      excluding rows like ('GO', ...) and ('W2', ...).
    """
    result = pd.DataFrame(index=df.index)

    # Determine country groups
    countries = df.columns.get_level_values("Country").unique()
    if region_map:
        region_groups = {}
        for country in countries:
            region = region_map.get(country, "ROW")
            region_groups.setdefault(region, []).append(country)
    else:
        region_groups = {country: [country] for country in countries}

    # Exclude invalid rows
    valid_rows = df.index[
        (~df.index.get_level_values("Country").isin(["GO", "W2"]))
    ]

    # Compute CPI weights for each group
    for region_name, region_countries in region_groups.items():
        region_cols = [(c, consumption_code) for c in region_countries if (c, consumption_code) in df.columns]
        if not region_cols:
            continue

        region_total = df.loc[valid_rows, region_cols].sum(axis=1).sum()
        region_share = (
            df.loc[valid_rows, region_cols].sum(axis=1) / region_total
            if region_total > 0 else pd.Series(0, index=valid_rows)
        )

        # Fill zeros elsewhere, assign weights to valid rows
        weight_col = pd.Series(0.0, index=df.index)
        weight_col.loc[valid_rows] = region_share
        result[(region_name, "cpi_weight")] = weight_col

    # Drop W2 and GO rows from result
    result = result.loc[valid_rows]

    # Ensure column MultiIndex
    result.columns = pd.MultiIndex.from_tuples(result.columns)

    return result
