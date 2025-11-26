# ✈️ SkyNet: Global Air Travel Analysis & Forecasting

**SkyNet** is a multidisciplinary data science project exploring the dynamics of international air travel to and from the United States from 1990 to the present. By enriching aviation data with global economic, demographic, and geographic indicators, this project aims to model historical trends, quantify the disruptive impact of COVID-19, and forecast future connectivity.

> **Long-Term Vision:** This project serves as a foundational sandbox for developing **Graph Neural Networks (GNNs)** to model the global air transportation network as a substrate for **epidemiological forecasting**, predicting the spread of infectious diseases based on passenger flow.

-----

## 💡 Key Insights & Findings

Through exploratory data analysis and hypothesis testing, several critical trends and data nuances have been uncovered:

### 1\. The "Data Bias" Discovery

We identified a critical discrepancy between U.S. government datasets. The "Domestic" T-100 dataset includes international flights but **only for U.S. carriers**. Comparing this against international "All Carrier" data revealed:

  * **Foreign Market Share:** There is a massive, persistent gap between total passengers and U.S.-carrier passengers, representing the market share of foreign airlines (e.g., AeroMexico, Air Canada).
  * **Data Break:** Post-2020, the "All Carrier" dataset for certain regions (Mexico, Canada) erroneously converges with U.S.-carrier data, signaling a failure in reporting foreign carrier data during the pandemic.

### 2\. Disparate Regional Recovery

The post-pandemic recovery is highly non-uniform:

  * **Africa:** Has remarkably **surpassed** pre-pandemic passenger volumes.
  * **North/South America:** Rapid "bounce-back" to pre-pandemic levels.
  * **Asia:** Remains significantly below trend, reflecting prolonged restrictions (e.g., China's Zero-COVID policy).
  * **Europe:** Has recovered summer peaks but shows deeper winter troughs, suggesting a structural change in seasonality.

### 3\. The "Net Balance" Signal

Analysis of inbound vs. outbound flows revealed a consistent 30-year surplus of \~16 million inbound passengers.

  * **Hypothesis:** This surplus likely represents **net immigration** and long-term visa holders (students, H-1B workers) rather than tourism (which nets to zero).
  * **Validation:** This hypothesis was strengthened by observing the **1997 Asian Financial Crisis**, where the net balance for Asia plummeted to zero, indicating a sudden halt in inbound economic migration.

-----

## 🔬 Research Roadmap

This project follows a progressive complexity curve, moving from statistical analysis to deep learning.

| Phase | Focus | Key Question | Status |
| :--- | :--- | :--- | :--- |
| **1** | **Exploratory Analysis** | What are the historical drivers (GDP, Population) of air travel? | ✅ Complete |
| **2** | **Predictive Modeling** | Can we quantify the "lost" traffic due to COVID-19 using counterfactual forecasting? | 🔄 In Progress |
| **3** | **Deep Learning** | Can an LSTM or MLP forecast route demand better than classical regressions? | 🔜 Next Step |
| **4** | **Network Science** | Can a **Graph Neural Network (GNN)** predict passenger flow (edge) or hub growth (node) by learning the network structure? | 🚀 Future Goal |

-----

## 📓 Repository Structure

The analysis is broken down into modular notebooks and scripts.

  * [**`domestic_and_international_travel_data_exploration.ipynb`**](https://www.google.com/search?q=./notebooks/domestic_and_international_travel_data_exploration.ipynb): The primary EDA notebook covering trends, carrier analysis, and the "Data Bias" discovery.
  * [**`international_incoming_vs_outgoing.ipynb`**](https://www.google.com/search?q=./notebooks/international_incoming_vs_outgoing.ipynb): Deep dive into the net passenger balance, migration signals, and regional disparities.
  * [**`seasonality.ipynb`**](https://www.google.com/search?q=./notebooks/seasonality.ipynb): Clustering airports and countries based on their seasonal travel profiles.
  * **`scripts/`**: Contains the Python ETL pipelines for downloading, cleaning, and enriching the raw data from Socrata, the World Bank, and the EIA.

-----

## 🛠️ Tech Stack & Data Sources

**Tools:**

  * **Data Processing:** Pandas, NumPy
  * **Visualization:** Seaborn, Matplotlib
  * **Machine Learning:** Scikit-Learn (Random Forest, K-Means), Prophet (Time-Series)
  * **Deep Learning:** PyTorch (Planned)

**Data Sources:**

  * **U.S. DOT T-100 Market Data:** Primary passenger volume (via Socrata API).
  * **World Bank Open Data:** GDP, Population, Inflation, Tourism arrivals.
  * **EIA:** Jet Fuel Prices.
  * **OurAirports:** Geospatial airport metadata.

-----

## 🚀 Collaboration

I am actively looking for collaborators

-----

## ⚙️ Setup

To reproduce this analysis:

```bash
# 1. Install mamba (recommended for speed)
conda install mamba -n base -c conda-forge

# 2. Create the environment
mamba env create -f environment.yml

# 3. Activate
conda activate airtravel
```
