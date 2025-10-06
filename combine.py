import pandas as pd
from pathlib import Path

# Set the folder containing your CSV files
csv_folder = Path("C:/Users/danie/Nextcloud/Coding/Masterthesis-Burbach-Economics/part_gas_price_shock/outputs/weighted_impacts")
output_file = Path("C:/Users/danie/Nextcloud/Coding/Masterthesis/appendix_results/gas_price_shock_merged_weighted_impacts.xlsx") 
# Create an Excel writer
with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
    for csv_file in csv_folder.glob("*.csv"):
        # Read each CSV file
        df = pd.read_csv(csv_file)
        # Use the filename (without .csv) as the sheet name
        sheet_name = csv_file.stem[:31]  # Excel limits sheet names to 31 characters
        # Write to the Excel workbook
        df.to_excel(writer, sheet_name=sheet_name, index=False)

print(f"Combined Excel workbook saved as: {output_file.resolve()}")
