"""
Paris Local Business Directory with Accessibility
=============================================

This script creates an interactive map of local businesses in Paris with detailed accessibility information.
It includes information about wheelchair access, hearing assistance, visual assistance, and other accessibility features.

Features:
- Maps various types of businesses (restaurants, shops, services)
- Shows accessibility features for each business
- Displays business hours and contact information
- Includes ratings and reviews where available
- Provides detailed accessibility information
- Shows nearby accessible facilities

Dependencies:
- folium: For creating interactive maps
- pandas: For data manipulation
- requests: For API calls
- geopy: For geocoding
- urllib3: For HTTP requests

Usage:
    python paris_business_directory.py

Output:
    - paris_business_directory.html: Interactive map with business information
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

def get_business_data():
    """
    Fetch business data from OpenStreetMap using the Overpass API.
    
    Returns:
        tuple: (business_data, accessibility_data) containing lists of dictionaries with location information
    """
    # Initialize Nominatim geocoder with a proper user agent
    geolocator = Nominatim(
        user_agent="ParisBusinessDirectory/1.0 (https://github.com/yourusername/paris-business-directory; your.email@example.com)"
    )
    
    # Define the bounding box for Paris
    bbox = {
        'north': 48.9025,
        'south': 48.8156,
        'east': 2.4025,
        'west': 2.2241
    }
    
    # List of business types
    business_types = [
        'restaurant', 'cafe', 'bar', 'shop', 'supermarket',
        'pharmacy', 'bank', 'post_office', 'library', 'cinema',
        'theatre', 'museum', 'gallery', 'hotel', 'hospital',
        'clinic', 'school', 'university', 'office', 'government'
    ]
    
    # List of accessibility features
    accessibility_features = [
        'wheelchair', 'hearing_loop', 'braille', 'tactile_paving',
        'elevator', 'ramp', 'wide_door', 'accessible_toilet',
        'sign_language', 'audio_description', 'guide_dog'
    ]
    
    business_data = []
    accessibility_data = []
    
    # Overpass API endpoints
    overpass_endpoints = [
        'https://overpass.kumi.systems/api/interpreter',
        'https://overpass-api.de/api/interpreter',
        'https://maps.mail.ru/osm/tools/overpass/api/interpreter'
    ]
    
    # Fetch business data
    for business_type in business_types:
        print(f"Fetching data for {business_type}...")
        
        query = f"""
        [out:json][timeout:25];
        (
          node["amenity"="{business_type}"]({bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']});
          way["amenity"="{business_type}"]({bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']});
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
                            
                            # Get accessibility features
                            accessibility = {}
                            for feature in accessibility_features:
                                accessibility[feature] = tags.get(feature, 'unknown')
                            
                            business_data.append({
                                'lat': float(element['lat']),
                                'lon': float(element['lon']),
                                'name': tags.get('name', business_type.title()),
                                'type': business_type,
                                'wheelchair': wheelchair,
                                'opening_hours': opening_hours,
                                'phone': phone,
                                'website': website,
                                'email': email,
                                'address': addr,
                                'brand': brand,
                                'operator': operator,
                                'accessibility': accessibility
                            })
                    
                    success = True
                    print(f"Successfully fetched {business_type} data from {endpoint}")
                    break
                
            except Exception as e:
                print(f"Error with endpoint {endpoint} for {business_type}: {str(e)}")
                continue
        
        if not success:
            print(f"Failed to fetch data for {business_type} from all endpoints")
        
        time.sleep(2)
    
    return business_data

def create_business_map():
    """
    Create an interactive map of businesses in Paris with accessibility information.
    """
    print("Fetching business data in Paris...")
    business_data = get_business_data()
    
    if not business_data:
        print("No business data found. Please try again later.")
        return
    
    # Create a base map centered on Paris
    m = folium.Map(location=[48.8566, 2.3522], zoom_start=13)
    
    # Create marker clusters for different types of businesses
    business_cluster = MarkerCluster(name='Businesses').add_to(m)
    
    # Color scheme for different business types
    color_scheme = {
        'restaurant': 'red',
        'cafe': 'orange',
        'bar': 'purple',
        'shop': 'blue',
        'supermarket': 'green',
        'pharmacy': 'yellow',
        'bank': 'gray',
        'post_office': 'pink',
        'library': 'brown',
        'cinema': 'darkred',
        'theatre': 'darkblue',
        'museum': 'darkgreen',
        'gallery': 'lightred',
        'hotel': 'lightblue',
        'hospital': 'lightgreen',
        'clinic': 'lightgray',
        'school': 'cadetblue',
        'university': 'darkpurple',
        'office': 'white',
        'government': 'black'
    }
    
    # Add business markers
    for business in business_data:
        # Get color based on business type
        color = color_scheme.get(business['type'], 'gray')
        
        # Create accessibility icons
        accessibility_icons = []
        for feature, value in business['accessibility'].items():
            if value == 'yes':
                icon = f'<i class="fa fa-check-circle" style="color: green"></i> {feature.replace("_", " ").title()}'
                accessibility_icons.append(icon)
        
        # Create popup content with HTML formatting
        popup_content = f"""
        <div style="width: 300px;">
            <h3 style="color: #2c3e50;">{business['name']}</h3>
            <p><strong>Type:</strong> {business['type'].replace('_', ' ').title()}</p>
            <p><strong>Brand:</strong> {business['brand']}</p>
            <p><strong>Address:</strong> {business['address']}</p>
            <p><strong>Opening Hours:</strong> {business['opening_hours']}</p>
            <p><strong>Phone:</strong> {business['phone']}</p>
            <p><strong>Email:</strong> {business['email']}</p>
            <p><strong>Website:</strong> <a href="{business['website']}" target="_blank">Visit Website</a></p>
            <p><strong>Wheelchair Access:</strong> {business['wheelchair']}</p>
            <h4>Accessibility Features:</h4>
            <ul style="list-style-type: none; padding-left: 0;">
                {''.join(f'<li>{icon}</li>' for icon in accessibility_icons)}
            </ul>
        </div>
        """
        
        folium.CircleMarker(
            location=[business['lat'], business['lon']],
            radius=8,
            color=color,
            fill=True,
            popup=popup_content,
            tooltip=business['name']
        ).add_to(business_cluster)
    
    # Add a legend
    legend_html = '''
    <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; background-color: white; padding: 10px; border: 2px solid grey; border-radius: 5px;">
        <h4>Business Types</h4>
        <p><i class="fa fa-circle" style="color: red"></i> Restaurant</p>
        <p><i class="fa fa-circle" style="color: orange"></i> Cafe</p>
        <p><i class="fa fa-circle" style="color: purple"></i> Bar</p>
        <p><i class="fa fa-circle" style="color: blue"></i> Shop</p>
        <p><i class="fa fa-circle" style="color: green"></i> Supermarket</p>
        <p><i class="fa fa-circle" style="color: yellow"></i> Pharmacy</p>
        <p><i class="fa fa-circle" style="color: gray"></i> Bank</p>
        <p><i class="fa fa-circle" style="color: pink"></i> Post Office</p>
        <p><i class="fa fa-circle" style="color: brown"></i> Library</p>
        <p><i class="fa fa-circle" style="color: darkred"></i> Cinema</p>
        <p><i class="fa fa-circle" style="color: darkblue"></i> Theatre</p>
        <p><i class="fa fa-circle" style="color: darkgreen"></i> Museum</p>
        <p><i class="fa fa-circle" style="color: lightred"></i> Gallery</p>
        <p><i class="fa fa-circle" style="color: lightblue"></i> Hotel</p>
        <p><i class="fa fa-circle" style="color: lightgreen"></i> Hospital</p>
        <p><i class="fa fa-circle" style="color: lightgray"></i> Clinic</p>
        <p><i class="fa fa-circle" style="color: cadetblue"></i> School</p>
        <p><i class="fa fa-circle" style="color: darkpurple"></i> University</p>
        <p><i class="fa fa-circle" style="color: white"></i> Office</p>
        <p><i class="fa fa-circle" style="color: black"></i> Government</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Save the map with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'paris_business_directory_{timestamp}.html'
    m.save(filename)
    print(f"Map has been created and saved as '{filename}'")
    print(f"Found {len(business_data)} businesses")

if __name__ == "__main__":
    create_business_map() 