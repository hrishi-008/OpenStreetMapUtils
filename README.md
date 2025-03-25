# Paris Accessibility Maps

A collection of interactive maps showing various accessibility features in Paris, France.

## Overview

This project contains several Python scripts that create interactive maps using OpenStreetMap data to visualize different aspects of accessibility in Paris:

1. **Public Transport Accessibility Map**
   - Shows metro stations, bus stops, and RER stations
   - Displays accessibility features for each transport facility
   - Includes information about elevators, escalators, and other accessibility features

2. **Emergency Services Map**
   - Maps hospitals, police stations, fire stations, and pharmacies
   - Shows accessibility features for emergency services
   - Includes emergency contact numbers and service information

3. **School Zone Safety Map**
   - Displays schools and safety infrastructure
   - Shows crosswalks, traffic signals, and other safety features
   - Includes accessibility information for educational facilities

4. **Tourist Guide Map**
   - Maps tourist attractions and points of interest
   - Shows accessibility features for tourist locations
   - Includes information about facilities and services

5. **Restroom Finder Map**
   - Shows public restroom locations
   - Displays accessibility features for restrooms
   - Includes information about facilities and maintenance

## Requirements

- Python 3.7 or higher
- Required packages (install using `pip install -r requirements.txt`):
  - folium
  - geopy
  - pandas
  - numpy
  - requests
  - beautifulsoup4
  - urllib3

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/hrishi-008/OpenStreetMapUtils.git
   cd OpenStreetMapUtils
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Each map can be generated independently using its respective script:

```bash
# Generate Public Transport Accessibility Map
python paris_transport_accessibility.py

# Generate Emergency Services Map
python paris_emergency_services.py

# Generate School Zone Safety Map
python paris_school_safety.py

# Generate Tourist Guide Map
python paris_tourist_guide.py

# Generate Restroom Finder Map
python paris_restroom_finder.py
```

All generated maps will be saved in the `output` directory with timestamped filenames.

## Output

The scripts generate interactive HTML maps that can be opened in any web browser. Each map includes:
- Color-coded markers for different types of facilities
- Interactive popups with detailed information
- Accessibility features and descriptions
- Comprehensive legends
- Layer controls for different map elements

## Project Structure

```
paris-accessibility-maps/
├── README.md
├── requirements.txt
├── output/                    # Create manually (configured automation for some scripts but not all)
├── paris_transport_accessibility.py
├── paris_emergency_services.py
├── paris_school_safety.py
├── paris_tourist_guide.py
└── paris_restroom_finder.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenStreetMap contributors for providing the data
- Folium library for map visualization
- And some of my pair coding partners - OpenAI (ofc i take help from them)