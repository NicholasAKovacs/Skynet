import pandas as pd
from sodapy import Socrata
from pathlib import Path
import time

# --- 1. SETUP ---
client = Socrata("datahub.transportation.gov", None)
socrata_dataset_identifier = "xgub-n9bw"

output_dir = Path("data/T100_International")
output_dir.mkdir(parents=True, exist_ok=True)
parquet_path = output_dir / "t100_international_data_by_year.parquet"

# --- 2. DEFINE YEARS TO DOWNLOAD ---
# Let's download a substantial chunk of recent data.
years_to_download = range(1990, 2025) # Downloads 1990 through 2024

all_yearly_data = []

print("Starting download by year...")

# --- 3. LOOP THROUGH YEARS AND DOWNLOAD DATA ---
for year in years_to_download:
    print(f"Fetching data for {year}...")
    try:
        # Construct a SoQL 'where' clause for the specific year
        query = f"year = '{year}'"
        
        # Use a high limit to get all data for the year
        results = client.get(
            socrata_dataset_identifier, 
            where=query, 
            limit=50000
        )
        
        if results:
            year_df = pd.DataFrame.from_records(results)
            all_yearly_data.append(year_df)
            print(f"  -> Found {len(year_df)} records for {year}.")
        else:
            print(f"  -> No records found for {year}.")
            
        time.sleep(1) # Be polite to the API server

    except Exception as e:
        print(f"  -> An error occurred for {year}: {e}")

client.close()

# --- 4. COMBINE AND SAVE TO PARQUET ---
if all_yearly_data:
    print("\nDownload complete. Combining all data...")
    combined_df = pd.concat(all_yearly_data, ignore_index=True)
    
    print(f"Total records downloaded: {len(combined_df)}")
    print(f"Saving to Parquet file: {parquet_path}")
    
    combined_df.to_parquet(parquet_path)
    
    print("\nProcess complete.")
else:
    print("\nNo data was downloaded.")