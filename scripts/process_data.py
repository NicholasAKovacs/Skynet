import pandas as pd
import json
import os

def process_data():
    base_dir = '/home/natti/skynet/data'
    output_dir = '/home/natti/skynet/src/data'
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    print("Loading data...")
    # Load Routes Data
    routes_path = os.path.join(base_dir, 'T100_domestic', 'processed', 'final_enriched_t100_data.parquet')
    df_routes = pd.read_parquet(routes_path)
    
    # Load Airports Data
    airports_path = os.path.join(base_dir, 'lookups', 'airports_enriched.parquet')
    df_airports = pd.read_parquet(airports_path)
    
    print("Data loaded. Processing...")

    # Aggregate passengers by route (Origin-Destination)
    # We group by Origin and Dest, and sum passengers
    route_stats = df_routes.groupby(['ORIGIN', 'DEST'])['PASSENGERS'].sum().reset_index()
    
    # Sort by passengers descending
    route_stats = route_stats.sort_values('PASSENGERS', ascending=False)
    
    # Take top 2000 routes
    top_routes = route_stats.head(2000)
    
    # Merge with airport coordinates
    # We need coordinates for both Origin and Dest
    
    # Prepare airport lookup
    # Assuming df_airports has 'IATA' code and lat/lon
    # Let's check airport columns first if we were interactive, but I'll assume standard names or fix if it fails.
    # Based on previous inspection, airport file had 'iata_code', 'latitude_deg', 'longitude_deg' etc? 
    # Wait, I saw the airport file content earlier in the 'inspect_data.py' output but it was truncated.
    # I saw: column 1 is likely index, then 'id', 'ident', 'type', 'name', 'latitude_deg', 'longitude_deg', 'elevation_ft', 'continent', 'iso_country', 'iso_region', 'municipality', 'scheduled_service', 'gps_code', 'iata_code', 'local_code', 'home_link', 'wikipedia_link', 'keywords', 'country_name'.
    # So 'iata_code' is the key.
    
    airport_lookup = df_airports.set_index('iata_code')[['latitude_deg', 'longitude_deg', 'name', 'municipality', 'iso_region']].to_dict('index')
    
    processed_routes = []
    
    for _, row in top_routes.iterrows():
        origin = row['ORIGIN']
        dest = row['DEST']
        passengers = row['PASSENGERS']
        
        if origin in airport_lookup and dest in airport_lookup:
            origin_data = airport_lookup[origin]
            dest_data = airport_lookup[dest]
            
            processed_routes.append({
                'origin': origin,
                'dest': dest,
                'passengers': int(passengers),
                'origin_lat': origin_data['latitude_deg'],
                'origin_lon': origin_data['longitude_deg'],
                'origin_name': origin_data['name'],
                'origin_city': origin_data['municipality'],
                'dest_lat': dest_data['latitude_deg'],
                'dest_lon': dest_data['longitude_deg'],
                'dest_name': dest_data['name'],
                'dest_city': dest_data['municipality']
            })
            
    print(f"Processed {len(processed_routes)} valid routes.")
    
    # Save to JSON
    with open(os.path.join(output_dir, 'routes.json'), 'w') as f:
        json.dump(processed_routes, f)
        
    # Save Airports Lookup as well for the UI to show details if needed
    # We only need airports that are in our routes to save space
    used_airports = set([r['origin'] for r in processed_routes] + [r['dest'] for r in processed_routes])
    filtered_airports = {k: v for k, v in airport_lookup.items() if k in used_airports}
    
    with open(os.path.join(output_dir, 'airports.json'), 'w') as f:
        json.dump(filtered_airports, f)
        
    print("Done.")

if __name__ == "__main__":
    process_data()
