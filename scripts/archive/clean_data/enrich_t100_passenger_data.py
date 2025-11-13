import pandas as pd
import wbgapi as wb
import pycountry
import yaml
from pathlib import Path
import traceback
from typing import Dict, List, Optional
from myeia.api import API
import os
from dotenv import load_dotenv

# --- CONSTANTS ---
# Use the comprehensive "domestic" file as the single source of truth
RAW_DATA_PATH = Path("./data/T100_domestic/processed/t100_domestic_market_all_carrier.parquet")
ENRICHED_OUTPUT_PATH = Path("./data/T100_domestic/processed/final_enriched_t100_data.parquet")

# Lookup and config files
AIRPORTS_URL = "https://davidmegginson.github.io/ourairports-data/airports.csv"
COUNTRIES_URL = "https://davidmegginson.github.io/ourairports-data/countries.csv"
AIRPORT_NAME_FIX = Path('./inputs/airport_name_fix.yaml')

# World Bank Indicators
WB_INDICATORS = {
    'SP.POP.TOTL': 'population',
    'NY.GDP.MKTP.CD': 'gdp',
    'NY.GDP.PCAP.CD': 'gdp_per_capita',
    'TG.VAL.TOTL.GD.ZS': 'trade_pct_gdp',
    'ST.INT.ARVL': 'tourism_arrivals',
    'FP.CPI.TOTL.ZG': 'inflation_cp'
}

# --- HELPER FUNCTIONS ---

def load_and_clean_data(file_path: Path, airport_corrections: Dict) -> pd.DataFrame:
    """Loads and performs initial cleaning on the T-100 dataset."""
    print(f"--- Loading and cleaning data from {file_path} ---")
    df = pd.read_parquet(file_path)
    df['data_dte'] = pd.to_datetime(df[['YEAR', 'MONTH']].assign(DAY=1))
    
    print("\n--- Applying airport code corrections ---")
    for old_code, details in airport_corrections.items():
        for col in ['ORIGIN', 'DEST']:
            affected_rows = df[col] == old_code
            if affected_rows.any():
                df.loc[affected_rows, col] = details['new_code']
    return df

def create_airport_lookup() -> pd.DataFrame:
    """Creates a lookup table with enriched airport and country data."""
    print("--- Preparing airport lookup table ---")
    df_airports_raw = pd.read_csv(AIRPORTS_URL, keep_default_na=False, na_values=[''])
    df_countries = pd.read_csv(COUNTRIES_URL, keep_default_na=False, na_values=[''])
    df_airports_raw.rename(columns={'type': 'airport_type', 'name': 'airport_name'}, inplace=True)
    df_countries.rename(columns={'name': 'country_name'}, inplace=True)
    df_airports = pd.merge(df_airports_raw, df_countries[['code', 'country_name']], left_on='iso_country', right_on='code', how='left').drop(columns='code')
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

def fetch_world_bank_data(df: pd.DataFrame, indicators: Dict[str, str]) -> pd.DataFrame:
    """Fetches and processes World Bank data for all countries in the dataset."""
    print("\n--- Fetching and processing World Bank data for all countries ---")
    
    def convert_iso2_to_iso3(code: str) -> str:
        if not isinstance(code, str): return None
        try: return pycountry.countries.get(alpha_2=code).alpha_3
        except: return None
    
    df['origin_iso_country_alpha3'] = df['origin_iso_country'].apply(convert_iso2_to_iso3)
    df['dest_iso_country_alpha3'] = df['dest_iso_country'].apply(convert_iso2_to_iso3)

    all_codes = pd.concat([df['origin_iso_country_alpha3'], df['dest_iso_country_alpha3']]).dropna().unique().tolist()
    start_year, end_year = int(df['YEAR'].min()), int(df['YEAR'].max())
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
    return df_wb

def fetch_jet_fuel_prices(api_key: str) -> Optional[pd.DataFrame]:
    """Fetches annual NY Harbor jet fuel spot prices."""
    print("--- Fetching jet fuel price data ---")
    try:
        api = API(api_key)
        series_data = api.get_series_via_route(route="petroleum/pri/spt", series="EER_EPJK_PF4_Y35NY_DPG", frequency="annual")
        df_fuel = pd.DataFrame(series_data)
        df_fuel.reset_index(inplace=True)
        df_fuel.columns = ['year', 'jet_fuel_price']
        df_fuel['year'] = df_fuel['year'].dt.year
        return df_fuel
    except Exception as e:
        print(f"  -> Could not fetch jet fuel data: {e}")
        return None

def main():
    """Main function to orchestrate the full data enrichment pipeline."""
    load_dotenv()
    EIA_API_KEY = os.getenv("EIA_API_KEY")

    with open(AIRPORT_NAME_FIX, 'r') as f:
        airport_corrections = yaml.safe_load(f)

    # --- Full Pipeline ---
    df_flights = load_and_clean_data(RAW_DATA_PATH, airport_corrections)
    df_airports = create_airport_lookup()
    df_merged = merge_airport_data(df_flights, df_airports)
    df_wb = fetch_world_bank_data(df_merged, WB_INDICATORS)
    df_jet_fuel = fetch_jet_fuel_prices(EIA_API_KEY)
    
    # --- Final Merges ---
    print("--- Performing final year-specific merges ---")
    df_merged['YEAR'] = df_merged['YEAR'].astype(int)
    df_wb['year'] = df_wb['year'].astype(int)

    # Merge data for ORIGIN country
    df_final = pd.merge(df_merged, df_wb, left_on=['origin_iso_country_alpha3', 'YEAR'], right_on=['economy', 'year'], how='left')
    df_final.rename(columns={v: f"origin_{v}" for v in WB_INDICATORS.values()}, inplace=True)
    df_final.drop(columns=['economy', 'year'], inplace=True, errors='ignore')

    # Merge data for DESTINATION country
    df_final = pd.merge(df_final, df_wb, left_on=['dest_iso_country_alpha3', 'YEAR'], right_on=['economy', 'year'], how='left')
    df_final.rename(columns={v: f"dest_{v}" for v in WB_INDICATORS.values()}, inplace=True)
    df_final.drop(columns=['economy', 'year'], inplace=True, errors='ignore')
    
    # Merge global jet fuel price
    if df_jet_fuel is not None:
        df_jet_fuel['year'] = df_jet_fuel['year'].astype(int)
        df_final = pd.merge(df_final, df_jet_fuel, left_on='YEAR', right_on='year', how='left')
        df_final.drop(columns=['year'], inplace=True, errors='ignore')

    # Save the final result
    print("\n--- Final enriched dataset ---")
    print(df_final.head())
    ENRICHED_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_final.to_parquet(ENRICHED_OUTPUT_PATH)
    print(f"\nFinal enriched data saved to {ENRICHED_OUTPUT_PATH}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("\n--- SCRIPT FAILED ---")
        traceback.print_exc()