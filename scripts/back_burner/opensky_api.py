from opensky_api import OpenSkyApi
import traceback

# Optional: Add your OpenSky username and password if needed
# username = "your_username"
# password = "your_password"
# api = OpenSkyApi(username, password)

api = OpenSkyApi()

print("Attempting to fetch flight states...")

try:
    # Define a bounding box for Europe
    # (min_latitude, max_latitude, min_longitude, max_longitude)
    europe_bbox = (35.0, 70.0, -15.0, 40.0)
    
    # Request states specifically within the bounding box
    states = api.get_states(bbox=europe_bbox)

    if states:
        print(f"Successfully retrieved data for {len(states.states)} aircraft.")
        # Print details for the first 5 aircraft found
        for i, s in enumerate(states.states):
            print(f"  Aircraft {i+1}: Callsign='{s.callsign.strip()}', Origin='{s.origin_country}', Altitude={s.geo_altitude}m")
            if i >= 4:
                break
    else:
        # This is the case you were hitting before
        print("API call successful, but no state vectors were returned for the specified area.")
        print("This could be a temporary issue with the OpenSky Network feed.")

except Exception as e:
    print("\n--- An error occurred during the API call ---")
    print(f"Error: {e}")
    traceback.print_exc()
    