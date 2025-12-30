import tornado.ioloop
import tornado.web
import pandas as pd
import json
import os

PORT = 8888
BASE_DIR = '/home/natti/skynet/data'

class RoutesHandler(tornado.web.RequestHandler):
    def initialize(self, routes_data):
        self.routes_data = routes_data

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def options(self):
        self.set_status(204)
        self.finish()

    def get(self):
        self.write(json.dumps(self.routes_data))

def load_data():
    print("Loading data...")
    routes_path = os.path.join(BASE_DIR, 'T100_domestic', 'processed', 'final_enriched_t100_data.parquet')
    airports_path = os.path.join(BASE_DIR, 'lookups', 'airports_enriched.parquet')
    
    try:
        df_routes = pd.read_parquet(routes_path)
        df_airports = pd.read_parquet(airports_path)
    except Exception as e:
        print(f"Error loading parquet files: {e}")
        return []

    print("Processing routes...")
    # Aggregate passengers by route (Origin-Destination)
    route_stats = df_routes.groupby(['ORIGIN', 'DEST'])['PASSENGERS'].sum().reset_index()
    
    # Sort by passengers descending and take top 2000
    route_stats = route_stats.sort_values('PASSENGERS', ascending=False).head(2000)
    
    # Create airport lookup
    # 'iata_code' is the key based on previous inspection
    airport_lookup = df_airports.drop_duplicates(subset=['iata_code']).set_index('iata_code')[['latitude_deg', 'longitude_deg', 'airport_name', 'municipality', 'iso_region']].to_dict('index')
    
    processed_routes = []
    for _, row in route_stats.iterrows():
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
                'origin_name': origin_data['airport_name'],
                'origin_city': origin_data['municipality'],
                'dest_lat': dest_data['latitude_deg'],
                'dest_lon': dest_data['longitude_deg'],
                'dest_name': dest_data['airport_name'],
                'dest_city': dest_data['municipality']
            })
            
    print(f"Loaded {len(processed_routes)} routes.")
    return processed_routes

def make_app():
    data = load_data()
    return tornado.web.Application([
        (r"/api/routes", RoutesHandler, dict(routes_data=data)),
    ])

if __name__ == "__main__":
    app = make_app()
    print(f"Server starting on port {PORT}")
    app.listen(PORT)
    tornado.ioloop.IOLoop.current().start()
