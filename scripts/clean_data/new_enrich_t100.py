import pandas as pd
import numpy as np
import wbgapi as wb
import pycountry
import yaml
from pathlib import Path
import traceback
from typing import Dict, List, Optional
from myeia.api import API
import os
from dotenv import load_dotenv
import argparse # Import argparse for command-line arguments

# --- CONSTANTS ---
# Use the comprehensive unified file as the single source of truth
RAW_DATA_PATH = Path("./data/T100_domestic/processed/t100_domestic_market_all_carrier.parquet")
ENRICHED_OUTPUT_PATH = Path("./data/T100_domestic/processed/final_enriched_t100_data.parquet")

# Lookup and config files
AIRPORTS_URL = "https://davidmegginson.github.io/ourairports-data/airports.csv"
COUNTRIES_URL = "https://davidmegginson.github.io/ourairports-data/countries.csv"
AIRPORT_NAME_FIX = Path('./inputs/airport_name_fix.yaml')

# --- LOCAL CACHE FILE PATHS ---
LOOKUP_DIR = Path("./data/lookups")
EXTERNAL_DIR = Path("./data/external")
AIRPORT_LOOKUP_CACHE = LOOKUP_DIR / "airports_enriched.parquet"
WORLD_BANK_CACHE = EXTERNAL_DIR / "world_bank_data.parquet"
JET_FUEL_CACHE = EXTERNAL_DIR / "jet_fuel_prices.parquet"

# World Bank Indicators
WB_INDICATORS = {
    'SP.POP.TOTL': 'population',
    'NY.GDP.MKTP.CD': 'gdp',
    'NY.GDP.PCAP.CD': 'gdp_per_capita',
    'TG.VAL.TOTL.GD.ZS': 'trade_pct_gdp',
    'ST.INT.ARVL': 'tourism_arrivals',
    'FP.CPI.TOTL.ZG': 'inflation_cp'
}

project_root = Path(__file__).resolve().parents[2] # Assumes script is in ./scripts/clean_data/
dotenv_path = project_root / '.env'
load_dotenv(dotenv_path=dotenv_path) # Prints warning saying .env not found even if it was found
EIA_API_KEY = os.getenv("EIA_API_KEY")
if EIA_API_KEY:
    print("Despite above warning, successfully loaded EIA API key from .env file.")
else:
    print("Warning: .env file found, but EIA_API_KEY was not inside. Jet fuel data will be skipped.")

# --- HELPER FUNCTIONS ---

def load_and_clean_data(file_path: Path, airport_corrections: Dict) -> pd.DataFrame:
    """Loads raw flight data, optimizes memory, and performs initial cleaning/corrections."""
    print(f"--- Loading and cleaning data from {file_path} ---")
    df = pd.read_parquet(file_path)

    # --- Memory Optimization ---
    print("Optimizing memory usage by converting object columns to category...")
    for col in df.select_dtypes(include=['object']).columns:
        if col not in ['ORIGIN_CITY_NAME', 'DEST_CITY_NAME']: # Exclude city names for now
            if df[col].nunique() / len(df) < 0.5:
                df[col] = df[col].astype('category')
    print("Memory optimization complete.")

    df['date'] = pd.to_datetime(df[['YEAR', 'MONTH']].assign(DAY=1))

    print("--- Applying airport code corrections ---")
    for old_code, details in airport_corrections.items():
        for col in ['ORIGIN', 'DEST']:
            affected_rows = df[col] == old_code
            if affected_rows.any():
                df.loc[affected_rows, col] = details['new_code']
    print("Initial data cleaning and corrections complete.")
    return df

def create_airport_lookup(force_refresh: bool = False) -> pd.DataFrame:
    """Creates/Loads a lookup table with enriched airport and country data."""
    LOOKUP_DIR.mkdir(parents=True, exist_ok=True)
    if not force_refresh and AIRPORT_LOOKUP_CACHE.exists():
        print(f"--- Loading airport lookup table from cache: {AIRPORT_LOOKUP_CACHE} ---")
        return pd.read_parquet(AIRPORT_LOOKUP_CACHE)
    else:
        print("--- Creating airport lookup table from online sources ---")
        df_airports_raw = pd.read_csv(AIRPORTS_URL, keep_default_na=False, na_values=[''])
        df_countries = pd.read_csv(COUNTRIES_URL, keep_default_na=False, na_values=[''])
        df_airports_raw.rename(columns={'type': 'airport_type', 'name': 'airport_name'}, inplace=True)
        df_countries.rename(columns={'name': 'country_name'}, inplace=True)
        df_airports = pd.merge(df_airports_raw, df_countries[['code', 'country_name']], left_on='iso_country', right_on='code', how='left').drop(columns='code')
        print(f"Saving airport lookup table to cache: {AIRPORT_LOOKUP_CACHE}")
        df_airports.to_parquet(AIRPORT_LOOKUP_CACHE)
        return df_airports

def merge_airport_data(df: pd.DataFrame, df_airports: pd.DataFrame) -> pd.DataFrame:
    """Merges airport details for both ORIGIN and DEST."""
    print("--- Merging airport data into flight records ---")
    cols_to_keep = ['iata_code', 'airport_name', 'airport_type', 'country_name', 'continent', 'iso_country']
    for prefix in ['ORIGIN', 'DEST']:
        rename_dict = {col: f"{prefix.lower()}_{col}" for col in cols_to_keep if col != 'iata_code'}
        df = pd.merge(df, df_airports[cols_to_keep], left_on=prefix, right_on='iata_code', how='left')
        df.rename(columns=rename_dict, inplace=True)
        df.drop(columns='iata_code', inplace=True)
    return df

def fetch_world_bank_data(df: pd.DataFrame, indicators: Dict[str, str], force_refresh: bool = False) -> pd.DataFrame:
    """Fetches/Loads and processes World Bank data."""
    EXTERNAL_DIR.mkdir(parents=True, exist_ok=True)
    if not force_refresh and WORLD_BANK_CACHE.exists():
        print(f"--- Loading World Bank data from cache: {WORLD_BANK_CACHE} ---")
        return pd.read_parquet(WORLD_BANK_CACHE)
    else:
        print("\n--- Fetching and processing World Bank data from API ---")
        def convert_iso2_to_iso3(code: str) -> str:
            if not isinstance(code, str): return None
            try: return pycountry.countries.get(alpha_2=code).alpha_3
            except: return None
        
        # Create alpha3 codes needed for fetch call
        df_temp = df.copy() # Avoid modifying original df within function scope
        df_temp['origin_iso_country_alpha3'] = df_temp['origin_iso_country'].apply(convert_iso2_to_iso3)
        df_temp['dest_iso_country_alpha3'] = df_temp['dest_iso_country'].apply(convert_iso2_to_iso3)
        all_codes = pd.concat([df_temp['origin_iso_country_alpha3'], df_temp['dest_iso_country_alpha3']]).dropna().unique().tolist()
        start_year, end_year = int(df_temp['YEAR'].min()), int(df_temp['YEAR'].max())
        year_range = range(start_year, end_year + 1)

        df_wide = wb.data.DataFrame(list(indicators.keys()), all_codes, time=year_range)
        df_long = pd.melt(df_wide.reset_index(), id_vars=['economy', 'series'], var_name='year', value_name='value')
        df_long['value'] = pd.to_numeric(df_long['value'], errors='coerce')
        df_long['year'] = pd.to_numeric(df_long['year'].str.replace('YR', ''))
        df_long.sort_values(['economy', 'year'], inplace=True)
        df_long['value'] = df_long.groupby(['economy', 'series'])['value'].transform(lambda x: x.interpolate(method='linear', limit_direction='both').bfill().ffill())
        df_wb = df_long.pivot_table(index=['economy', 'year'], columns='series', values='value').reset_index()
        df_wb.rename(columns=indicators, inplace=True)
        df_wb.columns.name = None
        
        print(f"Saving World Bank data to cache: {WORLD_BANK_CACHE}")
        df_wb.to_parquet(WORLD_BANK_CACHE)
        return df_wb

def fetch_jet_fuel_prices(api_key: str, force_refresh: bool = False) -> Optional[pd.DataFrame]:
    """Fetches/Loads annual NY Harbor jet fuel spot prices."""
    EXTERNAL_DIR.mkdir(parents=True, exist_ok=True)
    if not force_refresh and JET_FUEL_CACHE.exists():
        print(f"--- Loading jet fuel price data from cache: {JET_FUEL_CACHE} ---")
        return pd.read_parquet(JET_FUEL_CACHE)
    else:
        print("--- Fetching jet fuel price data from EIA API ---")
        if not api_key:
            print("  -> EIA API key not found. Skipping jet fuel fetch.")
            return None
        try:
            api = API(api_key)
            series_data = api.get_series_via_route(route="petroleum/pri/spt", series="EER_EPJK_PF4_RGC_DPG", frequency="monthly")
            df_fuel = pd.DataFrame(series_data)
            df_fuel.reset_index(inplace=True)
            df_fuel['year'] = df_fuel['Date'].dt.year
            df_fuel['month'] = df_fuel['Date'].dt.month
            df_fuel.drop(columns=['Date'], inplace=True)
            print(f"Saving jet fuel data to cache: {JET_FUEL_CACHE}")
            df_fuel.to_parquet(JET_FUEL_CACHE)
            return df_fuel
        except Exception as e:
            print(f"  -> Could not fetch jet fuel data: {e}")
            return None

def merge_external_data(df_merged: pd.DataFrame, df_wb: pd.DataFrame, df_jet_fuel: Optional[pd.DataFrame]) -> pd.DataFrame:
    """Performs year-specific merges for all external data sources."""
    print("--- Performing final year-specific merges ---")
    
    # Ensure year columns have the same type
    df_merged['YEAR'] = df_merged['YEAR'].astype(int)
    df_merged['MONTH'] = df_merged['MONTH'].astype(int)
    df_wb['year'] = df_wb['year'].astype(int)
    
    # Create the alpha3 columns needed for merging
    def convert_iso2_to_iso3(code: str) -> str:
        if not isinstance(code, str): return None
        try: return pycountry.countries.get(alpha_2=code).alpha_3
        except: return None
        
    print("Creating 3-letter ISO codes for merging...")
    df_merged['origin_iso_country_alpha3'] = df_merged['origin_iso_country'].apply(convert_iso2_to_iso3)
    df_merged['dest_iso_country_alpha3'] = df_merged['dest_iso_country'].apply(convert_iso2_to_iso3)

    # Merge World Bank data for ORIGIN country
    df_final = pd.merge(df_merged, df_wb, left_on=['origin_iso_country_alpha3', 'YEAR'], right_on=['economy', 'year'], how='left')
    df_final.rename(columns={v: f"origin_{v}" for v in WB_INDICATORS.values()}, inplace=True)
    df_final.drop(columns=['economy', 'year'], inplace=True, errors='ignore')

    # Merge World Bank data for DESTINATION country
    df_final = pd.merge(df_final, df_wb, left_on=['dest_iso_country_alpha3', 'YEAR'], right_on=['economy', 'year'], how='left')
    df_final.rename(columns={v: f"dest_{v}" for v in WB_INDICATORS.values()}, inplace=True)
    df_final.drop(columns=['economy', 'year'], inplace=True, errors='ignore')
    
    # Merge the jet fuel data if it exists
    if df_jet_fuel is not None:
        print("--- Merging jet fuel price data ---")
        df_jet_fuel['year'] = df_jet_fuel['year'].astype(int)
        df_jet_fuel['month'] = df_jet_fuel['month'].astype(int)
        df_final = pd.merge(df_final, df_jet_fuel, left_on=['YEAR', 'MONTH'], right_on=['year', 'month'], how='left')
        df_final.drop(columns=['year', 'month'], inplace=True, errors='ignore')

    return df_final

def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Final cleaning steps on the enriched dataset.
    
    NULL value explanations
    - FREIGHT = From MESA airlines, probably just 0 (221 rows)
    - AIRLINE_ID, UNIQUE_CARRIER_NAME, UNIQUE_CARRIER_ENTITY, REGION, CARRIER_NAME, CARRIER_GROUP_NEW = seems like smaller carriers (3084 rows)
    - UNIQUE_CARRIER = North American Airlines - this isnt need for now
    - CARRIER = Executive Airlines for some of its flight has this missing, so filling in with "OW" like the rest of the columns
    - ORIGIN_CITY_NAME, DEST_CITY_NAME = ONly 6 rows, removing since inconsequential
    - ORIGIN_STATE_ABR, ORIGIN_STATE_NM = only US and Canada have state info
    - ORIGIN_STATE_FIPS = only US have this
    - ORIGIN_COUNTRY = Berlin, Prague, and Windhoek, Nambia
    - DEST_STATE_ABR, DEST_STATE_NM = only US and Canada have state info
    - DEST_STATE_FIPS = only US have this
    - origin and dest iso_country_alpha3 = Kosovo. 12 and 17 rows. Dropping
    - 30,000+ missing rows for origin and dest airport cols, removing since its a bunch of small, old airports
    - 244,000 missing rows for world bank cols, missing data seems to be for 2025, or small countries. Leaving
    """

    print("--- Performing final dataset cleaning ---")
    df.loc[df.FREIGHT.isna(), 'FREIGHT'] = 0
    df.loc[(df.UNIQUE_CARRIER_NAME == 'Executive Airlines') & (df.CARRIER.isna()), 'CARRIER'] = 'OW'
    #df['ORIGIN_COUNTRY'] = df['ORIGIN_COUNTRY'].cat.add_categories(['NA'])
    df.loc[df.ORIGIN_CITY_NAME == 'Berlin, Berlin', 'ORIGIN_COUNTRY'] = 'DE'
    df.loc[df.ORIGIN_CITY_NAME == 'Prague, Czechoslovakia', 'ORIGIN_COUNTRY'] = 'CZ'
    df.loc[df.ORIGIN_CITY_NAME == 'Windhoek, Namibia', 'ORIGIN_COUNTRY'] = 'NA'
    #df['DEST_COUNTRY'] = df['DEST_COUNTRY'].cat.add_categories(['NA'])
    df.loc[df.DEST_CITY_NAME== 'Berlin, Berlin', 'DEST_COUNTRY'] = 'DE'
    df.loc[df.DEST_CITY_NAME == 'Prague, Czechoslovakia', 'DEST_COUNTRY'] = 'CZ'
    df.loc[df.DEST_CITY_NAME.isin(['Windhoek, Namibia', 'Walvis Bay, Namibia', 'Ondangwa, Namibia']), 'DEST_COUNTRY'] = 'NA'

    original_len = len(df)
    subset_cols = [
        'AIRLINE_ID', 'ORIGIN_CITY_NAME', 'DEST_CITY_NAME',
        'origin_airport_name', 'dest_airport_name',
        'origin_iso_country_alpha3', 'dest_iso_country_alpha3'
    ]
    df.dropna(subset=subset_cols, inplace=True)
    print(f"Dropped {original_len - len(df)} rows with missing data.")

    return df


def dom_intl_feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """Performs feature engineering on the dataset."""
    print("--- Performing feature engineering ---")
    continent_map = {
        'AS': 'Asia',
        'EU': 'Europe',
        'NA': 'North America',
        'SA': 'South America',
        'OC': 'Oceania',
        'AF': 'Africa'
    }

    conditions = [
        (df['ORIGIN_COUNTRY'] == 'US') & (df['DEST_COUNTRY'] == 'US'),
        (df['ORIGIN_COUNTRY'] != 'US') & (df['DEST_COUNTRY'] == 'US'),
        (df['ORIGIN_COUNTRY'] == 'US') & (df['DEST_COUNTRY'] != 'US')
    ]

    choices = [
        'Domestic',
        'Inbound International',
        'Outbound International'
    ]

    choices_continent = [
        'Domestic',
        'Inbound from ' + df['origin_continent'].map(continent_map).fillna(df['origin_continent']),
        'Outbound to ' + df['dest_continent'].map(continent_map).fillna(df['dest_continent'])
    ]

    df['Travel_type'] = np.select(conditions, choices, default='Other')
    df['Travel_type_continent'] = np.select(conditions, choices_continent, default='Other')

    return df


def main(force_refresh_all: bool = False):
    """Main function to orchestrate the data enrichment pipeline."""

    with open(AIRPORT_NAME_FIX, 'r') as f:
        airport_corrections = yaml.safe_load(f)

    # --- Full Pipeline ---
    df_flights = load_and_clean_data(RAW_DATA_PATH, airport_corrections)
    df_airports = create_airport_lookup(force_refresh=force_refresh_all)
    df_merged = merge_airport_data(df_flights, df_airports)
    df_wb = fetch_world_bank_data(df_merged, WB_INDICATORS, force_refresh=force_refresh_all)
    df_jet_fuel = fetch_jet_fuel_prices(EIA_API_KEY, force_refresh=force_refresh_all)
    df_final = merge_external_data(df_merged, df_wb, df_jet_fuel)
    df_final = clean_dataset(df_final)
    df_final = dom_intl_feature_engineering(df_final)

    # Display and save
    print("\n--- Final enriched dataset ---")
    print(df_final.head())
    ENRICHED_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_final.to_parquet(ENRICHED_OUTPUT_PATH)
    print(f"\nFinal enriched data saved to {ENRICHED_OUTPUT_PATH}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enrich T100 flight data.")
    parser.add_argument('-r', '--refresh', action='store_true', help='Force download of external data, ignoring cache.')
    args = parser.parse_args()

    try:
        main(force_refresh_all=args.refresh)
    except Exception as e:
        print("\n--- SCRIPT FAILED ---")
        traceback.print_exc()