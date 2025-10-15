import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

parquet_path = "../data/T100_International/final_enriched_data.parquet"
df = pd.read_parquet(parquet_path)

df.info()

# --- 2. Data Cleaning & Type Conversion ---
# Convert columns that should be numbers from text to numeric types
# errors='coerce' will turn any values that can't be converted into NaN (missing)
numeric_cols = ['year', 'month', 'usg_apt_id', 'usg_wac', 'fg_apt_id', 
                'fg_wac', 'airlineid', 'carriergroup',  'scheduled', 
                'charter', 'total']
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Convert date column to datetime objects
df['data_dte'] = pd.to_datetime(df['data_dte'])

# Drop rows with missing values in key columns after conversion - not needed
df.dropna(subset=numeric_cols, inplace=True)
df.info()

# --- 3. Basic Statistics ---
print("\n--- 2. Summary Statistics for Numerical Columns ---")
# .describe() gives you the count, mean, standard deviation, min, max, etc.
print(df[numeric_cols].describe())


# --- 4. Value Counts ---
print("\n--- 3. Top 15 US Gateway Airports by Number of Routes ---")
print(df['usg_apt'].value_counts().head(15))

print("\n--- 4. Top 15 Carriers by Number of Routes ---")
print(df['carrier'].value_counts().head(15))


# --- 5. Grouped Analysis ---
print("\n--- 5. Top 10 Carriers by Total Passengers Transported ---")
# Group by carrier, sum the 'total' passengers, sort, and show the top 10
total_pax_by_carrier = df.groupby('carrier')['total'].sum().sort_values(ascending=False)
print(total_pax_by_carrier.head(10))

##################################################

df['year_month'] = df['data_dte'].dt.to_period('M')

# --- Visualization Script ---
print("\n--- Visualizing Total Passengers Over Time with a Line Plot ---")

# Group data by year_month
pax_by_year_month = df.groupby(['year_month'])['total'].sum().reset_index()

# Convert the 'year_month' period object to a string for easier plotting
pax_by_year_month['year_month'] = pax_by_year_month['year_month'].astype(str)


# (Assume 'pax_by_year_month' DataFrame is already created and sorted)

# --- Create the plot ---
plt.figure(figsize=(15, 7))

# The lineplot call is correct
sns.lineplot(data=pax_by_year_month, x='year_month', y='total')

# --- CORRECTED PART: Customize the x-axis ticks ---
# 1. Get the unique x-axis labels that seaborn is plotting
x_labels = pax_by_year_month['year_month'].unique()

# 2. Find the position (index) of each 'January' label in that unique list
tick_positions = []
tick_labels = []
for index, label in enumerate(x_labels):
    # Check if the month is January ('-01')
    if '-01' in label:
        tick_positions.append(index)
        tick_labels.append(label[:4]) # Just show the year 'YYYY'

# 3. Apply the corrected ticks
plt.xticks(ticks=tick_positions, labels=tick_labels, rotation=45, ha='right')

# --- Add labels and title ---
plt.title('Total International Passengers per Month by Continent')
plt.xlabel('Date')
plt.ylabel('Total Passengers')
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()

#########################################################
#########################################################

# Group data by year_month
pax_by_year_month = df.groupby(['year_month', 'fg_continent'])['total'].sum().reset_index()

# Convert the 'year_month' period object to a string for easier plotting
pax_by_year_month['year_month'] = pax_by_year_month['year_month'].astype(str)

# (Assume 'pax_by_year_month' DataFrame is already created and sorted)

# --- Create the plot ---
plt.figure(figsize=(15, 7))

# The lineplot call is correct
sns.lineplot(data=pax_by_year_month, x='year_month', y='total', hue='fg_continent')

# --- CORRECTED PART: Customize the x-axis ticks ---
# 1. Get the unique x-axis labels that seaborn is plotting
x_labels = pax_by_year_month['year_month'].unique()

# 2. Find the position (index) of each 'January' label in that unique list
tick_positions = []
tick_labels = []
for index, label in enumerate(x_labels):
    # Check if the month is January ('-01')
    if '-01' in label:
        tick_positions.append(index)
        tick_labels.append(label[:4]) # Just show the year 'YYYY'

# 3. Apply the corrected ticks
plt.xticks(ticks=tick_positions, labels=tick_labels, rotation=45, ha='right')

# --- Add labels and title ---
plt.title('Total International Passengers per Month by Continent')
plt.xlabel('Date')
plt.ylabel('Total Passengers')
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()



#########################################################
#########################################################

# --- Create the plot ---
plt.figure(figsize=(15, 7))

# The lineplot call is correct
sns.relplot(data=pax_by_year_month, x='year_month', y='total', row='fg_continent', kind='line', height=3, aspect=4, facet_kws={'sharey': False, 'sharex': True})

# --- CORRECTED PART: Customize the x-axis ticks ---
# 1. Get the unique x-axis labels that seaborn is plotting
x_labels = pax_by_year_month['year_month'].unique()

# 2. Find the position (index) of each 'January' label in that unique list
tick_positions = []
tick_labels = []
for index, label in enumerate(x_labels):
    # Check if the month is January ('-01')
    if '-01' in label:
        tick_positions.append(index)
        tick_labels.append(label[:4]) # Just show the year 'YYYY'

# 3. Apply the corrected ticks
plt.xticks(ticks=tick_positions, labels=tick_labels, rotation=45, ha='right')

# --- Add labels and title ---
plt.title('Total International Passengers per Month by Continent')
plt.xlabel('Date')
plt.ylabel('Total Passengers')
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()
