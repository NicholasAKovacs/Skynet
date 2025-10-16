# Could not get this to work, will come back later if data is needed

import json
import pandas as pd
import trino
from trino import dbapi
from trino.auth import BasicAuthentication

# --- 1. LOAD CREDENTIALS FROM JSON FILE ---
credentials_path = './inputs/credentials.json'

try:
    with open(credentials_path) as f:
        credentials = json.load(f)
    OPENSKY_USER = credentials['clientId']
    OPENSKY_PASS = credentials['clientSecret']
    print("Credentials loaded successfully.")
except FileNotFoundError:
    print(f"Error: Credentials file not found at '{credentials_path}'")
    exit()

# --- 2. CONNECT TO THE TRINO DATABASE ---
print("Connecting to the OpenSky Trino database...")
conn = dbapi.connect(
    host='data.opensky-network.org',
    port=443,
    user=OPENSKY_USER,
    http_scheme='https',
    auth=BasicAuthentication(OPENSKY_USER, OPENSKY_PASS),
    request_timeout=120
)

cursor = conn.cursor()

# --- 3. EXECUTE THE SAME SQL QUERY ---
# Your SQL queries work exactly the same way.
sql_query = """
SELECT callsign, origin, destination
FROM flight
WHERE origin = 'KATL' AND day = '2025-09-15'
LIMIT 20
"""

print("\nExecuting SQL query...")
cursor.execute(sql_query)
df = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])

print("\n--- Query Results ---")
print(df)

# --- 4. CLOSE CONNECTION ---
cursor.close()
conn.close()