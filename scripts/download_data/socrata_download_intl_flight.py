import pandas as pd
from sodapy import Socrata
from pathlib import Path
import time
from typing import Optional, List

# --- CONSTANTS ---
SOCRATA_DOMAIN = "datahub.transportation.gov"
SOCRATA_DATASET_ID = "xgub-n9bw"
OUTPUT_DIR = Path("data/T100_International")
PARQUET_PATH = OUTPUT_DIR / "t100_international_data_by_year.parquet"
YEARS_TO_DOWNLOAD = range(1990, 2025)


def fetch_year_data(client: Socrata, year: int) -> Optional[pd.DataFrame]:
    """
    Fetches all T-100 International Market data for a single year.

    Args:
        client: An authenticated Socrata client instance.
        year: The year to fetch data for.

    Returns:
        A pandas DataFrame containing the data for that year, or None if an error occurs.
    """
    print(f"Fetching data for {year}...")
    try:
        query = f"year = '{year}'"
        results = client.get(
            SOCRATA_DATASET_ID,
            where=query,
            limit=50000  # Assuming a year has less than 50,000 records
        )

        if results:
            df = pd.DataFrame.from_records(results)
            print(f"  -> Found {len(df)} records for {year}.")
            return df
        else:
            print(f"  -> No records found for {year}.")
            return None

    except Exception as e:
        print(f"  -> An error occurred for {year}: {e}")
        return None


def download_all_data(years: range) -> Optional[pd.DataFrame]:
    """
    Downloads and combines data for a given range of years.

    Args:
        years: A range of years to download.

    Returns:
        A single pandas DataFrame containing all downloaded data, or None if no data was found.
    """
    client = Socrata(SOCRATA_DOMAIN, None)
    all_yearly_data: List[pd.DataFrame] = []

    print("Starting download by year...")
    for year in years:
        year_df = fetch_year_data(client, year)
        if year_df is not None:
            all_yearly_data.append(year_df)
        time.sleep(1)  # Be polite to the API server

    client.close()

    if all_yearly_data:
        print("\nDownload complete. Combining all data...")
        combined_df = pd.concat(all_yearly_data, ignore_index=True)
        return combined_df
    else:
        print("\nNo data was downloaded.")
        return None


def main():

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    combined_df = download_all_data(YEARS_TO_DOWNLOAD)

    if combined_df is not None:
        print(f"Total records downloaded: {len(combined_df)}")
        print(f"Saving to Parquet file: {PARQUET_PATH}")
        combined_df.to_parquet(PARQUET_PATH)
        print("\nProcess complete.")


if __name__ == "__main__":
    main()