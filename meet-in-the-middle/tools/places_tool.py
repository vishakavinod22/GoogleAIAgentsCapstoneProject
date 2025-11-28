"""
Places Search Tool
Find nearby places using the Google Places API - implementation for finding meeting spots
"""
import requests
from typing import List, Dict, Optional

class PlacesTool:
    """Tool for searching nearby places (cafe's, restaurants, etc.)"""

    PLACE_TYPES = {
        'cafe': 'cafe',
        'restaurant': 'restaurant',
        'park': 'park',
        'bar': 'bar',
        'library': 'library',
        'mall': 'mall',
        'beach': 'beach'
    }

    def __init__(self, api_key: str):
        """Initialize with Google Maps API Key"""
        self.api_key = api_key
        self.base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        self.details_url = "https://maps.googleapis.com/maps/api/place/details/json"

    def search_nearby(self, location: Dict[str, float], place_type: str = 'cafe', radius: int = 2000, max_results: int = 10) -> Dict:
        """
        Search for places near a location

        :param location: Center point coordinates {'lat': float, 'lng': float}
        :param place_type: Type of place like cafe, restaurant, etc.
        :param radius: Search radius in meters (2000m = 2km)
        :param max_results: Maximum number of results to return
        :return: List of place dictionaries with details of the place
        """
        if place_type.lower() not in self.PLACE_TYPES:
            place_type = 'cafe'

        params = {
            'location': f"{location['lat']}, {location['lng']}",
            'radius': radius,
            'type': self.PLACE_TYPES[place_type.lower()],
            'key': self.api_key
        }

        try:
            # Call the Google Places API
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()

            data = response.json()

            if data['status'] != 'OK':
                return {
                    'success': False,
                    'error': f"Places search failed: {data['status']}",
                    'results': []
                }

            # Parse results
            places = []
            for place in data['results'][:max_results]:
                place_info = {
                    'name': place.get('name', 'Unknown'),
                    'address': place.get('vicinity', 'Address not available'),
                    'lat': place['geometry']['location']['lat'],
                    'lng': place['geometry']['location']['lng'],
                    'rating': place.get('rating', 'No rating'),
                    'user_ratings_total': place.get('user_ratings_total', 0),
                    'place_id': place.get('place_id', ''),
                    'types': place.get('types', []),
                    'price_level': place.get('price_level', 'Unknown'),
                    'open_now': place.get('opening_hours', {}).get('open_now', None)
                }
                places.append(place_info)

            return {
                'success': True,
                'place_type': place_type,
                'search_location': location,
                'radius_meters': radius,
                'results': places,
                'total_found': len(places)
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f"API request failed: {str(e)}",
                'results': []
            }

    def search_multiple_types(self, location: Dict[str, float], place_types: List[str], radius: int = 2000) -> Dict[str, List[Dict]]:
        """
        Search for multiple types of places at once

        :param location: Center point coordinates {'lat': float, 'lng': float}
        :param place_types: List of place like cafe, restaurant, etc.
        :param radius: Search radius in meters (2000m = 2km)
        :return: Dictionary with results grouped by places
        """
        results = {}

        for place_type in place_types:
            search_result = self.search_nearby(
                location=location,
                place_type=place_type,
                radius=radius,
                max_results=5
            )

            if search_result['success']:
                results[place_type] = search_result['results']
            else:
                results[place_type] = []

        return results


# Test the tool
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    print("Testing Places Search Tool...")
    print("=" * 50)

    # Load API key
    load_dotenv()
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')

    if not api_key:
        print("❌ GOOGLE_MAPS_API_KEY not found in .env")
        exit(1)

    # Create tool
    places_tool = PlacesTool(api_key)

    # Test location (midpoint between CN Tower and Yorkdale)
    test_location = {'lat': 43.6840, 'lng': -79.4192}

    print(f"\n📍 Searching near: ({test_location['lat']}, {test_location['lng']})")
    print("🔍 Looking for cafes within 2km...\n")

    # Search for cafes
    result = places_tool.search_nearby(
        location=test_location,
        place_type='cafe',
        radius=2000,
        max_results=5
    )

    if result['success']:
        print(f"✅ Found {result['total_found']} cafes:\n")
        for i, place in enumerate(result['results'], 1):
            print(f"{i}. {place['name']}")
            print(f"   📍 {place['address']}")
            print(f"   ⭐ Rating: {place['rating']} ({place['user_ratings_total']} reviews)")
            print(f"   💰 Price: {place['price_level']}")
            print(f"   🕐 Open now: {place['open_now']}")
            print()
    else:
        print(f"❌ Search failed: {result['error']}")