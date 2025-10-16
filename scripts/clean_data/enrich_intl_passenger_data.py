import pandas as pd
import wbgapi as wb
import pycountry
import yaml
from pathlib import Path
import traceback
from typing import Dict, List

# --- CONSTANTS ---
RAW_DATA_PATH = Path("./data/T100_International/t100_international_data_by_year.parquet")
ENRICHED_OUTPUT_PATH = Path("./data/T100_International/final_enriched_data.parquet")
AIRPORTS_URL = "https://davidmegginson.github.io/ourairports-data/airports.csv"
COUNTRIES_URL = "https://davidmegginson.github.io/ourairports-data/countries.csv"
AIRPORT_NAME_FIX = Path('./inputs/airport_name_fix.yaml')
WB_INDICATORS = {
    'SP.POP.TOTL': 'population',
    'NY.GDP.MKTP.CD': 'gdp',
    'NY.GDP.PCAP.CD': 'gdp_per_capita',
    'TG.VAL.TOTL.GD.ZS': 'trade_pct_gdp',
    'ST.INT.ARVL': 'tourism_arrivals',
    'EP.PMP.JFPS.CD': 'jet_fuel_price'
}

def load_and_clean_flight_data(file_path: Path, airport_corrections: Dict) -> pd.DataFrame:
    """
    Loads raw flight data from a Parquet file and performs initial cleaning and corrections.

    Args:
        file_path: The path to the input Parquet file.
        airport_corrections: A dictionary containing airport codes to be corrected.

    Returns:
        A cleaned and processed pandas DataFrame.
    """
    print(f"--- Loading and cleaning data from {file_path} ---")
    
    df_flights = pd.read_parquet(file_path)

    # Define columns for numeric conversion
    numeric_cols = [
        'year', 'month', 'usg_apt_id', 'usg_wac', 'fg_apt_id', 
        'fg_wac', 'airlineid', 'scheduled', 'charter', 'total'
    ]
    
    # Apply standard conversions
    df_flights[numeric_cols] = df_flights[numeric_cols].apply(pd.to_numeric, errors='coerce')
    df_flights['carriergroup'] = df_flights['carriergroup'].map({'0': 'Foreign', '1': 'Domestic'})
    df_flights['data_dte'] = pd.to_datetime(df_flights[['year', 'month']].assign(DAY=1))

    # --- Apply and report airport code corrections ---
    print("\n--- Applying airport code corrections ---")
    
    # Define a list of the airport columns to check and correct
    apt_columns_to_correct = ['usg_apt', 'fg_apt']
    
    for old_code, details in airport_corrections.items():
        new_code = details['new_code']
        reason = details['reason']
        
        # Loop through both the US and Foreign airport columns
        for col in apt_columns_to_correct:
            # Find how many rows will be affected in the current column
            affected_rows = df_flights[col] == old_code
            num_affected = affected_rows.sum()
            
            if num_affected > 0:
                print(f"Correcting {num_affected} rows in '{col}': '{old_code}' -> '{new_code}' (Reason: {reason})")
                # Apply the replacement to the current column
                df_flights.loc[affected_rows, col] = new_code

    print("\nData cleaning and corrections complete.")
    return df_flights


def create_airport_lookup() -> pd.DataFrame:
    """Loads airport and country CSVs and merges them into a single lookup table."""
    print("--- Preparing airport lookup table ---")
    df_airports_raw = pd.read_csv(AIRPORTS_URL, keep_default_na=False, na_values=[''])
    df_countries = pd.read_csv(COUNTRIES_URL, keep_default_na=False, na_values=[''])

    df_airports_raw.rename(columns={'type': 'airport_type', 'name': 'airport_name'}, inplace=True)
    df_countries.rename(columns={'name': 'country_name'}, inplace=True)

    df_airports = pd.merge(
        df_airports_raw,
        df_countries[['code', 'country_name']],
        left_on='iso_country',
        right_on='code',
        how='left'
    ).drop(columns='code')

    df_airports.loc[df_airports['airport_type'] == 'seaplane_base', 'elevation_ft'] = 0
    return df_airports

def merge_airport_data(df: pd.DataFrame, df_airports: pd.DataFrame) -> pd.DataFrame:
    """Merges airport details into the main flight DataFrame for both USG and FG airports."""
    print("--- Merging airport data into flight records ---")
    cols_to_keep = [
        'iata_code', 'airport_name', 'airport_type', 'country_name', 'latitude_deg', 
        'longitude_deg', 'elevation_ft', 'continent', 'iso_country', 'iso_region', 
        'municipality'
    ]

    def create_rename_dict(prefix: str, cols: List[str]) -> Dict[str, str]:
        return {col: f"{prefix}_{col}" for col in cols if col != 'iata_code'}

    # Merge for USG airports
    usg_dict = create_rename_dict('usg', cols_to_keep)
    df_merged = pd.merge(df, df_airports[cols_to_keep], left_on='usg_apt', right_on='iata_code', how='left')
    df_merged.rename(columns=usg_dict, inplace=True)
    df_merged.drop(columns='iata_code', inplace=True)

    # Merge for FG airports
    fg_dict = create_rename_dict('fg', cols_to_keep)
    df_merged = pd.merge(df_merged, df_airports[cols_to_keep], left_on='fg_apt', right_on='iata_code', how='left')
    df_merged.rename(columns=fg_dict, inplace=True)
    df_merged.drop(columns='iata_code', inplace=True)
    
    return df_merged

def fetch_and_process_world_bank_data(df: pd.DataFrame, indicators: Dict[str, str]) -> pd.DataFrame:
    """Fetches, reshapes, and interpolates World Bank data for all countries and years in the flight dataset."""
    print("--- Fetching and processing World Bank data ---")

    def convert_iso2_to_iso3(code: str) -> str:
        if not isinstance(code, str): return None
        try: return pycountry.countries.get(alpha_2=code).alpha_3
        except: return None

    df['usg_iso_country_alpha3'] = df['usg_iso_country'].apply(convert_iso2_to_iso3)
    df['fg_iso_country_alpha3'] = df['fg_iso_country'].apply(convert_iso2_to_iso3)

    all_codes = pd.concat([df['usg_iso_country_alpha3'], df['fg_iso_country_alpha3']]).dropna().unique().tolist()
    start_year, end_year = int(df['year'].min()), int(df['year'].max())
    year_range = range(start_year, end_year + 1)

    print(f"Fetching data for {len(all_codes)} countries from {start_year}-{end_year}")
    df_wide = wb.data.DataFrame(list(indicators.keys()), all_codes, time=year_range, labels=True)

    # Reshape and clean data
    df_long = pd.melt(df_wide.reset_index(), id_vars=['economy', 'series', 'Country', 'Series'], var_name='year', value_name='value')
    df_long['value'] = pd.to_numeric(df_long['value'], errors='coerce')
    df_long['year'] = pd.to_numeric(df_long['year'].str.replace('YR', ''))
    df_long.sort_values(['economy', 'year'], inplace=True)

    # Interpolate and fill missing values
    print("Filling missing economic data by interpolation...")
    df_long['value'] = df_long.groupby(['economy', 'series'])['value'].transform(
        lambda x: x.interpolate(method='linear', limit_direction='both').bfill().ffill()
    )

    # Pivot to final format
    df_wb = df_long.pivot_table(index=['economy', 'year'], columns='series', values='value').reset_index()
    df_wb.rename(columns=indicators, inplace=True)
    df_wb.columns.name = None
    return df_wb

def merge_world_bank_data(df_merged: pd.DataFrame, df_wb: pd.DataFrame) -> pd.DataFrame:
    """Performs year-specific merges for USG and FG economic data."""
    print("--- Performing final year-specific merges ---")
    
    # Ensure year columns have the same type
    df_merged['year'] = df_merged['year'].astype(int)
    df_wb['year'] = df_wb['year'].astype(int)

    # Merge for foreign gateway
    df_final = pd.merge(df_merged, df_wb, left_on=['fg_iso_country_alpha3', 'year'], right_on=['economy', 'year'], how='left')
    df_final.rename(columns=WB_INDICATORS, inplace=True, errors='ignore') # Avoid renaming conflicts
    df_final.rename(columns={v: f"fg_{v}" for v in WB_INDICATORS.values()}, inplace=True)
    df_final.drop(columns=['economy'], inplace=True)

    # Merge for US gateway
    df_final = pd.merge(df_final, df_wb, left_on=['usg_iso_country_alpha3', 'year'], right_on=['economy', 'year'], how='left')
    df_final.rename(columns=WB_INDICATORS, inplace=True, errors='ignore')
    df_final.rename(columns={v: f"usg_{v}" for v in WB_INDICATORS.values()}, inplace=True)
    df_final.drop(columns=['economy'], inplace=True)
    
    return df_final

def main():

    with open(AIRPORT_NAME_FIX, 'r') as f:
        airport_corrections_dict = yaml.safe_load(f)

    df_flights = load_and_clean_flight_data(RAW_DATA_PATH, airport_corrections_dict)

    # reate the airport lookup table
    df_airports = create_airport_lookup()

    # Merge airport data into flight data
    df_merged = merge_airport_data(df_flights, df_airports)

    # Fetch and process World Bank data
    df_wb = fetch_and_process_world_bank_data(df_merged, WB_INDICATORS)

    # Perform the final merges
    df_final = merge_world_bank_data(df_merged, df_wb)

    # Display and save final result
    print("\n--- Final dataset with year-appropriate economic data ---")
    display_cols = ['year', 'usg_apt', 'fg_apt', 'usg_gdp', 'fg_gdp', 'usg_population', 'fg_population']
    print(df_final[display_cols].head())

    ENRICHED_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_final.to_parquet(ENRICHED_OUTPUT_PATH)
    print(f"\nFinal enriched data saved to {ENRICHED_OUTPUT_PATH}")
    print("\n--- SCRIPT COMPLETED SUCCESSFULLY ---")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("\n--- SCRIPT FAILED ---")
        print(f"An error occurred: {e}")
        traceback.print_exc()