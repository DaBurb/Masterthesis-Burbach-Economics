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
FIGARO_A_MATRIX_DIR = FIGARO_PROCESSED_DIR / "A_matrix"

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

# Systemic Prices submatrices
SYSTEMIC_Z_MATRIX_DIR = SYSTEMIC_PRICES_DATA / "Z_matrix"
SYSTEMIC_A_MATRIX_DIR = SYSTEMIC_PRICES_DATA / "A_matrix"
SYSTEMIC_X_VECTOR_DIR = SYSTEMIC_PRICES_DATA / "X_vector"
SYSTEMIC_Y_MATRIX_DIR = SYSTEMIC_PRICES_DATA / "Y_matrix"
SYSTEMIC_FULL_MATRIX_DIR = SYSTEMIC_PRICES_DATA / "full_matrix"
SYSTEMIC_CPI_WEIGHTS_DIR = SYSTEMIC_PRICES_DATA / "cpi_weights"

# Output systemic prices directories
SYSTEMIC_UNWEIGHTED_IMPACTS_DIR = SYSTEMIC_PRICES_OUTPUTS / "unweighted_impacts"
SYSTEMIC_WEIGHTED_IMPACTS_DIR = SYSTEMIC_PRICES_OUTPUTS / "weighted_impacts"
SYSTEMIC_VOLATILITY_DIR = SYSTEMIC_PRICES_OUTPUTS / "volatility"
SYSTEMIC_CPI_WEIGHTS_DIR = SYSTEMIC_PRICES_OUTPUTS / "cpi_weights"


# Ensure all directories exist
directories = [
    FIGARO_RAW_DIR, FIGARO_PROCESSED_DIR,
    FIGARO_FULL_MATRIX_DIR, FIGARO_Z_MATRIX_DIR, FIGARO_Y_MATRIX_DIR, FIGARO_X_VECTOR_DIR, FIGARO_VA_MATRIX_DIR, FIGARO_A_MATRIX_DIR,
    EXIOBASE_RAW_DIR, EXIOBASE_PROCESSED_DIR,
    SEA_RAW_DIR, SEA_PROCESSED_DIR, 
    SHARED_DIR,
    GAS_PRICE_SHOCK_SRC, GAS_PRICE_SHOCK_NOTEBOOKS, GAS_PRICE_SHOCK_OUTPUTS,
    GAS_PRICE_SHOCK_DATA, GAS_PRICE_SHOCK_VIS,
    SYSTEMIC_PRICES_SRC, SYSTEMIC_PRICES_NOTEBOOKS, SYSTEMIC_PRICES_OUTPUTS,
    SYSTEMIC_PRICES_DATA, SYSTEMIC_PRICES_VIS,
    SYSTEMIC_Z_MATRIX_DIR, SYSTEMIC_A_MATRIX_DIR, SYSTEMIC_X_VECTOR_DIR, SYSTEMIC_Y_MATRIX_DIR, SYSTEMIC_FULL_MATRIX_DIR, SYSTEMIC_CPI_WEIGHTS_DIR,
    SYSTEMIC_UNWEIGHTED_IMPACTS_DIR, SYSTEMIC_WEIGHTED_IMPACTS_DIR, SYSTEMIC_VOLATILITY_DIR, SYSTEMIC_CPI_WEIGHTS_DIR
]

for directory in directories:
    directory.mkdir(parents=True, exist_ok=True)
    print(f"Ensured directory exists: {directory}")


# Mapping of Figaro sectors to NACE codes

NACE_DESCRIPTION_MAP = {
    "A01": "Crop and animal production, hunting and related service activities",
    "A02": "Forestry and logging",
    "A03": "Fishing and aquaculture",
    "B": "Mining and quarrying",
    "C10-C12": "Manufacture of food products, beverages and tobacco products",
    "C13-C15": "Manufacture of textiles, wearing apparel and leather products",
    "C16": "Manufacture of wood and of products of wood and cork, except furniture; manufacture of articles of straw and plaiting materials",
    "C17": "Manufacture of paper and paper products",
    "C18": "Printing and reproduction of recorded media",
    "C19": "Manufacture of coke and refined petroleum products",
    "C20": "Manufacture of chemicals and chemical products",
    "C21": "Manufacture of basic pharmaceutical products and pharmaceutical preparations",
    "C20_C21": "Manufacture of chemicals, chemical products, basic pharmaceutical, products and pharmaceutical preparations",
    "C22": "Manufacture of rubber and plastic products",
    "C23": "Manufacture of other non-metallic mineral products",
    "C24": "Manufacture of basic metals",
    "C25": "Manufacture of fabricated metal products, except machinery and equipment",
    "C26": "Manufacture of computer, electronic and optical products",
    "C27": "Manufacture of electrical equipment",
    "C28": "Manufacture of machinery and equipment n.e.c.",
    "C29": "Manufacture of motor vehicles, trailers and semi-trailers",
    "C30": "Manufacture of other transport equipment",
    "C31_C32": "Manufacture of furniture; other manufacturing",
    "C33": "Repair and installation of machinery and equipment",
    "D35": "Electricity, gas, steam and air conditioning supply",
    "E36": "Water collection, treatment and supply",
    "E37-E39": "Sewerage; waste collection, treatment and disposal activities; materials recovery; remediation activities",
    "F": "Construction",
    "G45": "Wholesale and retail trade and repair of motor vehicles and motorcycles",
    "G46": "Wholesale trade, except of motor vehicles and motorcycles",
    "G47": "Retail trade, except of motor vehicles and motorcycles",
    "H49": "Land transport and transport via pipelines",
    "H50": "Water transport",
    "H51": "Air transport",
    "H52": "Warehousing and support activities for transportation",
    "H53": "Postal and courier activities",
    "I": "Accommodation and food service activities",
    "J": "Information and communication",
    "J58": "Publishing activities",
    "J59_J60": "Motion picture, video & sound publishing; broadcasting",
    "J61": "Telecommunications",
    "J62_J63": "IT services & consultancy",
    "K64": "Financial service activities, except insurance and pension funding",
    "K65": "Insurance, reinsurance and pension funding, except compulsory social security",
    "K66": "Activities auxiliary to financial services and insurance activities",
    "L68": "Real estate activities",
    "M_N": "Professional, scientific and technical activities; administrative and support service activities",
    "M69_M70": "Legal & accounting; management consulting",
    "M71": "Engineering & testing",
    "M72": "Scientific R&D",
    "M73": "Advertising & market research",
    "M74_M75": "Other scientific & veterinary activities",
    "N77": "Rental & leasing",
    "N78": "Employment activities",
    "N79": "Travel & reservation services",
    "N80-N82": "Security, landscape, office admin",
    "N": "Administrative & support services",
    "M_N": "Professional, scientific and technical activities; administrative and support service activities",
    "O84": "Public administration and defence; compulsory social security",
    "P85": "Education",
    "Q": "Human health and social work activities",
    "R_S": "Arts, entertainment, recreation and other service activities",
    "T": "Activities of households as employers; undifferentiated goods- and services-producing activities of households for own use",
    "U": "Activities of extraterritorial organizations and bodies"
}


NACE_SHORT_DESCRIPTION_MAP = {
    "A01": "Crop and animal production (...)",
    "A02": "Forestry and logging",
    "A03": "Fishing and aquaculture",
    "B": "Mining and quarrying",
    "C10-C12": "Manufacture of food products (...)",
    "C13-C15": "Manufacture of textiles (...) and leather products",
    "C16": "Manufacture of wood and of products of wood (...)",
    "C17": "Manufacture of paper and paper products",
    "C18": "Printing and reproduction of recorded media",
    "C19": "Manufacture of coke and refined petroleum products",
    "C20": "Manufacture of chemicals and chemical products",
    "C21": "Manufacture of basic pharmaceutical products (...)",
    "C20_C21": "Manufacture of chemicals & pharmaceuticals",
    "C22": "Manufacture of rubber and plastic products",
    "C23": "Manufacture of other non-metallic mineral products",
    "C24": "Manufacture of basic metals",
    "C25": "Manufacture of fabricated metal products (...)",
    "C26": "Manufacture of computer, electronic and optical products",
    "C27": "Manufacture of electrical equipment",
    "C28": "Manufacture of machinery and equipment n.e.c.",
    "C29": "Manufacture of motor vehicles, trailers and semi-trailers",
    "C30": "Manufacture of other transport equipment",
    "C31_C32": "Manufacture of furniture; other manufacturing",
    "C33": "Repair and installation of machinery and equipment",
    "D35": "Electricity, gas, steam and air conditioning supply",
    "E36": "Water collection, treatment and supply",
    "E37-E39": "Sewerage; waste collection (...)",
    "F": "Construction",
    "G45": "Wholesale and retail trade (...) vehicles and motorcycles",
    "G46": "Wholesale trade, except of motor vehicles and motorcycles",
    "G47": "Retail trade, except of motor vehicles and motorcycles",
    "H49": "Land transport and transport via pipelines",
    "H50": "Water transport",
    "H51": "Air transport",
    "H52": "Warehousing and support activities for transportation",
    "H53": "Postal and courier activities",
    "I": "Accommodation and food service activities",
    "J": "Information and communication",
    "J58": "Publishing activities",
    "J59_J60": "Motion picture, video & sound publishing; broadcasting",
    "J61": "Telecommunications",
    "J62_J63": "IT services & consultancy",
    "K64": "Financial service activities (...)",
    "K65": "Insurance, reinsurance and pension funding(...)",
    "K66": "Activities auxiliary to financial services and insurance activities",
    "L68": "Real estate activities",
    "M_N": "Professional, scientific and technical activities (...)",
    "M69_M70": "Legal & accounting; management consulting",
    "M71": "Engineering & testing",
    "M72": "Scientific R&D",
    "M73": "Advertising & market research",
    "M74_M75": "Other scientific & veterinary activities",
    "N77": "Rental & leasing",
    "N78": "Employment activities",
    "N79": "Travel & reservation services",
    "N80-N82": "Security, landscape, office admin",
    "N": "Administrative & support services",
    "M_N": "Professional, scientific and technical activities; administrative and support service activities",
    "O84": "Public administration and defence; compulsory social security",
    "P85": "Education",
    "Q": "Human health and social work activities",
    "R_S": "Arts, entertainment, recreation and other service activities",
    "T": "Activities of households as employers (...)",
    "U": "Activities of extraterritorial organizations and bodies"
}

# Aggregation mapping for sectors

AGGREGATION_MAPPING_FIGARO_SYSTEMIC = {
    "N77": "N", 
    "N78": "N", 
    "N79": "N", 
    "N80-N82": "N",
    "Q86": "Q", 
    "Q87_Q88": "Q",
    "R90-R92": "R_S", 
    "R93": "R_S", 
    "S94": "R_S", 
    "S95": "R_S", 
    "S96": "R_S"
}

# CPI REGION MAPPINGS

# Full EU28 membership as of pre-Brexit (GB included)
EU28_COUNTRIES = [
    "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU", "IE",
    "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE", "GB"
]

# Ipsen et al. (2023): Core vs. Periphery
IPSEN_REGION_MAP = {
    "AT": "core", "BE": "core", "DK": "core", "FI": "core", "DE": "core",
    "FR": "core", "IE": "core", "IT": "core", "LU": "core", "NL": "core", "SE": "core", "GB": "core",
    "BG": "periphery", "CY": "periphery", "CZ": "periphery", "EE": "periphery",
    "ES": "periphery", "GR": "periphery", "HR": "periphery", "HU": "periphery",
    "LT": "periphery", "LV": "periphery", "MT": "periphery", "PL": "periphery",
    "PT": "periphery", "RO": "periphery", "SI": "periphery", "SK": "periphery"
}

# Geographic: North vs. South EU (approximate, incl. GB in North)
EU_NORTH_SOUTH_MAP = {
    "AT": "north", "BE": "north", "DE": "north", "DK": "north", "FI": "north",
    "FR": "north", "IE": "north", "LU": "north", "NL": "north", "SE": "north", "GB": "north",
    "BG": "south", "CY": "south", "CZ": "south", "EE": "north",
    "ES": "south", "GR": "south", "HR": "south", "HU": "south",
    "IT": "south", "LT": "north", "LV": "north", "MT": "south",
    "PL": "north", "PT": "south", "RO": "south", "SI": "south", "SK": "south"
}

# Geographic: West vs. East EU (approximate political-economic divide)
EU_WEST_EAST_MAP = {
    "AT": "west", "BE": "west", "DE": "west", "DK": "west", "FI": "west",
    "FR": "west", "IE": "west", "IT": "west", "LU": "west", "NL": "west", "SE": "west", "GB": "west",
    "BG": "east", "CY": "east", "CZ": "east", "EE": "east",
    "ES": "west", "GR": "east", "HR": "east", "HU": "east",
    "LT": "east", "LV": "east", "MT": "west", "PL": "east",
    "PT": "west", "RO": "east", "SI": "east", "SK": "east"
}

# Gerographic: Based on Louvain Clustering (2019)
CLUSTER_REGION_MAP_2019 = {
    "AT": "core", "BE": "core", "CH": "core", "DE": "core", "ES": "core", "FR": "core", "GB": "core", "IE": "core", "NL": "core",
    "AR": "global", "AU": "global", "BR": "global", "CA": "global", "CN": "global", "FIGW1": "global", "ID": "global",
    "IN": "global", "JP": "global", "KR": "global", "MX": "global", "SA": "global", "US": "global", "ZA": "global",
    "BG": "SEP", "CY": "SEP", "GR": "SEP", "HR": "SEP", "IT": "SEP", "MT": "SEP", "PT": "SEP", "RO": "SEP", "SI": "SEP", "TR": "SEP",
    "CZ": "NEP", "DK": "NEP", "EE": "NEP", "FI": "NEP", "HU": "NEP", "LT": "NEP", "LU": "NEP", "LV": "NEP",
    "NO": "NEP", "PL": "NEP", "RU": "NEP", "SE": "NEP", "SK": "NEP"
}


EXIOBASE_ROW_REGION_MAPPING = {
    "WA": "FIGW1",  # Rest of Asia
    "WE": "FIGW1",  # Rest of Europe
    "WF": "FIGW1",  # Africa
    "WL": "FIGW1",  # Latin America
    "WM": "FIGW1",  # Middle East
    "WP": "FIGW1",  # Pacific region
    "TW": "FIGW1"   # Taiwan
}

# Mapping of EXIOBASE sectors to NACE codes
EXIOBASE_TO_NACE_MAPPING = {
    "A_PARI": "A01", "A_WHEA": "A01", "A_OCER": "A01", "A_FVEG": "A01", "A_OILS": "A01",
    "A_SUGB": "A01", "A_FIBR": "A01", "A_OTCR": "A01", "A_CATL": "A01", "A_PIGS": "A01",
    "A_PLTR": "A01", "A_OMEA": "A01", "A_OANP": "A01", "A_MILK": "A01", "A_WOOL": "A01",
    "A_MANC": "A01", "A_MANB": "A01", "A_FORE": "A02", "A_FISH": "A03", "A_GASE": "B_gas",
    "A_OGPL": "B_gas", "A_COAL": "B_nongas", "A_COIL": "B_nongas", "A_ORAN": "B_nongas",
    "A_IRON": "B_nongas", "A_COPO": "B_nongas", "A_NIKO": "B_nongas", "A_ALUO": "B_nongas",
    "A_PREO": "B_nongas", "A_LZTO": "B_nongas", "A_ONFO": "B_nongas", "A_STON": "B_nongas",
    "A_SDCL": "B_nongas", "A_CHMF": "B_nongas", "A_PCAT": "C10-C12", "A_PPIG": "C10-C12",
    "A_PPLT": "C10-C12", "A_POME": "C10-C12", "A_VOIL": "C10-C12", "A_DAIR": "C10-C12",
    "A_RICE": "C10-C12", "A_SUGR": "C10-C12", "A_OFOD": "C10-C12", "A_BEVR": "C10-C12",
    "A_FSHP": "C10-C12", "A_TOBC": "C10-C12", "A_TEXT": "C13-C15", "A_GARM": "C13-C15",
    "A_LETH": "C13-C15", "A_WOOD": "C16", "A_WOOW": "C16", "A_PULP": "C17", "A_PAPR": "C17",
    "A_PAPE": "C17", "A_MDIA": "C18", "A_COKE": "C19", "A_REFN": "C19", "A_PLAS": "C20_C21",
    "A_PLAW": "C20_C21", "A_NFER": "C20_C21", "A_PFER": "C20_C21", "A_CHEM": "C20_C21",
    "A_RUBP": "C22", "A_GLAS": "C23", "A_GLAW": "C23", "A_CRMC": "C23", "A_BRIK": "C23",
    "A_CMNT": "C23", "A_ASHW": "C23", "A_ONMM": "C23", "A_NUCF": "C24", "A_STEL": "C24",
    "A_STEW": "C24", "A_PREM": "C24", "A_PREW": "C24", "A_ALUM": "C24", "A_ALUW": "C24",
    "A_LZTP": "C24", "A_LZTW": "C24", "A_COPP": "C24", "A_COPW": "C24", "A_ONFM": "C24",
    "A_ONFW": "C24", "A_METC": "C24", "A_FABM": "C25-C33", "A_MACH": "C25-C33",
    "A_OFMA": "C25-C33", "A_ELMA": "C25-C33", "A_RATV": "C25-C33", "A_MEIN": "C25-C33",
    "A_MOTO": "C25-C33", "A_OTRE": "C25-C33", "A_FURN": "C25-C33", "A_POWC": "D35",
    "A_POWG": "D35", "A_POWN": "D35", "A_POWH": "D35", "A_POWW": "D35", "A_POWP": "D35",
    "A_POWB": "D35", "A_POWS": "D35", "A_POWE": "D35", "A_POWO": "D35", "A_POWM": "D35",
    "A_POWZ": "D35", "A_POWT": "D35", "A_POWD": "D35", "A_GASD": "D35", "A_HWAT": "D35",
    "A_WATR": "E36", "A_RYMS": "E37-E39", "A_BOTW": "E37-E39", "A_INCF": "E37-E39",
    "A_INCP": "E37-E39", "A_INCL": "E37-E39", "A_INCM": "E37-E39", "A_INCT": "E37-E39",
    "A_INCW": "E37-E39", "A_INCO": "E37-E39", "A_BIOF": "E37-E39", "A_BIOP": "E37-E39",
    "A_BIOS": "E37-E39", "A_COMF": "E37-E39", "A_COMW": "E37-E39", "A_WASF": "E37-E39",
    "A_WASO": "E37-E39", "A_LANF": "E37-E39", "A_LANP": "E37-E39", "A_LANL": "E37-E39",
    "A_LANI": "E37-E39", "A_LANT": "E37-E39", "A_LANW": "E37-E39", "A_CONS": "F",
    "A_CONW": "F", "A_TDMO": "G45", "A_TDWH": "G46", "A_TDFU": "G47", "A_TDRT": "G47",
    "A_TRAI": "H49", "A_TLND": "H49", "A_TPIP": "H49", "A_TWAS": "H50", "A_TWAI": "H50",
    "A_TAIR": "H51", "A_TAUX": "H52", "A_PTEL": "H53", "A_HORE": "I", "A_COMP": "J",
    "A_FINT": "K64", "A_FINS": "K65", "A_FAUX": "K66", "A_REAL": "L68", "A_RESD": "M_N",
    "A_OBUS": "M_N", "A_MARE": "M_N", "A_PADF": "O84", "A_EDUC": "P85", "A_HEAL": "Q",
    "A_RECR": "R_S", "A_ORGA": "R_S", "A_OSER": "R_S", "A_PRHH": "T", "A_EXTO": "U"
}

GAS_FIGARO_MAPPING = {
    "C20": "C20_C21",
    "C21": "C20_C21",
    "J58": "J",
    "J59_J60": "J",
    "J61": "J",
    "J62_J63": "J",
    "M69_M70": "M_N",
    "M71": "M_N",
    "M72": "M_N",
    "M73": "M_N",
    "M74_M75": "M_N",
    "N77": "M_N",
    "N78": "M_N",
    "N79": "M_N",
    "N80-N82": "M_N",
    "N": "M_N",
    "Q86": "Q",
    "Q87_Q88": "Q",
    "R90-R92": "R_S",
    "R93": "R_S",
    "S94": "R_S",
    "S95": "R_S",
    "S96": "R_S",
}