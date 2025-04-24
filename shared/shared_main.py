# shared_main.py

from pathlib import Path
import sys

# Add project root to system path to allow relative imports from config and shared modules
sys.path.append(str(Path(__file__).resolve().parents[1]))

from config import FIGARO_RAW_DIR, FIGARO_FULL_MATRIX_DIR
from data_loader import get_figaro_file_paths
from preprocessing import get_preprocessed_figaro_matrices

def main():
    # Step 1: Download raw FIGARO data (only if not already downloaded)
    print("=== Downloading FIGARO data ===")
    file_paths = get_figaro_file_paths(start_year=2010, end_year=2022)

    # Step 2: Preprocess FIGARO data into MultiIndex format with consistent sector naming
    print("\n=== Preprocessing FIGARO data ===")
    figaro_data = get_preprocessed_figaro_matrices(file_paths, processed_dir=FIGARO_FULL_MATRIX_DIR)

    print("\n=== FIGARO data pipeline completed ===")
    return figaro_data


if __name__ == "__main__":
    main()