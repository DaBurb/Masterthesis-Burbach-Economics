from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Shared data directories
DATA_DIR = BASE_DIR / "data"

FIGARO_RAW_DIR = DATA_DIR / "figaro" / "raw"
FIGARO_PROCESSED_DIR = DATA_DIR / "figaro" / "processed"

# Submatrices of Figaro
FIGARO_FULL_MATRIX_DIR = FIGARO_PROCESSED_DIR / "full_matrix"
FIGARO_Z_MATRIX_DIR = FIGARO_PROCESSED_DIR / "Z_matrix"
FIGARO_Y_MATRIX_DIR = FIGARO_PROCESSED_DIR / "Y_matrix"
FIGARO_X_VECTOR_DIR = FIGARO_PROCESSED_DIR / "X_vector"
FIGARO_VA_MATRIX_DIR = FIGARO_PROCESSED_DIR / "VA_matrix"

EXIOBASE_RAW_DIR = DATA_DIR / "exiobase" / "raw"
EXIOBASE_PROCESSED_DIR = DATA_DIR / "exiobase" / "processed"

SEA_RAW_DIR = DATA_DIR / "sea" / "raw"
SEA_PROCESSED_DIR = DATA_DIR / "sea" / "processed"

# Shared module directory
SHARED_DIR = BASE_DIR / "shared"

# Directories for each of the two analyses
GAS_PRICE_SHOCK_DIR = BASE_DIR / "part_gas_price_shock"
SYSTEMIC_PRICES_DIR = BASE_DIR / "part_systemically_significant_prices"

# Analysis: Gas Price Shock
GAS_PRICE_SHOCK_SRC = GAS_PRICE_SHOCK_DIR / "src"
GAS_PRICE_SHOCK_NOTEBOOKS = GAS_PRICE_SHOCK_DIR / "notebooks"
GAS_PRICE_SHOCK_OUTPUTS = GAS_PRICE_SHOCK_DIR / "outputs"
GAS_PRICE_SHOCK_DATA = GAS_PRICE_SHOCK_DIR / "data"
GAS_PRICE_SHOCK_VIS = GAS_PRICE_SHOCK_DIR / "visualizations"

# Analysis: Systemically Significant Prices
SYSTEMIC_PRICES_SRC = SYSTEMIC_PRICES_DIR / "src"
SYSTEMIC_PRICES_NOTEBOOKS = SYSTEMIC_PRICES_DIR / "notebooks"
SYSTEMIC_PRICES_OUTPUTS = SYSTEMIC_PRICES_DIR / "outputs"
SYSTEMIC_PRICES_DATA = SYSTEMIC_PRICES_DIR / "data"
SYSTEMIC_PRICES_VIS = SYSTEMIC_PRICES_DIR / "visualizations"

# Ensure all directories exist
directories = [
    FIGARO_RAW_DIR, FIGARO_PROCESSED_DIR,
    FIGARO_FULL_MATRIX_DIR, FIGARO_Z_MATRIX_DIR, FIGARO_Y_MATRIX_DIR, FIGARO_X_VECTOR_DIR, FIGARO_VA_MATRIX_DIR,
    EXIOBASE_RAW_DIR, EXIOBASE_PROCESSED_DIR,
    SEA_RAW_DIR, SEA_PROCESSED_DIR, 
    SHARED_DIR,
    GAS_PRICE_SHOCK_SRC, GAS_PRICE_SHOCK_NOTEBOOKS, GAS_PRICE_SHOCK_OUTPUTS,
    GAS_PRICE_SHOCK_DATA, GAS_PRICE_SHOCK_VIS,
    SYSTEMIC_PRICES_SRC, SYSTEMIC_PRICES_NOTEBOOKS, SYSTEMIC_PRICES_OUTPUTS,
    SYSTEMIC_PRICES_DATA, SYSTEMIC_PRICES_VIS,
]

for directory in directories:
    directory.mkdir(parents=True, exist_ok=True)
    print(f"Ensured directory exists: {directory}")
