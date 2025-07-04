import sys
from pathlib import Path
import pymrio

# Extend sys.path to access config and shared modules
sys.path.append(str(Path(__file__).resolve().parents[2]))

import pymrio
from config import (
    EXIOBASE_RAW_DIR,
    EXIOBASE_PROCESSED_DIR,
    EXIOBASE_ROW_REGION_MAPPING,
    EXIOBASE_TO_NACE_MAPPING
)

import os
from shutil import copy2

def download_exiobase3_if_missing(year: int, system: str = "ixi") -> Path:
    """
    Ensures the EXIOBASE3 ZIP for the given year/system is present.
    Downloads only years 2010–2022 to a local cache and copies the target file.
    """
    assert 2010 <= year <= 2022, f"Year {year} is outside supported range (2010–2022)"
    zip_filename = f"IOT_{year}_{system}.zip"
    zip_path = EXIOBASE_RAW_DIR / zip_filename

    if zip_path.exists():
        print(f"EXIOBASE3 file already exists: {zip_path}")
        return zip_path

    # Define custom download/cache folder
    download_folder = EXIOBASE_RAW_DIR / "_download_cache"
    os.makedirs(download_folder, exist_ok=True)

    print(f"Downloading EXIOBASE3 ({system}) years 2010–2022 into {download_folder} ...")
    pymrio.download_exiobase3(
        system=system,
        years=list(range(2010, 2023)),
        storage_folder=str(download_folder)
    )

    # Copy the file for the requested year to the raw directory
    source_file = download_folder / zip_filename
    if not source_file.exists():
        raise FileNotFoundError(f"Expected downloaded file not found: {source_file}")

    print(f"Copying {source_file.name} to {zip_path}")
    copy2(source_file, zip_path)

    return zip_path

def load_exiobase3(year: int, system: str = "ixi"):
    """
    Load EXIOBASE3 data for a given year and system (ixi, pxi, etc.).
    Downloads the archive if missing.
    """
    zip_path = download_exiobase3_if_missing(year, system)
    print(f"Parsing EXIOBASE3: {zip_path}")
    exio3 = pymrio.parse_exiobase3(path=str(zip_path))
    return exio3

def preprocess_exiobase3(exio3):
    """
    Preprocess EXIOBASE3 MRIO object:
    - Rename sectors using ExioName → ExioLabel
    - Rename regions to FIGARO-compatible scheme (ROW to FIGW1)
    - Rename sectors to match NACE-based sector scheme
    - Aggregate duplicates
    """

    mrio_class = pymrio.get_classification(mrio_name="exio3_ixi")

    print("\nRenaming EXIOBASE sectors from ExioName to ExioLabel ...")
    conv_dict = mrio_class.get_sector_dict(
        mrio_class.sectors.ExioName, mrio_class.sectors.ExioLabel
    )

    print("\nRenaming EXIOBASE regions to FIGW1 ...")
    exio3.rename_regions(EXIOBASE_ROW_REGION_MAPPING)
    exio3.aggregate_duplicates(inplace=True)

    # Use exio3 labels for easier renaming
    exio3.rename_sectors(conv_dict)
   
    print("\nRenaming EXIOBASE sectors to NACE-compatible codes ...")
    exio3.rename_sectors(EXIOBASE_TO_NACE_MAPPING)
    exio3.aggregate_duplicates(inplace=True)

    return exio3

def save_processed_exiobase(exio3, year: int):
    """
    Save preprocessed EXIOBASE3 matrices to processed directory.
    """
    Z_path = EXIOBASE_PROCESSED_DIR / f"Z_matrix_{year}.csv"
    print(f"Saving Z matrix to {Z_path}")
    exio3.Z.to_csv(Z_path)

    Y_path = EXIOBASE_PROCESSED_DIR / f"Y_matrix_{year}.csv"
    print(f"Saving Y matrix to {Y_path}")
    exio3.Y.to_csv(Y_path)

    # Optionally save more components (e.g., X, A, VA) as needed later

    print("Preprocessing complete.")
    return Z_path, Y_path

def load_and_process_exiobase(year: int):
    exio3 = load_exiobase3(year)
    exio3 = preprocess_exiobase3(exio3)
    return save_processed_exiobase(exio3, year)
