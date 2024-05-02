from flask import Flask, jsonify, render_template
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import folium
import json
import os

app = Flask(__name__)

API_KEY = 'd3273b2c8bba1f586f4a07acd3e4559e'  # Replace with your actual API key from OpenWeatherMap.org

# List of San Antonio zip codes and their corresponding latitudes and longitudes
san_antonio_zip_codes = {
    78201: (29.4245, -98.4951), 78202: (29.4279, -98.4629), 78203: (29.4072, -98.4595), 78204: (29.4031, -98.5065),
    78205: (29.4241, -98.4936), 78206: (29.4148, -98.4785), 78207: (29.4226, -98.5261), 78208: (29.4392, -98.4644),
    78209: (29.4907, -98.4539), 78210: (29.3954, -98.4644), 78211: (29.3424, -98.5701), 78212: (29.4668, -98.4959),
    78213: (29.5165, -98.5218), 78214: (29.3253, -98.4709), 78215: (29.4418, -98.4805), 78216: (29.5372, -98.4883),
    78217: (29.5385, -98.4153), 78218: (29.4846, -98.3971), 78219: (29.4440, -98.3874), 78220: (29.4163, -98.3911),
    78221: (29.3534, -98.4843), 78222: (29.3546, -98.3712), 78223: (29.3092, -98.5286), 78224: (29.3058, -98.5521),
    78225: (29.3876, -98.5259), 78226: (29.3846, -98.5688), 78227: (29.4063, -98.6304), 78228: (29.4604, -98.5718),
    78229: (29.5052, -98.5706), 78230: (29.5452, -98.5571), 78231: (29.5782, -98.5429), 78232: (29.5901, -98.4739),
    78233: (29.5579, -98.3612), 78234: (29.4601, -98.4383), 78235: (29.3429, -98.4436), 78236: (29.3894, -98.6187),
    78237: (29.4195, -98.5702), 78238: (29.4714, -98.6166), 78239: (29.5201, -98.3604), 78240: (29.5264, -98.6161),
    78241: (29.3304, -98.3858), 78242: (29.3502, -98.6084), 78243: (29.3745, -98.3912), 78244: (29.4733, -98.3482),
    78245: (29.4012, -98.7304), 78246: (29.5318, -98.4305), 78247: (29.5860, -98.4060), 78248: (29.5887, -98.5257),
    78249: (29.5673, -98.6130), 78250: (29.5019, -98.6727), 78251: (29.4636, -98.6766), 78252: (29.4184, -98.7417),
    78253: (29.4686, -98.8101), 78254: (29.5468, -98.7278), 78255: (29.6511, -98.6563), 78256: (29.6236, -98.6205),
    78257: (29.6614, -98.5831), 78258: (29.6353, -98.4960), 78259: (29.6272, -98.4272), 78260: (29.6974, -98.4848),
    78261: (29.2417, -98.8285), 78263: (29.3631, -98.0983), 78264: (29.1962, -98.5172), 78265: (29.7441, -98.6535),
    78266: (29.8224, -98.7378), 78268: (29.1405, -98.2572), 78269: (29.1186, -98.6653), 78270: (29.8640, -98.5301),
    78278: (29.6298, -98.3484), 78279: (29.5668, -98.2646), 78280: (29.2361, -98.6543), 78283: (29.0489, -98.8093),
    78284: (29.9368, -98.7394), 78285: (29.3526, -99.1975), 78288: (29.6714, -98.7197), 78289: (28.9586, -98.5855),
    78291: (29.5793, -98.2983), 78292: (29.2014, -98.1341), 78293: (29.2133, -98.3709), 78294: (29.3484, -98.8949),
    78295: (28.8305, -98.5439), 78296: (29.8101, -99.0170), 78297: (28.7986, -98.4568), 78298: (29.2715, -98.8521),
    78299: (28.9648, -98.8203) 
}

# Configure the retry mechanism for API requests
retry_strategy = Retry(
    total=3,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)
http.mount("http://", adapter)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/map')
def san_antonio_map():
    map_center = (29.4241, -98.4936)  # Center coordinates for San Antonio
    zoom_level = 10  # Adjust the zoom level as needed

    # Create a Folium map centered on San Antonio
    san_antonio_map = folium.Map(location=map_center, zoom_start=zoom_level)

    # Load the GeoJSON file with Texas zip code boundaries
    with open('tx_texas_zip_codes_geo.min.json') as file:
        zip_code_data = json.load(file)

# Add the San Antonio zip code boundaries as a base map layer
    folium.GeoJson(
        zip_code_data,
        name='San Antonio Zip Code Boundaries',
        style_function=lambda feature: {
            'fillColor': 'transparent',
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.7
        } if feature['properties']['ZCTA5CE10'] in san_antonio_zip_codes and feature.get('geometry') else {}
    ).add_to(san_antonio_map)

    # Add markers for each zip code with weather data
    for zipcode, coords in san_antonio_zip_codes.items():
        # Make an API request to OpenWeatherMap.org for each zipcode
        print('API START')
        url = f'http://api.openweathermap.org/data/2.5/weather?zip={zipcode},us&appid={API_KEY}'
        response = http.get(url)  # Set a timeout of 10 seconds for each request
        print(response)
        print('API END')
        if response.status_code == 200:
            data = response.json()
            
            # Extract relevant weather information and convert temperature to Fahrenheit
            weather_info = f"""
                <b>Zip Code:</b> {zipcode}<br>
                <b>Description:</b> {data['weather'][0]['description']}<br>
                <b>Temperature:</b> {round((data['main']['temp'] - 273.15) * 9/5 + 32, 2)}°F<br>
                <b>Humidity:</b> {data['main']['humidity']}%<br>
                <b>Wind Speed:</b> {data['wind']['speed']} m/s
            """
            
            # Add a marker for the zip code with the weather information
            folium.Marker(coords, popup=weather_info).add_to(san_antonio_map)
        else:
            # Handle API request error
            print(f"Error retrieving weather data for zip code {zipcode}. Status code: {response.status_code}")

    # Generate the map HTML
    map_html = san_antonio_map._repr_html_()

    return render_template('map.html', map_html=map_html)

if __name__ == '__main__':
    app.run(debug=True)