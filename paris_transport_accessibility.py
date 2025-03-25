"""
Paris Public Transport Accessibility Map
=====================================

This script creates an interactive map of public transport facilities in Paris with detailed accessibility information.
It includes information about metro stations, bus stops, and RER stations with their accessibility features.

Features:
- Maps public transport locations (metro, bus, RER stations)
- Shows accessibility features for each station
- Displays operating hours and service information
- Includes elevator and escalator information
- Provides detailed accessibility information
- Shows nearby accessible facilities

Dependencies:
- folium: For creating interactive maps
- pandas: For data manipulation
- requests: For API calls
- geopy: For geocoding
- urllib3: For HTTP requests

Usage:
    python paris_transport_accessibility.py

Output:
    - output/paris_transport_accessibility.html: Interactive map with transport accessibility information
    - Console output showing progress and results

Author: [Your Name]
Date: [Current Date]
"""

import folium
import pandas as pd
from folium.plugins import MarkerCluster
import numpy as np
import requests
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import time
import urllib3
from datetime import datetime
import os

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def ensure_output_directory():
    """
    Create output directory if it doesn't exist.
    """
    output_dir = 'output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir

def get_transport_data():
    """
    Fetch public transport data from OpenStreetMap using the Overpass API.
    
    Returns:
        list: List of dictionaries containing transport facility information
    """
    # Initialize Nominatim geocoder with a proper user agent
    geolocator = Nominatim(
        user_agent="ParisTransportAccessibility/1.0 (https://github.com/yourusername/paris-transport-accessibility; your.email@example.com)"
    )
    
    # Define the bounding box for Paris
    bbox = {
        'north': 48.9025,
        'south': 48.8156,
        'east': 2.4025,
        'west': 2.2241
    }
    
    # List of transport facility types
    transport_types = [
        'subway_entrance', 'subway_station', 'bus_station', 'bus_stop',
        'train_station', 'railway_station', 'station', 'platform'
    ]
    
    # List of accessibility features
    accessibility_features = [
        'wheelchair', 'elevator', 'escalator', 'lift',
        'tactile_paving', 'braille', 'audio_announcements',
        'visual_announcements', 'wide_door', 'ramp',
        'accessible_toilet', 'guide_dog', 'step_free_access',
        'level_access', 'platform_height', 'platform_slope'
    ]
    
    transport_data = []
    
    # Overpass API endpoints
    overpass_endpoints = [
        'https://overpass.kumi.systems/api/interpreter',
        'https://overpass-api.de/api/interpreter',
        'https://maps.mail.ru/osm/tools/overpass/api/interpreter'
    ]
    
    # Fetch transport facility data
    for facility_type in transport_types:
        print(f"Fetching data for {facility_type}...")
        
        query = f"""
        [out:json][timeout:25];
        (
          node["public_transport"="{facility_type}"]({bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']});
          way["public_transport"="{facility_type}"]({bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']});
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
                            operator = tags.get('operator', 'unknown')
                            network = tags.get('network', 'unknown')
                            ref = tags.get('ref', 'unknown')
                            name = tags.get('name', facility_type.title())
                            
                            # Get transport-specific attributes
                            lines = tags.get('lines', 'unknown')
                            routes = tags.get('routes', 'unknown')
                            station_type = tags.get('station', 'unknown')
                            platform_level = tags.get('platform:level', 'unknown')
                            
                            # Get accessibility features
                            accessibility = {}
                            for feature in accessibility_features:
                                accessibility[feature] = tags.get(feature, 'unknown')
                            
                            transport_data.append({
                                'lat': float(element['lat']),
                                'lon': float(element['lon']),
                                'name': name,
                                'type': facility_type,
                                'wheelchair': wheelchair,
                                'opening_hours': opening_hours,
                                'operator': operator,
                                'network': network,
                                'ref': ref,
                                'lines': lines,
                                'routes': routes,
                                'station_type': station_type,
                                'platform_level': platform_level,
                                'accessibility': accessibility
                            })
                    
                    success = True
                    print(f"Successfully fetched {facility_type} data from {endpoint}")
                    break
                
            except Exception as e:
                print(f"Error with endpoint {endpoint} for {facility_type}: {str(e)}")
                continue
        
        if not success:
            print(f"Failed to fetch data for {facility_type} from all endpoints")
        
        time.sleep(2)
    
    return transport_data

def create_transport_map():
    """
    Create an interactive map of public transport facilities in Paris with accessibility information.
    """
    print("Fetching public transport data in Paris...")
    transport_data = get_transport_data()
    
    if not transport_data:
        print("No transport facility data found. Please try again later.")
        return
    
    # Create a base map centered on Paris
    m = folium.Map(location=[48.8566, 2.3522], zoom_start=13)
    
    # Create marker clusters for different types of transport facilities
    transport_cluster = MarkerCluster(name='Public Transport').add_to(m)
    
    # Color scheme for different transport facility types
    color_scheme = {
        'subway_entrance': 'red',
        'subway_station': 'darkred',
        'bus_station': 'blue',
        'bus_stop': 'lightblue',
        'train_station': 'green',
        'railway_station': 'darkgreen',
        'station': 'purple',
        'platform': 'orange'
    }
    
    # Add transport facility markers
    for facility in transport_data:
        # Get color based on facility type
        color = color_scheme.get(facility['type'], 'gray')
        
        # Create accessibility icons
        accessibility_icons = []
        for feature, value in facility['accessibility'].items():
            if value == 'yes':
                icon = f'<i class="fa fa-check-circle" style="color: green"></i> {feature.replace("_", " ").title()}'
                accessibility_icons.append(icon)
        
        # Create popup content with HTML formatting
        popup_content = f"""
        <div style="width: 300px;">
            <h3 style="color: #2c3e50;">{facility['name']}</h3>
            <p><strong>Type:</strong> {facility['type'].replace('_', ' ').title()}</p>
            <p><strong>Network:</strong> {facility['network']}</p>
            <p><strong>Operator:</strong> {facility['operator']}</p>
            <p><strong>Reference:</strong> {facility['ref']}</p>
            <p><strong>Lines:</strong> {facility['lines']}</p>
            <p><strong>Routes:</strong> {facility['routes']}</p>
            <p><strong>Opening Hours:</strong> {facility['opening_hours']}</p>
            <p><strong>Station Type:</strong> {facility['station_type']}</p>
            <p><strong>Platform Level:</strong> {facility['platform_level']}</p>
            <p><strong>Wheelchair Access:</strong> {facility['wheelchair']}</p>
            <h4>Accessibility Features:</h4>
            <ul style="list-style-type: none; padding-left: 0;">
                {''.join(f'<li>{icon}</li>' for icon in accessibility_icons)}
            </ul>
            <div style="margin-top: 10px; padding: 10px; background-color: #f8f9fa; border-radius: 5px;">
                <h4 style="color: #2c3e50;">Transport Information:</h4>
                <p><strong>Metro:</strong> Lines 1-14</p>
                <p><strong>RER:</strong> Lines A, B, C, D, E</p>
                <p><strong>Bus:</strong> 350+ routes</p>
                <p><strong>Night Bus:</strong> 47 Noctilien routes</p>
            </div>
        </div>
        """
        
        folium.CircleMarker(
            location=[facility['lat'], facility['lon']],
            radius=8,
            color=color,
            fill=True,
            popup=popup_content,
            tooltip=facility['name']
        ).add_to(transport_cluster)
    
    # Add a legend
    legend_html = '''
    <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; background-color: white; padding: 10px; border: 2px solid grey; border-radius: 5px;">
        <h4>Public Transport Facilities</h4>
        <p><i class="fa fa-circle" style="color: red"></i> Metro Entrance</p>
        <p><i class="fa fa-circle" style="color: darkred"></i> Metro Station</p>
        <p><i class="fa fa-circle" style="color: blue"></i> Bus Station</p>
        <p><i class="fa fa-circle" style="color: lightblue"></i> Bus Stop</p>
        <p><i class="fa fa-circle" style="color: green"></i> Train Station</p>
        <p><i class="fa fa-circle" style="color: darkgreen"></i> Railway Station</p>
        <p><i class="fa fa-circle" style="color: purple"></i> Station</p>
        <p><i class="fa fa-circle" style="color: orange"></i> Platform</p>
        <div style="margin-top: 10px; padding: 10px; background-color: #f8f9fa; border-radius: 5px;">
            <h4 style="color: #2c3e50;">Transport Information:</h4>
            <p><strong>Metro:</strong> Lines 1-14</p>
            <p><strong>RER:</strong> Lines A, B, C, D, E</p>
            <p><strong>Bus:</strong> 350+ routes</p>
            <p><strong>Night Bus:</strong> 47 Noctilien routes</p>
        </div>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Ensure output directory exists
    output_dir = ensure_output_directory()
    
    # Save the map with timestamp in the output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(output_dir, f'paris_transport_accessibility_{timestamp}.html')
    m.save(filename)
    print(f"Map has been created and saved as '{filename}'")
    print(f"Found {len(transport_data)} transport facilities")

if __name__ == "__main__":
    create_transport_map() 