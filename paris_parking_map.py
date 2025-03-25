"""
Paris Parking Availability Map
============================

This script creates an interactive map of parking facilities in Paris using OpenStreetMap data.
It includes information about different types of parking spots, restrictions, and amenities.

Features:
- Maps all parking facilities in Paris
- Shows public parking lots and street parking
- Displays disabled parking spots
- Indicates electric vehicle charging stations
- Shows parking restrictions and time limits
- Includes pricing information
- Provides real-time availability (where available)

Dependencies:
- folium: For creating interactive maps
- pandas: For data manipulation
- requests: For API calls
- geopy: For geocoding
- urllib3: For HTTP requests

Usage:
    python paris_parking_map.py

Output:
    - paris_parking_map.html: Interactive map with parking information
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

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_parking_data():
    """
    Fetch parking facility data from OpenStreetMap using the Overpass API.
    
    Returns:
        tuple: (parking_data, charging_data) containing lists of dictionaries with location information
    """
    # Initialize Nominatim geocoder with a proper user agent
    geolocator = Nominatim(
        user_agent="ParisParkingMap/1.0 (https://github.com/yourusername/paris-parking-map; your.email@example.com)"
    )
    
    # Define the bounding box for Paris
    bbox = {
        'north': 48.9025,
        'south': 48.8156,
        'east': 2.4025,
        'west': 2.2241
    }
    
    # List of parking types
    parking_types = [
        'parking', 'parking_space', 'parking_entrance',
        'parking_lane', 'parking_multi-storey'
    ]
    
    # List of charging station types
    charging_types = [
        'charging_station', 'ev_charging', 'ev_charging_station'
    ]
    
    parking_data = []
    charging_data = []
    
    # Overpass API endpoints
    overpass_endpoints = [
        'https://overpass.kumi.systems/api/interpreter',
        'https://overpass-api.de/api/interpreter',
        'https://maps.mail.ru/osm/tools/overpass/api/interpreter'
    ]
    
    # Fetch parking data
    for parking_type in parking_types:
        print(f"Fetching data for {parking_type}...")
        
        query = f"""
        [out:json][timeout:25];
        (
          node["amenity"="{parking_type}"]({bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']});
          way["amenity"="{parking_type}"]({bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']});
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
                            fee = tags.get('fee', 'unknown')
                            access = tags.get('access', 'unknown')
                            opening_hours = tags.get('opening_hours', 'unknown')
                            capacity = tags.get('capacity', 'unknown')
                            disabled = tags.get('disabled', 'unknown')
                            maxstay = tags.get('maxstay', 'unknown')
                            operator = tags.get('operator', 'unknown')
                            
                            parking_data.append({
                                'lat': float(element['lat']),
                                'lon': float(element['lon']),
                                'name': tags.get('name', parking_type.title()),
                                'type': parking_type,
                                'wheelchair': wheelchair,
                                'fee': fee,
                                'access': access,
                                'opening_hours': opening_hours,
                                'capacity': capacity,
                                'disabled': disabled,
                                'maxstay': maxstay,
                                'operator': operator
                            })
                    
                    success = True
                    print(f"Successfully fetched {parking_type} data from {endpoint}")
                    break
                
            except Exception as e:
                print(f"Error with endpoint {endpoint} for {parking_type}: {str(e)}")
                continue
        
        if not success:
            print(f"Failed to fetch data for {parking_type} from all endpoints")
        
        time.sleep(2)
    
    # Fetch charging station data
    for charging_type in charging_types:
        print(f"Fetching data for {charging_type}...")
        
        query = f"""
        [out:json][timeout:25];
        (
          node["amenity"="{charging_type}"]({bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']});
          way["amenity"="{charging_type}"]({bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']});
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
                            
                            charging_data.append({
                                'lat': float(element['lat']),
                                'lon': float(element['lon']),
                                'name': tags.get('name', charging_type.title()),
                                'type': charging_type,
                                'operator': tags.get('operator', 'unknown'),
                                'socket': tags.get('socket', 'unknown'),
                                'voltage': tags.get('voltage', 'unknown'),
                                'current': tags.get('current', 'unknown'),
                                'fee': tags.get('fee', 'unknown')
                            })
                    
                    success = True
                    print(f"Successfully fetched {charging_type} data from {endpoint}")
                    break
                
            except Exception as e:
                print(f"Error with endpoint {endpoint} for {charging_type}: {str(e)}")
                continue
        
        if not success:
            print(f"Failed to fetch data for {charging_type} from all endpoints")
        
        time.sleep(2)
    
    return parking_data, charging_data

def create_parking_map():
    """
    Create an interactive map of parking facilities in Paris.
    Includes layers for different types of parking and charging stations.
    """
    print("Fetching parking and charging station data in Paris...")
    parking_data, charging_data = get_parking_data()
    
    if not parking_data:
        print("No parking data found. Please try again later.")
        return
    
    # Create a base map centered on Paris
    m = folium.Map(location=[48.8566, 2.3522], zoom_start=13)
    
    # Create marker clusters for different types of parking
    parking_cluster = MarkerCluster(name='Parking Facilities').add_to(m)
    charging_cluster = MarkerCluster(name='Charging Stations').add_to(m)
    
    # Add parking facility markers
    for parking in parking_data:
        # Determine marker color based on type and features
        if parking['disabled'] == 'yes':
            color = 'blue'
        elif parking['fee'] == 'no':
            color = 'green'
        else:
            color = 'red'
        
        # Create popup content with HTML formatting
        popup_content = f"""
        <div style="width: 300px;">
            <h3 style="color: #2c3e50;">{parking['name']}</h3>
            <p><strong>Type:</strong> {parking['type'].replace('_', ' ').title()}</p>
            <p><strong>Access:</strong> {parking['access']}</p>
            <p><strong>Fee:</strong> {parking['fee']}</p>
            <p><strong>Opening Hours:</strong> {parking['opening_hours']}</p>
            <p><strong>Capacity:</strong> {parking['capacity']}</p>
            <p><strong>Disabled Parking:</strong> {parking['disabled']}</p>
            <p><strong>Max Stay:</strong> {parking['maxstay']}</p>
            <p><strong>Operator:</strong> {parking['operator']}</p>
        </div>
        """
        
        folium.CircleMarker(
            location=[parking['lat'], parking['lon']],
            radius=8,
            color=color,
            fill=True,
            popup=popup_content,
            tooltip=parking['name']
        ).add_to(parking_cluster)
    
    # Add charging station markers
    for charging in charging_data:
        # Create popup content
        popup_content = f"""
        <div style="width: 300px;">
            <h3 style="color: #2c3e50;">{charging['name']}</h3>
            <p><strong>Type:</strong> {charging['type'].replace('_', ' ').title()}</p>
            <p><strong>Operator:</strong> {charging['operator']}</p>
            <p><strong>Socket Type:</strong> {charging['socket']}</p>
            <p><strong>Voltage:</strong> {charging['voltage']}</p>
            <p><strong>Current:</strong> {charging['current']}</p>
            <p><strong>Fee:</strong> {charging['fee']}</p>
        </div>
        """
        
        folium.CircleMarker(
            location=[charging['lat'], charging['lon']],
            radius=5,
            color='purple',
            fill=True,
            popup=popup_content,
            tooltip=charging['name']
        ).add_to(charging_cluster)
    
    # Add a legend
    legend_html = '''
    <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; background-color: white; padding: 10px; border: 2px solid grey; border-radius: 5px;">
        <h4>Parking Facilities</h4>
        <p><i class="fa fa-circle" style="color: blue"></i> Disabled Parking</p>
        <p><i class="fa fa-circle" style="color: green"></i> Free Parking</p>
        <p><i class="fa fa-circle" style="color: red"></i> Paid Parking</p>
        <h4>Charging Stations</h4>
        <p><i class="fa fa-circle" style="color: purple"></i> EV Charging</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Save the map with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'output/paris_parking_map_{timestamp}.html'
    m.save(filename)
    print(f"Map has been created and saved as '{filename}'")
    print(f"Found {len(parking_data)} parking facilities and {len(charging_data)} charging stations")

if __name__ == "__main__":
    create_parking_map() 