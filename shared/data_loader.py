# shared/data_loader.py

from pathlib import Path
import requests
import sys
import pandas as pd

# Add the project root to the system path to allow importing from config.py
sys.path.append(str(Path(__file__).resolve().parents[1]))

from config import FIGARO_RAW_DIR  # centralized FIGARO raw data path

FIGARO_BASE_URL = (
    "https://ec.europa.eu/eurostat/documents/51957/19580762/" 
    "matrix_eu-ic-io_ind-by-ind_24ed_{year}.csv"
)

def download_figaro_file(year: int) -> Path:
    """
    Download a FIGARO CSV file for the specified year if it does not already exist.

    Parameters:
        year (int): Year of the FIGARO dataset.

    Returns:
        Path: Path to the downloaded or existing file.
    """
    filename = f"figaro_matrix_{year}.csv"
    filepath = FIGARO_RAW_DIR / filename

    if not filepath.exists():
        url = FIGARO_BASE_URL.format(year=year)
        print(f"Downloading FIGARO data for {year} from {url} ...")
        response = requests.get(url)
        if response.status_code != 200:
            raise ValueError(f"Failed to download FIGARO data for {year}: {url}")
        with open(filepath, "wb") as f:
            f.write(response.content)
        print(f"Downloaded and saved FIGARO data for {year} at {filepath}")
    else:
        print(f"FIGARO data for {year} already exists at {filepath}")

    return filepath


def get_figaro_file_paths(start_year=2010, end_year=2022) -> dict:
    """
    Download and return file paths for FIGARO datasets between two years.

    Parameters:
        start_year (int): First year to include (default: 2010).
        end_year (int): Last year to include (default: 2022).

    Returns:
        dict: A dictionary mapping years to file paths.
    """
    file_paths = {}
    for year in range(start_year, end_year + 1):
        path = download_figaro_file(year)
        file_paths[year] = path
    return file_paths

def load_figaro_processed(years: list[int]) -> dict[int, pd.DataFrame]:
    """
    Load preprocessed FIGARO matrices with MultiIndex for given years.
    Ensures that MultiIndex levels are named ['Country', 'Sector'].

    Parameters:
        years (list[int]): List of years to load.

    Returns:
        dict[int, pd.DataFrame]: Dictionary of {year: MultiIndexed DataFrame}
    """
    from config import FIGARO_FULL_MATRIX_DIR

    data = {}
    for year in years:
        path = FIGARO_FULL_MATRIX_DIR / f"figaro_matrix_{year}.csv"
        if not path.exists():
            raise FileNotFoundError(f"FIGARO processed file for {year} not found: {path}")

        df = pd.read_csv(path, index_col=[0, 1], header=[0, 1])

        # Ensure consistent MultiIndex naming
        df.index.names = ["Country", "Sector"]
        df.columns.names = ["Country", "Sector"]

        data[year] = df

    return data