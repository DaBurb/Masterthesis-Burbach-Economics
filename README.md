# From Sectoral Price Shocks to Overall Inflation: Insights from an Input-Output Perspective

This repository contains the complete codebase and data processing pipeline for the master's thesis of Daniel Leo Burbach (2025). The thesis investigates how sector specific shocks propagate throughout the economy and impact overall inflation, specifically for the EU28. The use of a modified Leontief price model, an input-output framework, allows for a detailed analysis of the transmission mechanisms of price shocks across different sectors and countries.

The approach is rooted in a Post-Keynesian perspective, which bridges the gap between microeconomic triggers and the aggregate, macro-economic outcomes and explores two main empirical questions:

1. **Which sectors are systemically significant for inflation transmission in the EU?**
2. **How did imported gas price shocks contribute to inflation across EU countries and sectors post-2021?**

Analyses are based mainly on **Eurostat FIGARO Input-Output Tables**, accompanied by **World Input Output Database (WIOD)**, more accurately its complementary dataset called **Socioeconomic Accounts (SEA)** for its producer price data, and **EXIOBASE3** (disaggregation of natural gas extraction and mining and quarrying sector).

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

To fully reproduce the results and analyses in this repository, follow these steps:

### 1. Clone the Repository

```bash
git clone https://github.com/DaBurb/Masterthesis-Burbach-Economics
cd Masterthesis-Burbach-Economics
```


### 2. Install Dependencies

Ensure you have Python 3.10+ installed, then create a virtual environment and install the required packages:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```


### 3. Download and Process Data

Run the shared preprocessing script to download and process the FIGARO data:

```bash
python shared/shared_main.py
```

This will create the necessary preprocessed matrices in the `shared/data/figaro/processed/` directory.


### 4. Run Analytical Parts

To run the analyses, execute the main scripts for each part:

```bash
# For Systemically Significant Prices
python part_systemically_significant_prices/src/systemic_main.py
# For Gas Price Shock Analysis
python part_gas_price_shock/src/gas_main.py
```






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
  Displays the CPI-weighted contribution of each (Country, Sector) pair to inflation, ordered by descending impact overall impact by country (x-axis).

- **Louvain Community Detection:**  
  Applies community detection to the endogenous impact matrix (before CPI-weighting) to identify clusters of countries or sectors that are more connected in the endogenous price system. 

- **Boxplots of Sectoral Impact Distribution:**  
  Shows the spread of each sector’s inflation contribution across EU countries.

- **Pareto Charts (Cumulative Shares):**  
  Illustrates how much of the total inflation impact is accounted for by the top-ranked sectors.

- **Temporal Dynamics:**  
    Analyzes how the sectoral contributions to inflation have evolved over time.

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

- **CPI-Weighted Inflation Impact on Countries (Stacked Bar):**  
  Shows how much of the total inflation impact is borne by each EU country when the gas price shock propagates through the production network.

- **Impact by Producing Country:**  
  Aggregates sectoral contributions by the country of origin, highlighting which countries' industries were the primary endogenous transmitters of inflationary pressure.

- **Heatmaps of Forward Linkages:**  
  Displays the intensity of forward linkages from the disaggregated natural gas sector, identifying key exposure channels.

- **Top-N Endogenous Sector Effects of Country:**  
  Visualizes which specific country-sector combinations were most impactful, using CPI-weighted metrics.

- **NOTE:**  
  The underlying data is divided into including domestic and excluding domestic gas extraction sectors. The focus in the thesis lies on imports, so the domestic sector is excluded in the main analysis. However, the domestic sector is included in the visualizations.


### How to Run

From the project root:


```bash
cd part_gas_price_shock/visualizations
jupyter lab
```

Then open `visualization.ipynb` and execute the cells.

---

## Data Sources

- Eurostat FIGARO input–output tables ([link](https://ec.europa.eu/eurostat/web/esa-supply-use-input-tables)) © Eurostat, licensed under the European Union Open Data Portal License.
- EXIOBASE v3 multi-regional input–output database ([link](https://www.exiobase.eu/)).
- WIOD SEA data ([link](https://www.rug.nl/ggdc/valuechain/wiod/)).

---

## Methodological Tools & Software


### `python-louvain`

> **Aynaud, T.** (2020). *python-louvain 0.16: Louvain algorithm for community detection*.  
> Available at: [https://github.com/taynaud/python-louvain](https://github.com/taynaud/python-louvain)  
> Based on:  
> Blondel, V.D., Guillaume, J.L., Lambiotte, R., & Lefebvre, E. (2008). *Fast unfolding of communities in large networks*. *Journal of Statistical Mechanics: Theory and Experiment*, 2008(10), P10008. [https://doi.org/10.1088/1742-5468/2008/10/P10008](https://doi.org/10.1088/1742-5468/2008/10/P10008)

### `pymrio`

> **Stadler, K.** (2021). *Pymrio – A Python-Based Multi-Regional Input–Output Analysis Toolbox*.  
> *Journal of Open Research Software*, 9(1), 8. [https://doi.org/10.5334/jors.251](https://doi.org/10.5334/jors.251)

### `networkx`

> **Hagberg, A.A., Schult, D.A., & Swart, P.J.** (2008). *Exploring network structure, dynamics, and function using NetworkX*.  
> In *Proceedings of the 7th Python in Science Conference (SciPy2008)*, pp. 11–15.  
> [https://conference.scipy.org/proceedings/scipy2008/paper_2/](https://conference.scipy.org/proceedings/scipy2008/paper_2/)

---

## Disclaimer: Use of Generative AI

Generative AI assissted in increasing code efficiency and annotating this source-code.

---

## Citation

This repository accompanies the master's thesis:

**Daniel Leo Burbach (2025)**  
*From Sectoral Price Shocks to Overall Inflation: Insights from an Input–Output Perspective*  
*Master’s Thesis, M.A. Arbeit, Wirtschaft, Gesellschaft – Ökonomische und Soziologische Studien*,  
University of Hamburg

If you use this code or results in your own work, please cite the thesis appropriately.
