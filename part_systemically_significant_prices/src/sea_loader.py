# sea_loader.py

import sys
from pathlib import Path

# Add root directory to path so config.py can be imported
sys.path.append(str(Path(__file__).resolve().parents[2]))

import requests
import pandas as pd
from config import SEA_RAW_DIR

SEA_URL = "https://dataverse.nl/api/access/datafile/199095"
SEA_FILENAME = "WIOD_SEA.xlsx"
SEA_FILEPATH = SEA_RAW_DIR / SEA_FILENAME

def download_sea_file():
    if not SEA_FILEPATH.exists():
        print(f"Downloading WIOD SEA data from {SEA_URL} ...")
        response = requests.get(SEA_URL)
        if response.status_code != 200:
            raise ValueError(f"Failed to download file: status {response.status_code}")
        SEA_RAW_DIR.mkdir(parents=True, exist_ok=True)
        with open(SEA_FILEPATH, "wb") as f:
            f.write(response.content)
        print(f"File downloaded to: {SEA_FILEPATH}")
    else:
        print(f"File already exists: {SEA_FILEPATH}")
    return SEA_FILEPATH

def load_sea_data(sheet_name: str = "DATA") -> pd.DataFrame:
    return pd.read_excel(SEA_FILEPATH, sheet_name=sheet_name)
