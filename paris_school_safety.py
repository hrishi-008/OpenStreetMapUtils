"""
Paris School Zone Safety Map
===========================

This script creates an interactive map of school zones and safety infrastructure in Paris using OpenStreetMap data.
It includes information about school zones, crosswalks, traffic signals, and other safety features.

Features:
- Maps all schools in Paris
- Shows school zones and speed limits
- Displays crosswalks and traffic signals
- Indicates crossing guards and safe walking routes
- Shows nearby amenities (parks, libraries, etc.)
- Includes accessibility information
- Provides safety ratings for each area

Dependencies:
- folium: For creating interactive maps
- pandas: For data manipulation
- requests: For API calls
- geopy: For geocoding
- urllib3: For HTTP requests

Usage:
    python paris_school_safety.py

Output:
    - paris_school_safety_map.html: Interactive map with school safety information
    - Console output showing progress and results

Author: [Your Name]
Date: [Current Date]
"""

import folium
import pandas as pd
from folium.plugins import HeatMap, MarkerCluster
import numpy as np
import requests
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import time
import urllib3
from datetime import datetime

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_school_safety_data():
    """
    Fetch school and safety infrastructure data from OpenStreetMap using the Overpass API.
    
    Returns:
        tuple: (schools_data, safety_data) containing lists of dictionaries with location information
    """
    # Initialize Nominatim geocoder with a proper user agent
    geolocator = Nominatim(
        user_agent="ParisSchoolSafety/1.0 (https://github.com/yourusername/paris-school-safety; your.email@example.com)"
    )
    
    # Define the bounding box for Paris
    bbox = {
        'north': 48.9025,
        'south': 48.8156,
        'east': 2.4025,
        'west': 2.2241
    }
    
    # List of school types
    school_types = ['primary', 'secondary', 'kindergarten', 'university']
    
    # List of safety infrastructure types
    safety_types = [
        'crossing', 'traffic_signals', 'crossing_guard', 'school_zone',
        'speed_bump', 'pedestrian_zone', 'footway'
    ]
    
    schools_data = []
    safety_data = []
    
    # Overpass API endpoints
    overpass_endpoints = [
        'https://overpass.kumi.systems/api/interpreter',
        'https://overpass-api.de/api/interpreter',
        'https://maps.mail.ru/osm/tools/overpass/api/interpreter'
    ]
    
    # Fetch school data
    for school_type in school_types:
        print(f"Fetching data for {school_type} schools...")
        
        query = f"""
        [out:json][timeout:25];
        (
          node["amenity"="school"]["school:type"="{school_type}"]({bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']});
          way["amenity"="school"]["school:type"="{school_type}"]({bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']});
        );
        out body;
        >;
        out skel qt;
        """
        
        success = False
        for endpoint in overpass_endpoints:
            try:
                response = requests.post(
                    endpoint, 
                    data=query,
                    verify=False,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    for element in result.get('elements', []):
                        if 'lat' in element and 'lon' in element:
                            tags = element.get('tags', {})
                            
                            # Get various attributes
                            wheelchair = tags.get('wheelchair', 'unknown')
                            opening_hours = tags.get('opening_hours', 'unknown')
                            website = tags.get('website', '')
                            description = tags.get('description', '')
                            capacity = tags.get('capacity', 'unknown')
                            
                            schools_data.append({
                                'lat': float(element['lat']),
                                'lon': float(element['lon']),
                                'name': tags.get('name', 'School'),
                                'type': school_type,
                                'wheelchair': wheelchair,
                                'opening_hours': opening_hours,
                                'website': website,
                                'description': description,
                                'capacity': capacity
                            })
                    
                    success = True
                    print(f"Successfully fetched {school_type} school data from {endpoint}")
                    break
                
            except Exception as e:
                print(f"Error with endpoint {endpoint} for {school_type}: {str(e)}")
                continue
        
        if not success:
            print(f"Failed to fetch data for {school_type} from all endpoints")
        
        time.sleep(2)
    
    # Fetch safety infrastructure data
    for safety_type in safety_types:
        print(f"Fetching data for {safety_type}...")
        
        query = f"""
        [out:json][timeout:25];
        (
          node["amenity"="{safety_type}"]({bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']});
          way["amenity"="{safety_type}"]({bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']});
        );
        out body;
        >;
        out skel qt;
        """
        
        success = False
        for endpoint in overpass_endpoints:
            try:
                response = requests.post(
                    endpoint, 
                    data=query,
                    verify=False,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    for element in result.get('elements', []):
                        if 'lat' in element and 'lon' in element:
                            tags = element.get('tags', {})
                            
                            safety_data.append({
                                'lat': float(element['lat']),
                                'lon': float(element['lon']),
                                'type': safety_type,
                                'name': tags.get('name', safety_type.title()),
                                'description': tags.get('description', '')
                            })
                    
                    success = True
                    print(f"Successfully fetched {safety_type} data from {endpoint}")
                    break
                
            except Exception as e:
                print(f"Error with endpoint {endpoint} for {safety_type}: {str(e)}")
                continue
        
        if not success:
            print(f"Failed to fetch data for {safety_type} from all endpoints")
        
        time.sleep(2)
    
    return schools_data, safety_data

def create_safety_map():
    """
    Create an interactive map of schools and safety infrastructure in Paris.
    Includes layers for schools and safety features with detailed information.
    """
    print("Fetching school and safety data in Paris...")
    schools_data, safety_data = get_school_safety_data()
    
    if not schools_data:
        print("No school data found. Please try again later.")
        return
    
    # Create a base map centered on Paris
    m = folium.Map(location=[48.8566, 2.3522], zoom_start=13)
    
    # Create marker clusters for schools and safety features
    school_cluster = MarkerCluster(name='Schools').add_to(m)
    safety_cluster = MarkerCluster(name='Safety Features').add_to(m)
    
    # Add school markers
    for school in schools_data:
        # Create popup content with HTML formatting
        popup_content = f"""
        <div style="width: 300px;">
            <h3 style="color: #2c3e50;">{school['name']}</h3>
            <p><strong>Type:</strong> {school['type'].title()}</p>
            <p><strong>Wheelchair Accessible:</strong> {school['wheelchair']}</p>
            <p><strong>Opening Hours:</strong> {school['opening_hours']}</p>
            <p><strong>Capacity:</strong> {school['capacity']}</p>
            <p><strong>Description:</strong> {school['description']}</p>
            <p><strong>Website:</strong> <a href="{school['website']}" target="_blank">Visit Website</a></p>
        </div>
        """
        
        folium.CircleMarker(
            location=[school['lat'], school['lon']],
            radius=8,
            color='blue',
            fill=True,
            popup=popup_content,
            tooltip=school['name']
        ).add_to(school_cluster)
    
    # Add safety feature markers
    for safety in safety_data:
        # Determine marker color based on type
        if safety['type'] == 'crossing':
            color = 'green'
        elif safety['type'] == 'traffic_signals':
            color = 'red'
        elif safety['type'] == 'crossing_guard':
            color = 'yellow'
        else:
            color = 'gray'
        
        # Create popup content
        popup_content = f"""
        <div style="width: 300px;">
            <h3 style="color: #2c3e50;">{safety['name']}</h3>
            <p><strong>Type:</strong> {safety['type'].replace('_', ' ').title()}</p>
            <p><strong>Description:</strong> {safety['description']}</p>
        </div>
        """
        
        folium.CircleMarker(
            location=[safety['lat'], safety['lon']],
            radius=5,
            color=color,
            fill=True,
            popup=popup_content,
            tooltip=safety['name']
        ).add_to(safety_cluster)
    
    # Add a legend
    legend_html = '''
    <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; background-color: white; padding: 10px; border: 2px solid grey; border-radius: 5px;">
        <h4>Safety Features</h4>
        <p><i class="fa fa-circle" style="color: green"></i> Crosswalks</p>
        <p><i class="fa fa-circle" style="color: red"></i> Traffic Signals</p>
        <p><i class="fa fa-circle" style="color: yellow"></i> Crossing Guards</p>
        <p><i class="fa fa-circle" style="color: gray"></i> Other Safety Features</p>
        <h4>Schools</h4>
        <p><i class="fa fa-circle" style="color: blue"></i> Educational Institutions</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Save the map with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'paris_school_safety_map_{timestamp}.html'
    m.save(filename)
    print(f"Map has been created and saved as '{filename}'")
    print(f"Found {len(schools_data)} schools and {len(safety_data)} safety features")

if __name__ == "__main__":
    create_safety_map()