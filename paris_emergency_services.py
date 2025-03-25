"""
Paris Emergency Service Locator
============================

This script creates an interactive map of emergency services in Paris with detailed accessibility information.
It includes information about hospitals, police stations, fire stations, and 24-hour pharmacies.

Features:
- Maps emergency service locations (hospitals, police, fire stations, pharmacies)
- Shows accessibility features for each service
- Displays operating hours and contact information
- Includes emergency contact numbers
- Provides detailed accessibility information
- Shows nearby emergency services

Dependencies:
- folium: For creating interactive maps
- pandas: For data manipulation
- requests: For API calls
- geopy: For geocoding
- urllib3: For HTTP requests

Usage:
    python paris_emergency_services.py

Output:
    - paris_emergency_services.html: Interactive map with emergency service information
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

def get_emergency_data():
    """
    Fetch emergency service data from OpenStreetMap using the Overpass API.
    
    Returns:
        list: List of dictionaries containing emergency service information
    """
    # Initialize Nominatim geocoder with a proper user agent
    geolocator = Nominatim(
        user_agent="ParisEmergencyServices/1.0 (https://github.com/yourusername/paris-emergency-services; your.email@example.com)"
    )
    
    # Define the bounding box for Paris
    bbox = {
        'north': 48.9025,
        'south': 48.8156,
        'east': 2.4025,
        'west': 2.2241
    }
    
    # List of emergency service types
    emergency_types = [
        'hospital', 'police', 'fire_station', 'pharmacy',
        'emergency_ward', 'ambulance_station', 'emergency_phone'
    ]
    
    # List of accessibility features
    accessibility_features = [
        'wheelchair', 'hearing_loop', 'braille', 'tactile_paving',
        'elevator', 'ramp', 'wide_door', 'accessible_toilet',
        'sign_language', 'audio_description', 'guide_dog',
        'emergency_phone', 'emergency_lighting'
    ]
    
    emergency_data = []
    
    # Overpass API endpoints
    overpass_endpoints = [
        'https://overpass.kumi.systems/api/interpreter',
        'https://overpass-api.de/api/interpreter',
        'https://maps.mail.ru/osm/tools/overpass/api/interpreter'
    ]
    
    # Fetch emergency service data
    for service_type in emergency_types:
        print(f"Fetching data for {service_type}...")
        
        query = f"""
        [out:json][timeout:25];
        (
          node["amenity"="{service_type}"]({bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']});
          way["amenity"="{service_type}"]({bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']});
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
                            phone = tags.get('phone', 'unknown')
                            website = tags.get('website', 'unknown')
                            email = tags.get('email', 'unknown')
                            addr = tags.get('addr:full', 'unknown')
                            brand = tags.get('brand', 'unknown')
                            operator = tags.get('operator', 'unknown')
                            
                            # Get emergency-specific attributes
                            emergency = tags.get('emergency', 'unknown')
                            emergency_phone = tags.get('emergency_phone', 'unknown')
                            emergency_lighting = tags.get('emergency_lighting', 'unknown')
                            
                            # Get accessibility features
                            accessibility = {}
                            for feature in accessibility_features:
                                accessibility[feature] = tags.get(feature, 'unknown')
                            
                            emergency_data.append({
                                'lat': float(element['lat']),
                                'lon': float(element['lon']),
                                'name': tags.get('name', service_type.title()),
                                'type': service_type,
                                'wheelchair': wheelchair,
                                'opening_hours': opening_hours,
                                'phone': phone,
                                'website': website,
                                'email': email,
                                'address': addr,
                                'brand': brand,
                                'operator': operator,
                                'emergency': emergency,
                                'emergency_phone': emergency_phone,
                                'emergency_lighting': emergency_lighting,
                                'accessibility': accessibility
                            })
                    
                    success = True
                    print(f"Successfully fetched {service_type} data from {endpoint}")
                    break
                
            except Exception as e:
                print(f"Error with endpoint {endpoint} for {service_type}: {str(e)}")
                continue
        
        if not success:
            print(f"Failed to fetch data for {service_type} from all endpoints")
        
        time.sleep(2)
    
    return emergency_data

def create_emergency_map():
    """
    Create an interactive map of emergency services in Paris with accessibility information.
    """
    print("Fetching emergency service data in Paris...")
    emergency_data = get_emergency_data()
    
    if not emergency_data:
        print("No emergency service data found. Please try again later.")
        return
    
    # Create a base map centered on Paris
    m = folium.Map(location=[48.8566, 2.3522], zoom_start=13)
    
    # Create marker clusters for different types of emergency services
    emergency_cluster = MarkerCluster(name='Emergency Services').add_to(m)
    
    # Color scheme for different emergency service types
    color_scheme = {
        'hospital': 'red',
        'police': 'blue',
        'fire_station': 'orange',
        'pharmacy': 'green',
        'emergency_ward': 'darkred',
        'ambulance_station': 'lightred',
        'emergency_phone': 'purple'
    }
    
    # Add emergency service markers
    for service in emergency_data:
        # Get color based on service type
        color = color_scheme.get(service['type'], 'gray')
        
        # Create accessibility icons
        accessibility_icons = []
        for feature, value in service['accessibility'].items():
            if value == 'yes':
                icon = f'<i class="fa fa-check-circle" style="color: green"></i> {feature.replace("_", " ").title()}'
                accessibility_icons.append(icon)
        
        # Create popup content with HTML formatting
        popup_content = f"""
        <div style="width: 300px;">
            <h3 style="color: #2c3e50;">{service['name']}</h3>
            <p><strong>Type:</strong> {service['type'].replace('_', ' ').title()}</p>
            <p><strong>Brand:</strong> {service['brand']}</p>
            <p><strong>Address:</strong> {service['address']}</p>
            <p><strong>Opening Hours:</strong> {service['opening_hours']}</p>
            <p><strong>Phone:</strong> {service['phone']}</p>
            <p><strong>Emergency Phone:</strong> {service['emergency_phone']}</p>
            <p><strong>Email:</strong> {service['email']}</p>
            <p><strong>Website:</strong> <a href="{service['website']}" target="_blank">Visit Website</a></p>
            <p><strong>Wheelchair Access:</strong> {service['wheelchair']}</p>
            <p><strong>Emergency Lighting:</strong> {service['emergency_lighting']}</p>
            <h4>Accessibility Features:</h4>
            <ul style="list-style-type: none; padding-left: 0;">
                {''.join(f'<li>{icon}</li>' for icon in accessibility_icons)}
            </ul>
            <div style="margin-top: 10px; padding: 10px; background-color: #f8f9fa; border-radius: 5px;">
                <h4 style="color: #dc3545;">Emergency Numbers:</h4>
                <p><strong>Police:</strong> 17</p>
                <p><strong>Fire:</strong> 18</p>
                <p><strong>Ambulance:</strong> 15</p>
                <p><strong>European Emergency:</strong> 112</p>
            </div>
        </div>
        """
        
        folium.CircleMarker(
            location=[service['lat'], service['lon']],
            radius=8,
            color=color,
            fill=True,
            popup=popup_content,
            tooltip=service['name']
        ).add_to(emergency_cluster)
    
    # Add a legend
    legend_html = '''
    <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; background-color: white; padding: 10px; border: 2px solid grey; border-radius: 5px;">
        <h4>Emergency Services</h4>
        <p><i class="fa fa-circle" style="color: red"></i> Hospital</p>
        <p><i class="fa fa-circle" style="color: blue"></i> Police Station</p>
        <p><i class="fa fa-circle" style="color: orange"></i> Fire Station</p>
        <p><i class="fa fa-circle" style="color: green"></i> Pharmacy</p>
        <p><i class="fa fa-circle" style="color: darkred"></i> Emergency Ward</p>
        <p><i class="fa fa-circle" style="color: lightred"></i> Ambulance Station</p>
        <p><i class="fa fa-circle" style="color: purple"></i> Emergency Phone</p>
        <div style="margin-top: 10px; padding: 10px; background-color: #f8f9fa; border-radius: 5px;">
            <h4 style="color: #dc3545;">Emergency Numbers:</h4>
            <p><strong>Police:</strong> 17</p>
            <p><strong>Fire:</strong> 18</p>
            <p><strong>Ambulance:</strong> 15</p>
            <p><strong>European Emergency:</strong> 112</p>
        </div>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Save the map with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'paris_emergency_services_{timestamp}.html'
    m.save(filename)
    print(f"Map has been created and saved as '{filename}'")
    print(f"Found {len(emergency_data)} emergency services")

if __name__ == "__main__":
    create_emergency_map() 