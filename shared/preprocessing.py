# Revised version of shared/preprocessing.py with full scientific comments for clarity

from pathlib import Path
import pandas as pd
from config import (
    FIGARO_FULL_MATRIX_DIR,FIGARO_VA_MATRIX_DIR, FIGARO_X_VECTOR_DIR,FIGARO_Y_MATRIX_DIR, FIGARO_Z_MATRIX_DIR
)

# Define constants
SECTOR_RENAMES = {
    "C10T12": "C10-C12",
    "C13T15": "C13-C15",
    "C31_32": "C31_C32",
    "E37T39": "E37-E39",
    "J59_60": "J59_J60",
    "J62_63": "J62_J63",
    "M69_70": "M69_M70",
    "M74_75": "M74_M75",
    "N80T82": "N80-N82",
    "R90T92": "R90-R92",
    "Q87_88": "Q87-Q88",
    "L": "L68"
}

FINAL_DEMAND_CODES = {"P3_S13", "P3_S14", "P3_S15", "P51G", "P5M"}
VALUE_ADDED_CODES = {"D21X31", "OP_RES", "OP_NRES", "D1", "D29X39", "B2A3G"}

def split_index_to_multiindex(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converts the DataFrame's index and columns into a MultiIndex with levels: ['Country', 'Sector'].
    Splits each label at the first underscore.
    """

    def make_multiindex(labels):
        countries = []
        sectors = []
        for label in labels:
            label = str(label).strip()
            if "_" not in label:
                raise ValueError(f"Label '{label}' cannot be split at '_'.")
            country, sector = label.split("_", 1)
            countries.append(country)
            sectors.append(sector)
        return pd.MultiIndex.from_arrays([countries, sectors], names=["Country", "Sector"])

    df.index = make_multiindex(df.index)
    df.columns = make_multiindex(df.columns)
    return df

def rename_sector_codes_in_index(df: pd.DataFrame, rename_dict: dict) -> pd.DataFrame:
    """
    Safely renames the sector codes in the 'Sector' level of a MultiIndex for both index and columns.

    Parameters:
        df (pd.DataFrame): MultiIndexed DataFrame with levels ['Country', 'Sector']
        rename_dict (dict): Mapping from old to new sector codes

    Returns:
        pd.DataFrame: DataFrame with updated sector codes in MultiIndex.
    """
    # Rename row index
    df.index = df.index.set_levels(
        df.index.levels[1].to_series().replace(rename_dict),
        level="Sector"
    )

    # Rename column index
    df.columns = df.columns.set_levels(
        df.columns.levels[1].to_series().replace(rename_dict),
        level="Sector"
    )

    return df

def add_gross_output_row(df: pd.DataFrame) -> pd.DataFrame:
    """
    Appends a gross output row ('GO', 'GO') containing the column-wise sum of all existing rows.

    Parameters:
        df (pd.DataFrame): Input-output table with MultiIndex.

    Returns:
        pd.DataFrame: Extended table with gross output row.
    """
    gross_output = df.sum(axis=0)
    gross_output.name = ("GO", "GO")
    return pd.concat([df, pd.DataFrame(gross_output).T])

def extract_Z_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts the interindustry flow matrix (Z), excluding final demand columns,
    value added rows, and the gross output row.

    Returns:
        pd.DataFrame: Interindustry flow matrix.
    """
    row_filter = (~df.index.get_level_values("Country").isin(["W2", "GO"]))
    col_filter = (~df.columns.get_level_values("Sector").isin(FINAL_DEMAND_CODES)) & \
                 (~df.columns.get_level_values("Country").isin(["W2"]))
    return df.loc[row_filter, col_filter]

def extract_Y_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts the final demand matrix (Y) using defined final demand codes.

    Returns:
        pd.DataFrame: Final demand matrix.
    """
    col_filter = df.columns.get_level_values("Sector").isin(FINAL_DEMAND_CODES)
    row_filter = (~df.index.get_level_values("Country").isin(["GO"])) & \
                 (~df.index.get_level_values("Country").isin(["W2"]))
    return df.loc[row_filter, col_filter]

def extract_X_vector(df: pd.DataFrame) -> pd.Series:
    """
    Extracts the gross output vector (X) from the ('GO', 'GO') row.

    Returns:
        pd.Series: Gross output vector.
    """
    return df.loc[("GO", "GO")]

def extract_VA_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts the value added matrix (VA) from the W2 country rows.

    Returns:
        pd.DataFrame: Value added matrix.
    """
    mask = (df.index.get_level_values("Country") == "W2") & \
           (df.index.get_level_values("Sector").isin(VALUE_ADDED_CODES))
    return df.loc[mask]

def preprocess_figaro_data(filepath: Path, save_processed=True, processed_dir: Path = None) -> pd.DataFrame:
    """
    Load, convert, rename, and process a FIGARO dataset. Also extract and save submatrices
    (Z, Y, X, VA) for downstream modular access.

    Parameters:
        filepath (Path): Raw FIGARO CSV file.
        save_processed (bool): If True, save processed table and extracted matrices.
        processed_dir (Path): Optional override for the processed output directory.

    Returns:
        pd.DataFrame: Fully processed MultiIndexed FIGARO table.
    """
    df = pd.read_csv(filepath, index_col=0, header=0, sep=",", encoding="utf-8-sig")
    df = split_index_to_multiindex(df)
    df = rename_sector_codes_in_index(df, SECTOR_RENAMES)
    df = add_gross_output_row(df)

    # Ensure MultiIndex names are set before any export or downstream use
    df.index.names = ["Country", "Sector"]
    df.columns.names = ["Country", "Sector"]

    if save_processed:
        year = int(filepath.stem.split("_")[-1])
        processed_dir = processed_dir or FIGARO_FULL_MATRIX_DIR
        processed_dir.mkdir(parents=True, exist_ok=True)

        df.to_csv(processed_dir / filepath.name)
        extract_Z_matrix(df).to_csv(FIGARO_Z_MATRIX_DIR / f"Z_{year}.csv")
        extract_Y_matrix(df).to_csv(FIGARO_Y_MATRIX_DIR / f"Y_{year}.csv")
        extract_X_vector(df).to_frame(name="gross_output").to_csv(FIGARO_X_VECTOR_DIR / f"X_{year}.csv")
        extract_VA_matrix(df).to_csv(FIGARO_VA_MATRIX_DIR / f"VA_{year}.csv")

    return df

def get_preprocessed_figaro_matrices(filepaths: dict, processed_dir: Path = None):
    """
    Processes multiple FIGARO datasets into MultiIndex DataFrames with renamed sectors.

    Parameters:
        filepaths (dict): {year: Path} dictionary of raw data file paths.
        processed_dir (Path): Directory to save processed data.

    Returns:
        dict: {year: DataFrame} dictionary of processed data.
    """
    processed_data = {}
    for year, path in filepaths.items():
        processed_data[year] = preprocess_figaro_data(path, save_processed=True, processed_dir=processed_dir)
        print(f"Dataset for year {year} preprocessed successfully.")
    return processed_data