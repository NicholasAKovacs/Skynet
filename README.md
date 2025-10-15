# Global Air Travel Analysis and Forecasting

This project performs an in-depth analysis of international air passenger traffic to and from the United States, spanning from 1990 to the present. The core goal is to understand the key drivers of air travel, model historical trends, and forecast future passenger volume. The analysis pays special attention to the significant impact of the COVID-19 pandemic on global travel patterns.

This repository serves as a personal project to develop and apply advanced data science and machine learning techniques, with a long-term vision of adapting this framework for epidemiological modeling.

![International Passenger Volume Over Time](./results/intl_flight_passengers_by_year_month.png)

## 📈 Project Goals

* **Explore Historical Trends**: Analyze how international passenger volume has evolved over the past three decades.
* **Enrich the Dataset**: Combine flight data with geographic, economic, and demographic data to create a comprehensive analytical dataset.
* **Time-Series Forecasting**: Build a model to forecast "expected" passenger volume and quantify the deviation caused by the COVID-19 pandemic.
* **Predictive Modeling**: Use machine learning models to identify the key features (e.g., GDP, population, continent) that predict passenger traffic on a given route.
* **Advanced Deep Learning**: Apply neural networks, and eventually Graph Neural Networks (GNNs), to model the entire air travel system as an interconnected network.

---

## 🗃️ Data Sources

This analysis is built upon a foundation of several rich, open-source datasets:

* **[U.S. DOT T-100 International Market Data](https://www.opendatanetwork.com/dataset/datahub.transportation.gov/xgub-n9bw)**: The primary source for monthly passenger counts on international routes to/from the United States. Accessed via the Socrata Open Data API.
* **[OurAirports Data](https://davidmegginson.github.io/ourairports-data/)**: A comprehensive database of global airports, used to enrich the flight data with geographic details like country codes, continents, and GPS coordinates.
* **[World Bank Open Data](https://data.worldbank.org/)**: Provides country-level, year-appropriate economic and demographic indicators, such as GDP and population. Accessed via the `wbgapi` Python package.

---

## 🛠️ Methodology & Workflow

1.  **Data Acquisition**: A Python script downloads decades of T-100 International Market data by year using the Socrata API and saves it locally as an efficient Parquet file.
2.  **Data Enrichment**:
    * Airport and country details (names, continents, regions) are merged into the main dataset.
    * Economic and demographic data (GDP, population, etc.) is fetched from the World Bank API for all relevant countries and years.
3.  **Data Cleaning**: The World Bank data is reshaped from a wide to a long format, and missing values are intelligently filled using a combination of interpolation and forward/backward fill on a per-country basis.
4.  **Exploratory Data Analysis (EDA)**: The enriched dataset is explored to identify trends, with key visualizations created to show passenger volume over time, both globally and broken down by continent.
5.  **Predictive Modeling**: (In Progress)
    * **Baseline Model**: A Random Forest Regressor is trained to predict passenger volume based on the enriched features.
    * **Time-Series Forecasting**: A model will be trained on pre-2020 data to forecast the expected traffic during the pandemic years.

---

## 🚀 Future Work

This project serves as a launchpad for more advanced analyses:

* **Advanced Time-Series Forecasting**: Implement a model using `Prophet` to include seasonality and external regressors (like GDP) for a more robust forecast.
* **Deep Learning**: Build a PyTorch-based Multi-Layer Perceptron (MLP) to predict passenger volume and compare its performance to tree-based models like XGBoost.
* **Graph Neural Networks (GNNs)**:
    * Incorporate US domestic flight data to build a complete, dense air travel graph.
    * Model airports as nodes and flight routes as edges.
    * Use a GNN to predict future traffic on a specific route (edge prediction) or identify emerging hub airports (node prediction).
* **Epidemiological Modeling**: The ultimate goal is to leverage this air travel network as a substrate to model the potential spread of infectious diseases, incorporating global influenza surveillance metrics (genomic, antigenic, and hospitalization data) from sources like the CDC and WHO.

---

## ⚙️ Setup

This project uses Python with a Conda environment. To set up the environment and run the scripts, you can use the following:

```bash
# It is recommended to use mamba for faster environment creation
conda install mamba -n base -c conda-forge

# Create the conda environment with the required packages
mamba env create -f environment.yml

# Activate the environment
conda activate airtravel