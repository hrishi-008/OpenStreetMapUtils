import folium
import pandas as pd
from folium.plugins import HeatMap
import numpy as np
import requests
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import time
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_wheelchair_accessible_places():
    # Initialize Nominatim geocoder with a proper user agent
    geolocator = Nominatim(
        user_agent="ParisWheelchairMap/1.0 (https://github.com/yourusername/paris-wheelchair-map; your.email@example.com)"
    )
    
    # Define the bounding box for Paris
    bbox = {
        'north': 48.9025,
        'south': 48.8156,
        'east': 2.4025,
        'west': 2.2241
    }
    
    # List of amenity types to search for
    amenity_types = ['restaurant', 'cafe', 'museum', 'shop', 'bank', 'pharmacy', 'hospital']
    
    data = []
    
    # Overpass API endpoints
    overpass_endpoints = [
        'https://overpass.kumi.systems/api/interpreter',
        'https://overpass-api.de/api/interpreter',
        'https://maps.mail.ru/osm/tools/overpass/api/interpreter'
    ]
    
    for amenity in amenity_types:
        print(f"Fetching data for {amenity}...")
        
        # Construct the Overpass QL query
        query = f"""
        [out:json][timeout:25];
        (
          node["amenity"="{amenity}"]["wheelchair"]({bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']});
          way["amenity"="{amenity}"]["wheelchair"]({bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']});
        );
        out body;
        >;
        out skel qt;
        """
        
        success = False
        for endpoint in overpass_endpoints:
            try:
                # Use the Overpass API with a delay to avoid rate limiting
                response = requests.post(
                    endpoint, 
                    data=query,
                    verify=False,  # Disable SSL verification
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    for element in result.get('elements', []):
                        if 'lat' in element and 'lon' in element:
                            wheelchair_status = element.get('tags', {}).get('wheelchair', 'unknown')
                            weight = 1.0 if wheelchair_status == 'yes' else 0.5 if wheelchair_status == 'limited' else 0.0
                            
                            data.append({
                                'lat': float(element['lat']),
                                'lon': float(element['lon']),
                                'weight': weight,
                                'name': element.get('tags', {}).get('name', 'Unnamed'),
                                'type': element.get('tags', {}).get('amenity', 'Unknown')
                            })
                    
                    success = True
                    print(f"Successfully fetched {amenity} data from {endpoint}")
                    break
                
            except Exception as e:
                print(f"Error with endpoint {endpoint} for {amenity}: {str(e)}")
                continue
        
        if not success:
            print(f"Failed to fetch data for {amenity} from all endpoints")
        
        # Add a delay between requests
        time.sleep(2)
    
    return data

def create_heatmap():
    print("Fetching wheelchair accessible places in Paris...")
    data = get_wheelchair_accessible_places()
    
    if not data:
        print("No data found. Please try again later.")
        return
    
    df = pd.DataFrame(data)
    
    # Create a base map centered on Paris
    m = folium.Map(location=[48.8566, 2.3522], zoom_start=13)
    
    # Create heatmap data
    heat_data = [[row['lat'], row['lon'], row['weight']] for index, row in df.iterrows()]
    
    # Add heatmap layer
    HeatMap(heat_data).add_to(m)
    
    # Add markers for wheelchair accessible places
    for idx, row in df.iterrows():
        if row['weight'] > 0:
            color = 'green' if row['weight'] == 1.0 else 'yellow'
            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=5,
                color=color,
                fill=True,
                popup=f"Name: {row['name']}<br>Type: {row['type']}<br>Accessibility: {'Full' if row['weight'] == 1.0 else 'Limited'}",
                tooltip=row['name']
            ).add_to(m)
    
    # Save the map
    m.save('paris_wheelchair_heatmap.html')
    print(f"Heatmap has been created and saved as 'paris_wheelchair_heatmap.html'")
    print(f"Found {len(data)} wheelchair accessible places")

if __name__ == "__main__":
    create_heatmap() 