Preprocessing Pipeline for FIGARO Data

This repository includes a robust, modular pipeline for loading, preprocessing, and extracting economic submatrices from Eurostat FIGARO input-output datasets. The pipeline is tailored for use in systemic inflation exposure analysis and integrates smoothly into a larger thesis project.


✅ Progress Summary (Today’s Session)
1. Data Loading (data_loader.py)

    Implemented a robust function to download annual FIGARO CSVs directly from Eurostat.

    Prevents redundant downloads by checking if the file already exists.

    Returns a dictionary of {year: Path}.

2. Preprocessing Pipeline (shared/preprocessing.py)

    Loaded raw FIGARO CSVs with proper encoding and structure.

    Converted row and column labels into a MultiIndex format (['Country', 'Sector']) using a clean and validated split_index_to_multiindex() function.

    Renamed sector codes (e.g. C10T12 → C10-C12) using a safe mapping method that updates only the 'Sector' level of the MultiIndex.

    Added a gross output row labeled ('GO', 'GO'), computed from column-wise sums.

    Extracted submatrices for modular use:

        Z: Interindustry flow matrix

        Y: Final demand matrix

        X: Gross output vector

        VA: Value added matrix

    Saved all processed outputs into clearly defined folders under data/figaro/processed.

3. Structural Integrity Fix

    Ensured .index.names and .columns.names were explicitly re-applied after renaming steps.

    Solved a silent but critical issue where .names were dropped due to MultiIndex reconstruction.

4. Debugging Tools

    Implemented temporary debug prints to confirm MultiIndex structure and names at key transformation points.

    Verified correct behavior on a minimal working example (2010 dataset).

📁 Output Directory Structure

data/figaro/
├── raw/
├── processed/
│   ├── full_matrix/
│   ├── Z_matrix/
│   ├── Y_matrix/
│   ├── X_vector/
│   └── VA_matrix/

🔧 Next Steps

    Integrate loaders for extracted matrices (e.g. load_matrix("Z", year)).

    Expand preprocessing to EXIOBASE and SEA datasets.

    Link this pipeline into systemic_main.py for systemically significant price analysis.


▶️ How to Run the Pipeline

🔹 1. Main entry point

Run this from the project root:

python shared/shared_main.py

This will:

    Download all FIGARO datasets (2010–2022)

    Preprocess them

    Save full and partial outputs to data/figaro/processed/

🔹 2. Modify parameters (optional)

    To adjust years, edit this block in shared_main.py:

file_paths = get_figaro_file_paths(start_year=2010, end_year=2022)

    To only work on one year for testing:

file_paths = get_figaro_file_paths(start_year=2015, end_year=2015)