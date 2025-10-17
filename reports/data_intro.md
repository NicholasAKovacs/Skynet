# Work in progress -
# Summary of Findings: International Air Travel Analysis

This document summarizes the key insights and trends discovered from the exploratory data analysis of the U.S. DOT T-100 International Market dataset, spanning from 1990 to 2024.

---

## 1. Overall Passenger Volume Trends

The most striking feature of the dataset is the clear historical trend in passenger volume, which can be broken down into three distinct eras:

* **Steady Growth (1990-2019)**: International air travel saw consistent growth for three decades, with predictable seasonal peaks during the summer months.
* **The COVID-19 Collapse (2020)**: The pandemic caused an immediate and unprecedented collapse in air travel, with passenger volume dropping to levels not seen since the early 1990s.
* **Rapid Recovery (2021-Present)**: Following the initial collapse, the industry has demonstrated a remarkably strong and rapid recovery, though the trajectory varies significantly by region.

![Overall Passenger Volume](../results/data_intro/figures/total_passengers_per_month_per_continent.png)

---

## 2. Analysis of Top Carriers

An analysis of the top 10 carriers by total passenger volume reveals the significant impact of industry consolidation over the past two decades.

* **Market Dominance**: The market is heavily dominated by major U.S. carriers like American Airlines (AA), United Airlines (UA), and Delta Air Lines (DL).
* **Impact of Mergers**: The decline of once-major carriers like Northwest (NW), Continental (CO), and US Airways (US) is clearly visible, with their market share being absorbed by their acquiring airlines around 2010-2013.

![Yearly Passengers by Carrier](../results/data_intro/figures/top_10_carriers_stacked_area.png)

---

## 3. Geographic & Regional Insights

Breaking down the data by continent reveals significant differences in market size and recovery patterns.

* **Europe and North America (non-U.S.)** remain the largest markets for international travel to and from the United States.
* **Differing Pandemic Recoveries**:
    * Travel to/from **Africa** has not only recovered but has surpassed its pre-pandemic passenger volume, showing strong growth.
    * Travel to/from **Europe** is demonstrating a slower, more gradual recovery.
    * Travel to/from **North American** destinations (primarily Mexico and the Caribbean) showed the fastest initial bounce-back in mid-2020.

Dashboards for each continent provide a more detailed breakdown of the top airports and carriers for that specific region.

* [Dashboard for Europe](../results/data_intro/figures/dashboard_Europe.png)
* [Dashboard for Asia](../results/data_intro/figures/dashboard_Asia.png)
* [Dashboard for North America](../results/data_intro/figures/dashboard_NA.png)

---

## 4. Key Takeaways

* The international air travel market has shown remarkable long-term growth and resilience.
* The COVID-19 pandemic represents the single largest disruption in the history of modern air travel, with clear and dramatic effects on the data.
* Recovery from the pandemic has not been uniform, with different global regions demonstrating distinct trajectories influenced by local factors and travel restrictions.

![Top airports and Trends](../results/data_intro/figures/top_airports_and_trends.png)