# From Sectoral Price Shocks to Overall Inflation: Insights from an Input-Output Perspective

This repository contains the complete codebase and data processing pipeline for the master's thesis of Daniel Leo Burbach (2025). The thesis investigates how sector specific shocks propagate throughout the economy and impact overall inflation, specifically for the EU28. The use of a modified Leontief price model, an input-output framework, allows for a detailed analysis of the transmission mechanisms of price shocks across different sectors and countries.

The approach is rooted in a Post-Keynesian perspective, which bridges the gap between microeconomic triggers and the aggregate, macro-economic outcomes and explores two main empirical questions:

1. **Which sectors are systemically significant for inflation transmission in the EU?**
2. **How did imported gas price shocks contribute to inflation across EU countries and sectors post-2021?**

Analyses are based mainly on Eurostat FIGARO data, accompanied by World Input Output Database (price data) and EXIOBASE3 (disaggregation of natural gas extraction and mining and quarrying sector).

---

## Project Structure

The project is divided into two analytical parts:

## Shared Infrastructure (`shared/`)

This module contains all foundational tools used across both analytical parts.

### Key Components
- **`config.py`**: Defines all directory paths, filenames, mappings, and constants used throughout the project.
- **`preprocessing.py`**: Loads and preprocesses raw FIGARO input-output data, extracts submatrices (`Z`, `Y`, `X`, `VA`), applies aggregation, and adds gross output.
- **`aggregation.py`**: Sector mapping utilities (e.g., NACE → macro sectors).
- **`data_loader.py`**: Loads preprocessed FIGARO matrices (e.g., full, aggregated).
- **`extraction.py`**: Extracts quadrant matrices (`Z`, `Y`, `X`, etc.) from raw or aggregated data.
- **`cpi_weights.py`**: Computes CPI weighting schemes per country or region.
- **`technical_coefficients.py`**: Calculates Leontief `A` matrix from `Z` and `X`.

### Entry Point
- **`shared_main.py`**: First script to run. Downloads and processes FIGARO data into a modular, reusable format for both analysis parts.

---

## Part I: Systemically Significant Prices (`part_systemically_significant_prices/`)

This analysis identifies EU sectors that systematically amplify inflation shocks using volatility data and input-output propagation.

### Pipeline Scripts (`src/`)
- **`systemic_main.py`**: Main pipeline. Loads data, aggregates sectors, computes CPI weights, shock propagation, and generates visualizations.
- **`sea_loader.py`**: Downloads and loads WIOD SEA Excel data containing interindustry price indices.
- **`sea_processing.py`**: Processes SEA data, calculates sector-level volatility from yearly price index changes, and maps SEA to FIGARO countries.
- **`analyze_unweighted_shocks.py`**: Propagates volatility-based exogenous sectoral shocks through the input-output system without applying CPI weights.
- **`figaro_preprocessing.py`**: Adds CPI weights to FIGARO matrices based on household consumption.

---

## Part II: Gas Price Shock Analysis (`part_gas_price_shock/`)

This analysis quantifies the contribution of post-2021 natural gas price increases to EU inflation.

### Pipeline Overview
- **`gas_main.py`**: Loads FIGARO and EXIOBASE3 data to isolate the gas-extracting sector, constructs Leontief model, applies gas-specific cost shock.
- **`exiogas_loader.py`**: Prepares and filters EXIOBASE3 satellite account data to distinguish natural gas from general mining.
- **`shock_application.py`**: Injects the shock into the Leontief system, calculates resulting price effects.
- **`plotting.py`**: Generates visualizations such as heatmaps, country-sector breakdowns, and flow diagrams.

---

## Outputs

Each part saves outputs in a dedicated folder:
- **`data/figaro/processed/`** – Preprocessed input-output matrices.
- **`systemically_significant_prices/outputs/`** – Volatility shock results and weighted impacts on inflation.
- **`gas_price_shock/outputs/`** – Gas price shock simulation results and weighted impacts on inflation.

---

## Reproducibility

To reproduce results:
1. Run `shared_main.py` to prepare the base data.
2. Run `systemic_main.py` or `gas_main.py` depending on the analysis.
3. Output files and plots are stored under `/output`.

## Visualizaitons of Results

For the visualization of results, two Jupyter notebooks `visualization.ipynb` can be used, located in each parts respective `/visualizations subfolder`. They contain code to generate various plots and graphical visualizations based on the processed data.

## Visualization Notebook: Systemically Significant Prices

The `visualization.ipynb` notebook located in `part_systemically_significant_prices/visualizations/` provides manual visual exploration of the CPI-weighted and unweighted sectoral inflation impact results across EU countries.

It builds on outputs generated by `systemic_main.py` and enables the inspection of direct vs. indirect price effects, sectoral relevance, and country-level disparities.

### Key Visualizations Included

- **Volatility vs. Forward Linkages (Scatterplot):**  
  Compares each sector's WIOD SEA price volatility to its forward linkages (column sums of the Leontief A matrix). Gross output and CPI-weighted variants are included.

- **Top Inflation-Contributing Sectors (Bar Charts):**  
  Ranks sectors by total CPI-weighted impact across all EU28 countries. Both direct and indirect effects are shown.

- **Country–Sector Impact Heatmaps:**  
  Displays the CPI-weighted contribution of each (Country, Sector) pair to inflation, ordered by descending impact.

- **Boxplots of Sectoral Impact Distribution:**  
  Shows the spread of each sector’s inflation contribution across EU countries. Helps identify sectors with consistently high impact.

- **Pareto Charts (Cumulative Shares):**  
  Illustrates how much of the total inflation impact is accounted for by the top-ranked sectors.

- **Temporal Dynamics (Optional Extension):**  
  Placeholder included for multi-year analysis if CPI-weighted impacts are available over time.

### How to Run

From the project root:


```bash
cd part_systemically_significant_prices/visualizations
jupyter lab
```

Then open `visualization.ipynb` and execute the cells.


## Visualization Notebook: Gas Price Shock Analysis

The `visualization.ipynb` notebook located in `part_gas_price_shock/visualizations/` provides manual visualizations of the inflationary effects resulting from the post-2021 gas price shock, as simulated through the input–output price model.

It builds on outputs generated by `gas_main.py` and allows inspection of how the shock propagates across sectors, producing countries, and destination countries.

### Key Visualizations Included

- **CPI-Weighted Inflation Impact by Destination Country (Stacked Bar):**  
  Shows how much of the total inflation impact is borne by each EU country when the gas price shock propagates through the production network.

- **Impact by Producing Country:**  
  Aggregates sectoral contributions by the country of origin, highlighting which countries' exports were the primary transmitters of inflationary pressure.

- **Top Sectoral Contributors (Bar Charts):**  
  Highlights the sectors with the highest total inflation contribution across the EU28. Includes breakdowns of direct vs. indirect effects.

- **Heatmaps of Forward Linkages:**  
  Displays the intensity of forward linkages from the disaggregated natural gas sector, identifying key exposure channels.

- **Top-N Sector/Country Combinations:**  
  Visualizes which specific country-sector combinations were most impactful, using CPI-weighted metrics.

- **Impact Over Time (Optional Extension):**  
  Placeholder included for visualizing how shock effects evolve from 2010 to 2022 if year-specific simulations are available.

### How to Run

From the project root:


```bash
cd part_gas_price_shock/visualizations
jupyter lab
```

Then open `visualization.ipynb` and execute the cells.


---

## Citation

This repository accompanies the master's thesis:

**Daniel Leo Burbach (2025)**  
*From Sectoral Price Shocks to Overall Inflation: Insights from an Input–Output Perspective*  
*Master’s Thesis, M.A. Arbeit, Wirtschaft, Gesellschaft – Ökonomische und Soziologische Studien*,  
University of Hamburg

If you use this code or results in your own work, please cite the thesis appropriately.
