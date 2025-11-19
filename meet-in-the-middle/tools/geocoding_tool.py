"""
Geocoding tool
Converts addresses and landmarks to GPS coordinates using the Google Maps API
"""
import requests
from typing import Optional, Dict

from test_setup import response


class GeocodingTool:
    """Tool to convert location names to coordinates like latitude and longitude"""

    def __init__(self, api_key: str):
        """Initialize tool with Google Maps API key"""
        self.api_key = api_key
        self.base_url = "https://maps.googleapis.com/maps/api/geocode/json"

    def geocode(self, address: str) -> Optional[Dict]:
        """
        Convert an address into GPS coordinates
        :params address: Location string (example: "CN Tower, Toronto" or "123 Queen St West, Toronto")
        :return: Dictionary (dict) with lat, lng, formatted_address, or None if failed
        """

        params = {
            'address': address,
            'key': self.api_key
        }

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()

            data = response.json()

            if data['status'] == 'OK' and data['results']:
                result = data['results'][0]
                location = result['geometry']['location']

                return {
                    'lat': location['lat'],
                    'lng': location['lng'],
                    'formatted_address': result['formatted_address'],
                    'success': True
                }
            else:
                return {
                    'success': False,
                    'error': f"Geocoding failed: {data['status']}"
                }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f"API request failed: {str(e)}"
            }

    def batch_geocode(self, addresses: list) -> list:
        """
        Geocode multiple addresses
        :params addresses: List of location strings
        :return: List of geocoding results
        """

        results = []
        for address in addresses:
            result = self.geocode(address)
            results.append(result)

        return results


# Test the tool
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    print("Testing Geocoding Tool...")
    print("=" * 50)

    # Load API key
    load_dotenv()
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')

    if not api_key:
        print("❌ GOOGLE_MAPS_API_KEY not found in .env")
        exit(1)

    # Create tool
    geocoder = GeocodingTool(api_key)

    # Test locations
    test_locations = [
        "CN Tower, Toronto",
        "Union Station, Toronto",
        "Yorkdale Mall, Toronto",
        "123 Main Street, Toronto, ON",
        "15 Ellerslie Ave, North York"
    ]

    for location in test_locations:
        print(f"\n📍 Geocoding: {location}")
        result = geocoder.geocode(location)

        if result['success']:
            print(f"✅ Coordinates: ({result['lat']}, {result['lng']})")
            print(f"📝 Full Address: {result['formatted_address']}")
        else:
            print(f"❌ Error: {result['error']}")