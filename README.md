# ✈️ SkyNet: Global Air Travel Analysis & Forecasting

> **Project Origin:** This project was initiated in October 2025 during the U.S. government shutdown furlough. It continues to be actively developed as a personal research project in my free time.

**SkyNet** models international air travel to/from the United States (1990–Present) by enriching aviation data with global economic and demographic indicators. The project quantifies the impact of COVID-19 and forecasts future connectivity.

> **Vision:** A sandbox for developing **Graph Neural Networks (GNNs)** to model the global transportation network as a substrate for **epidemiological forecasting** (predicting disease spread via passenger flow).

---

## 💡 Key Insights

* **Data Bias Discovery:** Uncovered a critical gap between U.S. "Domestic" and "All Carrier" datasets, revealing that foreign carrier data is significantly underreported post-2020.
* **Asymmetric Recovery:** Post-pandemic recovery is non-uniform. **Africa** has surpassed pre-pandemic volumes, while **Asia** remains below trend due to prolonged restrictions.
* **The "Net Balance" Signal:** Identified a consistent 30-year surplus of ~16M inbound passengers, correlating strongly with economic migration events (e.g., the 1997 Asian Financial Crisis) rather than tourism.
* **Data Note:** *The raw dataset contains artifacts where origin and destination are identical; these are handled in the cleaning pipeline.*

---

## 🔬 Research Roadmap

| Phase | Focus | Status |
| --- | --- | --- |
| **1** | **Exploratory Analysis** (GDP/Pop drivers, Bias detection) | ✅ Complete |
| **2** | **Predictive Modeling** (Counterfactual COVID-19 forecasting) | 🔄 In Progress |
| **3** | **Deep Learning** (LSTM/MLP vs. Classical Regression) | 🔜 Next Step |
| **4** | **Network Science** (GNNs for node/edge prediction) | 🚀 Future Goal |

---

## 📓 Repository Structure

* **[`domestic_and_international_travel_data_exploration.ipynb`](notebooks/domestic_and_international_travel_data_exploration.ipynb)**: Primary EDA, trend analysis, and bias discovery.
* **[`international_incoming_vs_outgoing.ipynb`](notebooks/international_incoming_vs_outgoing.ipynb)**: Analysis of net passenger deficits and migration signals.
* **[`seasonality.ipynb`](notebooks/seasonality.ipynb)**: Clustering airports by seasonal profiles (e.g., Summer Peak vs. Constant).

---

## 🛠️ Tech Stack

* **Core:** Python, Pandas, NumPy, NetworkX
* **Viz:** Seaborn, Matplotlib
* **ML/DL:** Scikit-Learn, Prophet, PyTorch, PyTorch Geometric
* **Data:** U.S. DOT T-100, World Bank Open Data, OurAirports

---

## ⚙️ Setup

```bash
# Install and activate environment
conda install mamba -n base -c conda-forge
mamba env create -f environment.yml
conda activate airtravel

```