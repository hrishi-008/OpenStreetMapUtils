"""
Paris Public Restroom Finder
===========================

This script creates an interactive map of public restrooms in Paris using OpenStreetMap data.
It includes detailed information about accessibility features and facility quality.

Features:
- Maps all public restrooms in Paris
- Shows wheelchair accessibility
- Indicates if facilities are free or paid
- Displays opening hours
- Shows baby changing facilities
- Indicates drinking water availability
- Provides a quality score based on available features

Dependencies:
- folium: For creating interactive maps
- pandas: For data manipulation
- requests: For API calls
- geopy: For geocoding
- urllib3: For HTTP requests

Usage:
    python paris_restroom_finder.py

Output:
    - paris_restroom_map.html: Interactive map with restroom locations
    - Console output showing progress and results

Author: [Your Name]
Date: [Current Date]
"""

import folium
import pandas as pd
from folium.plugins import HeatMap
import numpy as np
import requests
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import time
import urllib3
from datetime import datetime

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_public_restrooms():
    """
    Fetch public restroom data from OpenStreetMap using the Overpass API.
    
    Returns:
        list: List of dictionaries containing restroom information
    """
    # Initialize Nominatim geocoder with a proper user agent
    geolocator = Nominatim(
        user_agent="ParisRestroomFinder/1.0 (https://github.com/yourusername/paris-restroom-finder; your.email@example.com)"
    )
    
    # Define the bounding box for Paris
    bbox = {
        'north': 48.9025,
        'south': 48.8156,
        'east': 2.4025,
        'west': 2.2241
    }
    
    # List of amenity types to search for
    amenity_types = ['toilets', 'wc', 'restroom']
    
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
          node["amenity"="{amenity}"]({bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']});
          way["amenity"="{amenity}"]({bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']});
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
                            tags = element.get('tags', {})
                            
                            # Get various attributes
                            wheelchair = tags.get('wheelchair', 'unknown')
                            fee = tags.get('fee', 'unknown')
                            access = tags.get('access', 'unknown')
                            opening_hours = tags.get('opening_hours', 'unknown')
                            baby_change = tags.get('baby_change', 'unknown')
                            drinking_water = tags.get('drinking_water', 'unknown')
                            
                            # Calculate a score based on available facilities
                            score = 0
                            if wheelchair == 'yes': score += 2
                            if baby_change == 'yes': score += 1
                            if drinking_water == 'yes': score += 1
                            if fee == 'no': score += 1
                            if access == 'public': score += 1
                            
                            data.append({
                                'lat': float(element['lat']),
                                'lon': float(element['lon']),
                                'score': score,
                                'name': tags.get('name', 'Public Restroom'),
                                'wheelchair': wheelchair,
                                'fee': fee,
                                'access': access,
                                'opening_hours': opening_hours,
                                'baby_change': baby_change,
                                'drinking_water': drinking_water
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

def create_restroom_map():
    """
    Create an interactive map of public restrooms in Paris.
    Includes a heatmap layer and markers with detailed information.
    """
    print("Fetching public restrooms in Paris...")
    data = get_public_restrooms()
    
    if not data:
        print("No data found. Please try again later.")
        return
    
    df = pd.DataFrame(data)
    
    # Create a base map centered on Paris
    m = folium.Map(location=[48.8566, 2.3522], zoom_start=13)
    
    # Create heatmap data based on score
    heat_data = [[row['lat'], row['lon'], row['score']] for index, row in df.iterrows()]
    
    # Add heatmap layer
    HeatMap(heat_data).add_to(m)
    
    # Add markers for restrooms
    for idx, row in df.iterrows():
        # Determine marker color based on score
        if row['score'] >= 4:
            color = 'green'
        elif row['score'] >= 2:
            color = 'yellow'
        else:
            color = 'red'
        
        # Create popup content
        popup_content = f"""
        <b>{row['name']}</b><br>
        Wheelchair Accessible: {row['wheelchair']}<br>
        Free: {row['fee']}<br>
        Access: {row['access']}<br>
        Opening Hours: {row['opening_hours']}<br>
        Baby Change: {row['baby_change']}<br>
        Drinking Water: {row['drinking_water']}
        """
        
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=5,
            color=color,
            fill=True,
            popup=popup_content,
            tooltip=row['name']
        ).add_to(m)
    
    # Add a legend
    legend_html = '''
    <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; background-color: white; padding: 10px; border: 2px solid grey; border-radius: 5px;">
        <h4>Restroom Quality</h4>
        <p><i class="fa fa-circle" style="color: green"></i> Excellent (4+ features)</p>
        <p><i class="fa fa-circle" style="color: yellow"></i> Good (2-3 features)</p>
        <p><i class="fa fa-circle" style="color: red"></i> Basic (0-1 features)</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Save the map with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'paris_restroom_map_{timestamp}.html'
    m.save(filename)
    print(f"Map has been created and saved as '{filename}'")
    print(f"Found {len(data)} public restrooms")

if __name__ == "__main__":
    create_restroom_map() 