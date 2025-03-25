"""
Paris Tourist Guide Map
=====================

This script creates an interactive map of tourist attractions in Paris with detailed accessibility information.
It includes information about museums, monuments, parks, and other points of interest.

Features:
- Maps tourist attractions and points of interest
- Shows accessibility features for each location
- Displays opening hours and admission fees
- Includes historical information
- Provides detailed facility information
- Shows nearby attractions

Dependencies:
- folium: For creating interactive maps
- pandas: For data manipulation
- requests: For API calls
- geopy: For geocoding
- urllib3: For HTTP requests

Usage:
    python paris_tourist_guide.py

Output:
    - output/paris_tourist_guide.html: Interactive map with tourist information
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

def get_tourist_attractions():
    """
    Fetch tourist attraction data from OpenStreetMap using the Overpass API.
    
    Returns:
        list: List of dictionaries containing tourist attraction information
    """
    # Initialize Nominatim geocoder with a proper user agent
    geolocator = Nominatim(
        user_agent="ParisTouristGuide/1.0 (https://github.com/yourusername/paris-tourist-guide; your.email@example.com)"
    )
    
    # Define the bounding box for Paris
    bbox = {
        'north': 48.9025,
        'south': 48.8156,
        'east': 2.4025,
        'west': 2.2241
    }
    
    # List of tourist attraction types
    attraction_types = [
        'museum', 'gallery', 'monument', 'memorial', 'castle', 
        'historic', 'tourism', 'viewpoint', 'artwork'
    ]
    
    data = []
    
    # Overpass API endpoints
    overpass_endpoints = [
        'https://overpass.kumi.systems/api/interpreter',
        'https://overpass-api.de/api/interpreter',
        'https://maps.mail.ru/osm/tools/overpass/api/interpreter'
    ]
    
    for attraction_type in attraction_types:
        print(f"Fetching data for {attraction_type}...")
        
        # Construct the Overpass QL query
        query = f"""
        [out:json][timeout:25];
        (
          node["tourism"="{attraction_type}"]({bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']});
          way["tourism"="{attraction_type}"]({bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']});
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
                            fee = tags.get('fee', 'unknown')
                            website = tags.get('website', '')
                            description = tags.get('description', '')
                            audio_guide = tags.get('audio_guide', 'unknown')
                            sign_language = tags.get('sign_language', 'unknown')
                            braille = tags.get('braille', 'unknown')
                            historic = tags.get('historic', '')
                            wikipedia = tags.get('wikipedia', '')
                            
                            # Calculate accessibility score
                            score = 0
                            if wheelchair == 'yes': score += 2
                            if audio_guide == 'yes': score += 1
                            if sign_language == 'yes': score += 1
                            if braille == 'yes': score += 1
                            
                            data.append({
                                'lat': float(element['lat']),
                                'lon': float(element['lon']),
                                'score': score,
                                'name': tags.get('name', 'Tourist Attraction'),
                                'type': attraction_type,
                                'wheelchair': wheelchair,
                                'opening_hours': opening_hours,
                                'fee': fee,
                                'website': website,
                                'description': description,
                                'audio_guide': audio_guide,
                                'sign_language': sign_language,
                                'braille': braille,
                                'historic': historic,
                                'wikipedia': wikipedia
                            })
                    
                    success = True
                    print(f"Successfully fetched {attraction_type} data from {endpoint}")
                    break
                
            except Exception as e:
                print(f"Error with endpoint {endpoint} for {attraction_type}: {str(e)}")
                continue
        
        if not success:
            print(f"Failed to fetch data for {attraction_type} from all endpoints")
        
        time.sleep(2)
    
    return data

def create_tourist_map():
    """
    Create an interactive map of tourist attractions in Paris with accessibility information.
    """
    print("Fetching tourist attraction data in Paris...")
    tourist_data = get_tourist_attractions()
    
    if not tourist_data:
        print("No tourist attraction data found. Please try again later.")
        return
    
    # Create a base map centered on Paris
    m = folium.Map(location=[48.8566, 2.3522], zoom_start=13)
    
    # Create marker clusters for different types of tourist attractions
    tourist_cluster = MarkerCluster(name='Tourist Attractions').add_to(m)
    
    # Color scheme for different tourist attraction types
    color_scheme = {
        'museum': 'red',
        'monument': 'blue',
        'park': 'green',
        'gallery': 'purple',
        'theatre': 'orange',
        'church': 'darkred',
        'palace': 'gold',
        'garden': 'lightgreen'
    }
    
    # Add tourist attraction markers
    for attraction in tourist_data:
        # Get color based on attraction type
        color = color_scheme.get(attraction['type'], 'gray')
        
        # Create accessibility icons
        accessibility_icons = []
        for feature, value in attraction.items():
            if feature in ['wheelchair', 'audio_guide', 'sign_language', 'braille'] and value == 'yes':
                icon = f'<i class="fa fa-check-circle" style="color: green"></i> {feature.replace("_", " ").title()}'
                accessibility_icons.append(icon)
        
        # Create popup content with HTML formatting
        popup_content = f"""
        <div style="width: 300px;">
            <h3 style="color: #2c3e50;">{attraction['name']}</h3>
            <p><strong>Type:</strong> {attraction['type'].replace('_', ' ').title()}</p>
            <p><strong>Accessibility:</strong></p>
            <ul style="list-style-type: none; padding-left: 0;">
                {''.join(f'<li>{icon}</li>' for icon in accessibility_icons)}
            </ul>
            <p><strong>Opening Hours:</strong> {attraction['opening_hours']}</p>
            <p><strong>Admission:</strong> {attraction['fee']}</p>
            <p><strong>Description:</strong> {attraction['description']}</p>
            <p><strong>Historical Period:</strong> {attraction['historic']}</p>
            <p><strong>Website:</strong> <a href="{attraction['website']}" target="_blank">Visit Website</a></p>
            <p><strong>Wikipedia:</strong> <a href="https://en.wikipedia.org/wiki/{attraction['wikipedia']}" target="_blank">Read More</a></p>
        </div>
        """
        
        folium.CircleMarker(
            location=[attraction['lat'], attraction['lon']],
            radius=8,
            color=color,
            fill=True,
            popup=popup_content,
            tooltip=attraction['name']
        ).add_to(tourist_cluster)
    
    # Add a legend
    legend_html = '''
    <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; background-color: white; padding: 10px; border: 2px solid grey; border-radius: 5px;">
        <h4>Tourist Attractions</h4>
        <p><i class="fa fa-circle" style="color: red"></i> Museum</p>
        <p><i class="fa fa-circle" style="color: blue"></i> Monument</p>
        <p><i class="fa fa-circle" style="color: green"></i> Park</p>
        <p><i class="fa fa-circle" style="color: purple"></i> Gallery</p>
        <p><i class="fa fa-circle" style="color: orange"></i> Theatre</p>
        <p><i class="fa fa-circle" style="color: darkred"></i> Church</p>
        <p><i class="fa fa-circle" style="color: gold"></i> Palace</p>
        <p><i class="fa fa-circle" style="color: lightgreen"></i> Garden</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Ensure output directory exists
    output_dir = ensure_output_directory()
    
    # Save the map with timestamp in the output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(output_dir, f'paris_tourist_guide_{timestamp}.html')
    m.save(filename)
    print(f"Map has been created and saved as '{filename}'")
    print(f"Found {len(tourist_data)} tourist attractions")

if __name__ == "__main__":
    create_tourist_map()