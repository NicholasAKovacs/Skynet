# Global Air Travel Analysis and Forecasting

This project explores the dynamics of international air travel to and from the United States, from 1990 to the present. It begins by building a rich dataset that combines passenger volume with country-level economic, demographic, and geographic data to analyze historical trends and identify key drivers of travel. The analysis places a strong emphasis on quantifying the impact of the COVID-19 pandemic.

From this foundation, the project serves as an open and collaborative space to apply a wide range of analytical techniques. It provides a real-world sandbox for anyone looking to develop their skills, progressing from classical machine learning and time-series forecasting to advanced deep learning architectures, including Graph Neural Networks (GNNs) for network science.

[Explore the Data in `data_intro.ipynb`](./notebooks/data_intro.ipynb)

![Top airports and Trends](./results/data_intro/figures/top_airports_and_trends.png)

![Overall Passenger Volume](./results/data_intro/figures/total_passengers_per_month_per_continent_with_forecast.png)


## ❓ Initial Observations & Next Questions

The initial time-series analysis reveals several compelling trends, particularly regarding the differential impact and recovery from the COVID-19 pandemic across various regions. These observations serve as the foundation for the next stage of deeper, more targeted analysis.

### 1. Disparate Regional Recoveries
The post-2020 recovery has not been uniform across the globe. Our forecasts highlight several distinct patterns:

* **Accelerated Growth**: Passenger volume to and from **Africa** has not only recovered but has significantly surpassed its pre-pandemic forecast.
* **Rapid Recovery**: **North and South America** demonstrated a swift bounce-back and have largely returned to their forecasted levels.
* **Lagging Recovery**: **Asia and Oceania** are showing the slowest recovery, still well below their pre-pandemic trend lines.
* **Altered Seasonality**: **Europe** appears to have recovered to its forecasted summer peaks, but its traditional winter off-season troughs are now much deeper than before. Also, it does not seem **Asia and Oceania** have returned to their forecasted seasonality. 

This leads to our primary question: **What factors explain this significant disparity in recovery rates and patterns between continents?**

### 2. Exploring Potential Drivers
To understand the "why" behind these observations, the next phase of this project will focus on integrating new data to explore several hypotheses:

* **Travel Restrictions**: Different countries imposed international travel bans of varying severity and duration. Can we find and integrate a dataset on these restrictions to see how they correlate with the observed recovery lags?
* **Economic Factors**: Are the existing economic indicators (GDP, population) sufficient to explain these trends? What happens if we incorporate additional metrics, such as a country's reliance on tourism, inflation rates, or exchange rates?
* **Network Dynamics**: How do domestic travel patterns influence international hubs? Would incorporating **U.S. domestic flight data** help explain why certain U.S. gateway airports recovered faster than others?
* **Travel Costs**: How did airfare evolve during this period? Could a dataset of average ticket prices help explain the suppression or recovery of travel demand to certain regions?

## 📈 Project Goals

* **Explore Historical Trends**: Analyze how international passenger volume has evolved over the past three decades.
* **Enrich the Dataset**: Combine flight data with geographic, economic, and demographic data to create a comprehensive analytical dataset.
* **Time-Series Forecasting**: Build a model to forecast "expected" passenger volume and quantify the deviation caused by the COVID-19 pandemic.
* **Predictive Modeling**: Use machine learning models to identify the key features (e.g., GDP, population, continent) that predict passenger traffic on a given route.
* **Advanced Deep Learning**: Apply neural networks, and eventually Graph Neural Networks (GNNs), to model the entire air travel system as an interconnected network.

---

## 🔬 Research Questions

This project aims to answer a series of questions, progressing from broad exploratory analysis to specific, advanced modeling tasks that build upon one another.

### 1. Foundational & Exploratory Analysis
*What are the fundamental patterns and major events in the data?*

* **Long-Term Trends**: What are the historical trends in international air passenger traffic to and from the United States since 1990?
* **Key Actors**: Which U.S. and foreign airports are the most significant gateways? Which airlines carry the most passengers?
* **Seasonality & Geography**: How does passenger volume vary seasonally and across different continents?
* **Pandemic Impact & Recovery**: Which continents or countries demonstrated the most resilience during the COVID-19 pandemic, returning to pre-pandemic volumes the fastest? Conversely, which have shown the slowest recovery? Are there any regions where traffic has not just recovered but exceeded pre-pandemic trends?

---

### 2. Predictive Modeling & Causal Inference
*Can we build models to predict outcomes and understand the key drivers of air travel?*

* **Pandemic Counterfactual**: **By how much did the actual passenger volume deviate from a pre-pandemic forecast?** Using a time-series model (e.g., Prophet or a Bayesian model) trained on 1990-2019 data, what was the full range of plausible "expected" passenger volumes for 2020-2024?
* **Feature Importance**: Using tree-based models (e.g., Random Forest, XGBoost), which factors—economic (GDP, population), geographic (continent), or temporal (month)—are the most powerful predictors of passenger volume on a given route?
* **Hierarchical Effects**: How does the relationship between a country's economic indicators and its passenger traffic vary across different continents? A Bayesian hierarchical model can provide robust estimates for these varying effects while quantifying our uncertainty.

---

### 3. Deep Learning for Time-Series Analysis
*Can advanced neural network architectures capture more complex patterns in the data?*

* **Forecasting with RNNs**: How accurately can a Recurrent Neural Network (RNN) or LSTM model forecast future demand for a specific route (e.g., ATL-LHR) compared to classical models, by learning from the historical sequence of monthly passenger data?
* **Pattern Recognition with CNNs**: Can a 1D Convolutional Neural Network (CNN) be trained to automatically classify the "seasonality profile" of a given route (e.g., 'summer-peaking', 'winter holiday spike', 'stable business route') by learning the characteristic shapes in its time-series data?

---

### 4. Network Science with Graph Neural Networks (GNNs)
*What can we learn by modeling the entire air travel system as an interconnected graph?*


* **Node-Level Prediction**: Can a GNN predict which airports (nodes) are most likely to increase in importance and passenger volume based not just on their own history, but on the growth of the airports they are connected to?
* **Edge-Level Prediction**: Can a GNN predict the future passenger traffic on a specific route (an edge) by learning from the features of the two connected airports and the overall structure of the network?
* **Community Detection**: What are the natural clusters or "communities" of airports within the global travel network? Do these align with geographic continents or economic trade blocs?

---

### 5. Future Vision: Epidemiological Modeling
*Can this air travel network be used as a substrate for modeling infectious disease spread?*

* The ultimate goal is to leverage this passenger flow data to forecast the dissemination pathways of emerging pathogens. By combining the air travel graph with genomic, antigenic, and clinical surveillance data (e.g., country-level influenza-like illness rates), can a model predict the most likely routes of viral spread and identify countries at highest risk?

---

## 🗃️ Data Sources

This analysis is built upon a foundation of several rich, open-source datasets:

* **[U.S. DOT T-100 International Market Data](https://www.opendatanetwork.com/dataset/datahub.transportation.gov/xgub-n9bw)**: The primary source for monthly passenger counts on international routes to/from the United States. Accessed via the Socrata Open Data API.
* **[OurAirports Data](https://davidmegginson.github.io/ourairports-data/)**: A comprehensive database of global airports, used to enrich the flight data with geographic details like country codes, continents, and GPS coordinates.
* **[World Bank Open Data](https://data.worldbank.org/indicator?tab=all)**: Provides country-level, year-appropriate economic and demographic indicators, such as GDP and population. Accessed via the `wbgapi` Python package.

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

## 🚀 Future Work & Collaboration

The roadmap below outlines several exciting avenues for future development, progressing from data enrichment to cutting-edge deep learning applications.

### 1. Data Expansion & Integration
To build a powerful model, we need a comprehensive dataset. A primary goal is to integrate additional data sources for a multi-faceted view of global travel, its drivers, and its potential role in the international transmission of pathogens like influenza.

* **Build a Complete U.S. Network**: Incorporate **U.S. domestic flight data** from the BTS to complement the international data, creating a complete and dense air travel graph for the United States.
* **Create a Global Travel Graph**: Expand beyond U.S.-centric routes by integrating **global international flight data** from sources like OpenSky Network to model the entire worldwide system.
* **Incorporate Land & Sea Travel**: Add data on cross-border travel at **U.S. land ports and seaports** to capture other major modes of international transit.
* **Add Richer Indicators**: Integrate more diverse datasets from the **World Bank Open Data** and other sources, such as data on international trade, tourism expenditures, fuel prices, and global connectivity metrics.

### 2. Advanced Predictive Modeling
This involves moving beyond baseline models to apply more sophisticated techniques for forecasting and inference, providing excellent practice for anyone looking to sharpen their ML skills.

* **Time-Series Forecasting**: Implement a robust forecasting model using **`Prophet`** or Bayesian methods to include seasonality and external regressors (like GDP) for a more accurate counterfactual analysis of the pandemic's impact.
* **Gradient Boosting Models**: Utilize powerful tree-based models like **XGBoost** or **LightGBM** to identify the most important features driving passenger volume and benchmark their performance.
* **Deep Learning with PyTorch**: Build and train a **Multi-Layer Perceptron (MLP)** to predict passenger volume, providing hands-on practice with core PyTorch concepts on large-scale tabular data.

### 3. Network Science with Graph Neural Networks (GNNs)
The most advanced modeling goal is to treat the entire air travel system as a complex, interconnected graph to uncover network effects.

* **Graph Construction**: Model airports as **nodes** (with features like country, GDP, and passenger volume) and flight routes as **edges** (with features like passenger flow and number of carriers).
* **Predictive Tasks**: Use a GNN (e.g., with PyTorch Geometric) to tackle advanced problems such as:
    * **Edge Prediction**: Forecast future passenger traffic on a specific route.
    * **Node Prediction**: Identify airports that are likely to grow in importance as global hubs.

### 4. Capstone Application: Epidemiological Modeling
The ultimate long-term vision is to leverage this global travel network as a substrate for modeling infectious disease spread, perfectly merging this project with real-world public health challenges.

* Integrate global **influenza surveillance data** (genomic, antigenic, and clinical metrics like ILI rates and hospitalizations) from sources like the CDC and WHO.
* Build a model that uses the air travel graph to forecast the most likely pathways of viral dissemination and identify countries at the highest risk from an emerging strain.

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