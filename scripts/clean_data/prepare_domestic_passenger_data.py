import pandas as pd
from pathlib import Path
import numpy as np

# --- 1. Define Paths ---
raw_data_dir = Path("./data/T100_domestic/raw")
output_dir = Path("./data/T100_domestic/processed")
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / "t100_domestic_market_all_carrier.parquet"

# --- 2. Find CSV Files ---
csv_files = sorted(list(raw_data_dir.glob("**/T_T100_MARKET_ALL_CARRIER.csv")))

if not csv_files:
    print(f"Error: No CSV files found in {raw_data_dir}")
else:
    print(f"Found {len(csv_files)} CSV files to combine.")

    # --- 3. Define Reading Options ---
    # Specify string types to avoid mixed-type warnings
    expected_dtypes = {
        'UNIQUE_CARRIER': str,
        'UNIQUE_CARRIER_NAME': str,
        'UNIQUE_CARRIER_ENTITY': str,
        'ORIGIN': str,
        'ORIGIN_CITY_NAME': str,
        'ORIGIN_STATE_ABR': str,
        'DEST': str,
        'DEST_CITY_NAME': str,
        'DEST_STATE_ABR': str,
        'AIRCRAFT_TYPE': str,
    }
    # Define values to interpret as NaN - Removed "NA" from this since airlines like North American Airlines use it as a valid code
    missing_values = ["", "#N/A", "N/A", "-1.#IND", "-1.#QNAN", "-NaN", "-nan", "1.#IND", "1.#QNAN", "<NA>", "NULL", "null", "NaN", "n/a", "nan", "none"]

    # --- 4. Read and Combine DataFrames ---
    all_dataframes = []
    for file in csv_files:
        print(f"Reading {file.parent.name}...")
        try:
            df = pd.read_csv(
                file,
                dtype=expected_dtypes,
                na_values=missing_values,
                keep_default_na=False
            )
            df['File_name'] = file.parent.name
            all_dataframes.append(df)
        except Exception as e:
            print(f"    -> Error reading {file}: {e}")

        print('  Year: ', df.YEAR.unique())

# --- 5. Combine and Perform Final Type Conversions ---
    if all_dataframes:
        print("\nCombining all data into a single DataFrame...")
        combined_df = pd.concat(all_dataframes, ignore_index=True)
        print(f"Total records combined: {len(combined_df):,}")

        # --- Convert integer columns to nullable Int64 ---
        # Ensure ALL columns intended as integers are listed here
        integer_cols = [
            'PASSENGERS', 'DISTANCE',
            'YEAR', 'QUARTER', 'MONTH', # Added QUARTER
            'ORIGIN_AIRPORT_ID', 'ORIGIN_WAC','ORIGIN_AIRPORT_SEQ_ID',
            'ORIGIN_CITY_MARKET_ID', 'ORIGIN_STATE_FIPS', # Corrected ORIGIN_STATE_FIPS
            'DEST_AIRPORT_ID', 'DEST_WAC', 'DEST_AIRPORT_SEQ_ID',
            'DEST_CITY_MARKET_ID', 'DEST_STATE_FIPS', # Corrected DEST_STATE_FIPS
            'AIRLINE_ID', # Corrected AIRLINE_ID
            'DISTANCE_GROUP',
            'FREIGHT', 'MAIL', # Corrected FREIGHT and MAIL
            'CARRIER_GROUP', 'CARRIER_GROUP_NEW' # Corrected CARRIER_GROUPs
        ]
        print("Converting integer columns to nullable Int64 type...")
        successful_conversions = []
        failed_conversions = []
        for col in integer_cols:
            if col in combined_df.columns:
                try:
                    # Convert to numeric first (handles errors), then to Int64
                    combined_df[col] = pd.to_numeric(combined_df[col], errors='coerce')
                    if col == 'FREIGHT':
                        combined_df[col] = combined_df[col].round(0)
                    combined_df[col] = combined_df[col].astype('Int64')
                    successful_conversions.append(col)
                except Exception as e:
                    print(f"    -> Failed to convert '{col}'. Error: {e}")
                    failed_conversions.append(col)
            else:
                print(f"    -> Column '{col}' not found in DataFrame.")
                failed_conversions.append(col)

        print(f"Successfully converted: {successful_conversions}")
        if failed_conversions:
             print(f"Failed or skipped: {failed_conversions}")


        # --- 6. Save to Parquet ---
        print(f"Saving combined data to: {output_path}")
        combined_df.to_parquet(output_path)
        print("\n--- Process complete. ---")
    else:
        print("\nNo data was combined.")