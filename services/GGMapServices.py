import requests

def download_satellite_image(lat, lon, api_key, zoom=20, size="640x640", filename="image.png"):
    """
    Downloads a satellite image from Google Static Maps API for the specified coordinates
    and saves it to a local file. A red marker is added at the given latitude and longitude.

    Args:
        lat (float): Latitude of the location.
        lon (float): Longitude of the location.
        api_key (str): Your Google Maps API key.
        zoom (int, optional): Zoom level of the map (default is 20).
        size (str, optional): Image size in format "widthxheight" (default is "640x640").
        filename (str, optional): The name of the file to save the image to (default is "image.png").

    Returns:
        None. The image is saved to the local file system if the request is successful.

    Prints:
        - ✅ A success message including the filename and coordinates.
        - ❌ An error message if the image could not be downloaded.
    """
    marker = f"color:red|label:X|{lat},{lon}" 
    url = (
        f"https://maps.googleapis.com/maps/api/staticmap?"
        f"center={lat},{lon}&zoom={zoom}&size={size}&maptype=satellite"
        f"&markers={marker}&key={api_key}"
    )
    
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"✅ Saved to {filename} with marker at ({lat}, {lon})")
    else:
        print(f"❌ Failed to download image. Status code: {response.status_code}")

def search_places_in_area(keyword, location, radius, api_key):
    """
    Searches for places near a specific location using a keyword and radius via the Google Places API.

    Args:
        keyword (str): Search term to filter places (e.g., 'factory', 'solar panel').
        location (str): Latitude and longitude of the center point in the format "lat,lon".
        radius (int): Search radius in meters.
        api_key (str): Your Google Maps API key.

    Returns:
        list: A list of dictionaries containing:
            - name (str): Name of the place.
            - address (str): Address or vicinity of the place.
            - location (dict): A dictionary with 'lat' and 'lng' keys representing coordinates.
    
    Notes:
        If the API call is successful (status == "OK"), it returns a list of matched places.
        Otherwise, returns an empty list.
    """
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": location,  
        "radius": radius,     
        "keyword": keyword,    
        "key": api_key
    }
    response = requests.get(url, params=params)
    data = response.json()

    results = []
    if data["status"] == "OK":
        for place in data["results"]:
            results.append({
                "name": place["name"],
                "address": place.get("vicinity", ""),
                "location": place["geometry"]["location"]
            })
    return results
