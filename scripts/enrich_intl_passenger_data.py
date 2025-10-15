import pandas as pd
import wbgapi as wb
import pycountry
from pathlib import Path
import traceback # <-- Added this import

try: # <-- Start of the error handling block

    # --- STEP 1: LOAD ALL RAW DATA ---
    print("--- Loading Raw Data ---")
    parquet_path = "./data/T100_International/t100_international_data_by_year.parquet"
    df = pd.read_parquet(parquet_path)

    airports_url = "https://davidmegginson.github.io/ourairports-data/airports.csv"
    countries_url = "https://davidmegginson.github.io/ourairports-data/countries.csv"

    df_airports_raw = pd.read_csv(airports_url, keep_default_na=False, na_values=[''])
    df_countries = pd.read_csv(countries_url, keep_default_na=False, na_values=[''])

    # --- STEP 2: PREPARE AIRPORT LOOKUP TABLE ---
    df_airports_raw.rename(columns={'type': 'airport_type', 'name': 'airport_name'}, inplace=True)
    df_countries.rename(columns={'name': 'country_name'}, inplace=True)

    df_airports = pd.merge(
        df_airports_raw,
        df_countries[['code', 'country_name']],
        left_on='iso_country',
        right_on='code',
        how='left'
    ).drop(columns='code')

    # --- STEP 3: MERGE AIRPORT DATA INTO FLIGHT DATA ---
    print("--- Merging Airport Data ---")
    airport_cols_to_keep = [
        'iata_code', 'airport_name', 'airport_type', 'country_name', 'latitude_deg', 'longitude_deg',
        'elevation_ft', 'continent', 'iso_country', 'iso_region', 'municipality'
    ]

    def create_rename_dict(prefix, cols):
        return {col: f"{prefix}_{col}" for col in cols if col != 'iata_code'}

    usg_rename_dict = create_rename_dict('usg', airport_cols_to_keep)
    df_merged = pd.merge(df, df_airports[airport_cols_to_keep], left_on='usg_apt', right_on='iata_code', how='left')
    df_merged.rename(columns=usg_rename_dict, inplace=True)
    df_merged.drop(columns='iata_code', inplace=True)

    fg_rename_dict = create_rename_dict('fg', airport_cols_to_keep)
    df_merged = pd.merge(df_merged, df_airports[airport_cols_to_keep], left_on='fg_apt', right_on='iata_code', how='left')
    df_merged.rename(columns=fg_rename_dict, inplace=True)
    df_merged.drop(columns='iata_code', inplace=True)

    df_merged['year'] = pd.to_numeric(df_merged['year'], errors='coerce')

    # --- STEP 4: FETCH AND PROCESS WORLD BANK DATA ---
    def convert_iso2_to_iso3(iso2_code):
        if not isinstance(iso2_code, str): return None
        try: return pycountry.countries.get(alpha_2=iso2_code).alpha_3
        except: return None

    df_merged['usg_iso_country_alpha3'] = df_merged['usg_iso_country'].apply(convert_iso2_to_iso3)
    df_merged['fg_iso_country_alpha3'] = df_merged['fg_iso_country'].apply(convert_iso2_to_iso3)

    all_country_codes = pd.concat([df_merged['usg_iso_country_alpha3'], df_merged['fg_iso_country_alpha3']]).dropna().unique().tolist()
    start_year, end_year = int(df_merged['year'].min()), int(df_merged['year'].max())
    year_range = range(start_year, end_year + 1)

    indicators = {'SP.POP.TOTL': 'population', 'NY.GDP.MKTP.CD': 'gdp'}

    print(f"\n--- Fetching World Bank data from {start_year}-{end_year} ---")
    df_wb_wide = wb.data.DataFrame(list(indicators.keys()), all_country_codes, time=year_range, labels=True)

    df_wb_long = pd.melt(df_wb_wide.reset_index(), id_vars=['economy', 'series', 'Country', 'Series'], var_name='year', value_name='value')
    df_wb_long['value'] = pd.to_numeric(df_wb_long['value'], errors='coerce')
    df_wb_long['year'] = pd.to_numeric(df_wb_long['year'].str.replace('YR', ''))
    df_wb_long.sort_values(['economy', 'year'], inplace=True)
    df_wb_long['value'] = df_wb_long.groupby(['economy', 'series'])['value'].transform(lambda x: x.interpolate(method='linear', limit_direction='both').bfill().ffill())
    df_wb = df_wb_long.pivot_table(index=['economy', 'year'], columns='series', values='value').reset_index()
    df_wb.rename(columns=indicators, inplace=True)
    df_wb.columns.name = None

    # --- STEP 5: FINAL YEAR-SPECIFIC MERGES ---
    print("--- Performing final year-specific merges ---")
    
    # Ensure year columns are the same integer type before merging
    df_merged['year'] = df_merged['year'].astype(int)
    df_wb['year'] = df_wb['year'].astype(int)
    
    df_final = pd.merge(df_merged, df_wb, left_on=['fg_iso_country_alpha3', 'year'], right_on=['economy', 'year'], how='left')
    df_final.rename(columns={'population': 'fg_population', 'gdp': 'fg_gdp'}, inplace=True)
    df_final.drop(columns=['economy'], inplace=True)

    df_final = pd.merge(df_final, df_wb, left_on=['usg_iso_country_alpha3', 'year'], right_on=['economy', 'year'], how='left')
    df_final.rename(columns={'population': 'usg_population', 'gdp': 'usg_gdp'}, inplace=True)
    df_final.drop(columns=['economy'], inplace=True)

    # --- STEP 6: DISPLAY AND SAVE FINAL RESULT ---
    print("\n--- Final dataset with year-appropriate economic data ---")
    display_cols = ['year', 'usg_apt', 'fg_apt', 'usg_gdp', 'fg_gdp', 'usg_population', 'fg_population']
    print(df_final[display_cols].head())

    output_path = Path("./data/T100_International/final_enriched_data.parquet")
    df_final.to_parquet(output_path)
    print(f"\nFinal enriched data saved to {output_path}")
    print("\n--- SCRIPT COMPLETED SUCCESSFULLY ---")

except Exception as e: # <-- This will catch any error
    print("\n--- SCRIPT FAILED ---")
    print(f"An error occurred: {e}")
    traceback.print_exc() # This prints the full, detailed error traceback