import pandas as pd
import os

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

def inspect_parquet(filepath):
    print(f"--- Inspecting {filepath} ---")
    try:
        df = pd.read_parquet(filepath)
        print("Columns:", df.columns.tolist())
        print("Shape:", df.shape)
        print("First 5 rows:")
        print(df.head())
        print("\n")
    except Exception as e:
        print(f"Error reading {filepath}: {e}")

base_dir = '/home/natti/skynet/data'
files_to_inspect = [
    os.path.join(base_dir, 'lookups', 'airports_enriched.parquet'),
    os.path.join(base_dir, 'T100_domestic', 'processed', 'final_enriched_t100_data.parquet')
]

for f in files_to_inspect:
    inspect_parquet(f)
