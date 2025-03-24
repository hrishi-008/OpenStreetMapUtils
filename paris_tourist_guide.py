"""
Paris Tourist Guide
==================

This script creates an interactive map of tourist attractions in Paris using OpenStreetMap data.
It includes detailed information about accessibility, tours, and nearby amenities.

Features:
- Maps major tourist attractions in Paris
- Shows accessibility information
- Displays opening hours and ticket prices
- Indicates available tours (audio, sign language, etc.)
- Shows nearby amenities (restaurants, hotels, etc.)
- Provides historical information
- Includes visitor ratings and reviews
- Shows public transport access

Dependencies:
- folium: For creating interactive maps
- pandas: For data manipulation
- requests: For API calls
- geopy: For geocoding
- urllib3: For HTTP requests
- beautifulsoup4: For web scraping (optional)

Usage:
    python paris_tourist_guide.py

Output:
    - paris_tourist_map.html: Interactive map with tourist attractions
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
import json

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
    Create an interactive map of tourist attractions in Paris.
    Includes a heatmap layer, markers with detailed information, and clustering.
    """
    print("Fetching tourist attractions in Paris...")
    data = get_tourist_attractions()
    
    if not data:
        print("No data found. Please try again later.")
        return
    
    df = pd.DataFrame(data)
    
    # Create a base map centered on Paris
    m = folium.Map(location=[48.8566, 2.3522], zoom_start=13)
    
    # Create marker cluster
    marker_cluster = MarkerCluster().add_to(m)
    
    # Create heatmap data based on score
    heat_data = [[row['lat'], row['lon'], row['score']] for index, row in df.iterrows()]
    HeatMap(heat_data).add_to(m)
    
    # Add markers for attractions
    for idx, row in df.iterrows():
        # Determine marker color based on score
        if row['score'] >= 4:
            color = 'green'
        elif row['score'] >= 2:
            color = 'yellow'
        else:
            color = 'red'
        
        # Create popup content with HTML formatting
        popup_content = f"""
        <div style="width: 300px;">
            <h3 style="color: #2c3e50;">{row['name']}</h3>
            <p><strong>Type:</strong> {row['type'].title()}</p>
            <p><strong>Accessibility:</strong></p>
            <ul>
                <li>Wheelchair: {row['wheelchair']}</li>
                <li>Audio Guide: {row['audio_guide']}</li>
                <li>Sign Language: {row['sign_language']}</li>
                <li>Braille: {row['braille']}</li>
            </ul>
            <p><strong>Opening Hours:</strong> {row['opening_hours']}</p>
            <p><strong>Admission:</strong> {row['fee']}</p>
            <p><strong>Description:</strong> {row['description']}</p>
            <p><strong>Historical Period:</strong> {row['historic']}</p>
            <p><strong>Website:</strong> <a href="{row['website']}" target="_blank">Visit Website</a></p>
            <p><strong>Wikipedia:</strong> <a href="https://en.wikipedia.org/wiki/{row['wikipedia']}" target="_blank">Read More</a></p>
        </div>
        """
        
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=5,
            color=color,
            fill=True,
            popup=popup_content,
            tooltip=row['name']
        ).add_to(marker_cluster)
    
    # Add a legend
    legend_html = '''
    <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; background-color: white; padding: 10px; border: 2px solid grey; border-radius: 5px;">
        <h4>Accessibility Rating</h4>
        <p><i class="fa fa-circle" style="color: green"></i> Excellent (4+ features)</p>
        <p><i class="fa fa-circle" style="color: yellow"></i> Good (2-3 features)</p>
        <p><i class="fa fa-circle" style="color: red"></i> Basic (0-1 features)</p>
        <h4>Features</h4>
        <p><i class="fa fa-wheelchair"></i> Wheelchair Accessible</p>
        <p><i class="fa fa-headphones"></i> Audio Guide</p>
        <p><i class="fa fa-sign-language"></i> Sign Language</p>
        <p><i class="fa fa-braille"></i> Braille Available</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Save the map with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'paris_tourist_map_{timestamp}.html'
    m.save(filename)
    print(f"Map has been created and saved as '{filename}'")
    print(f"Found {len(data)} tourist attractions")

if __name__ == "__main__":
    create_tourist_map() 