"""
Distance Matrix Tool
Calculates actual travel times between locations using Google Distance Matrix API
"""
import requests
from typing import Dict

class DistanceMatrixTool:
    """Tool for calculating real travel times and distances"""

    def __init__(self, api_key: str):
        """Initialize with Google Maps API key"""
        self.api_key = api_key
        self.base_url = "https://maps.googleapis.com/maps/api/distancematrix/json"

    def get_travel_time(
            self,
            origin: Dict[str, float],
            destination: Dict[str, float],
            mode: str = 'transit'
    ) -> Dict:
        """
        Get travel time between two points

        :param origin: {'lat': float, 'lng': float}
        :param destination: {'lat': float, 'lng': float}
        :param mode: 'driving', 'walking', 'transit', or 'bicycling'
        :return: Dictionary with duration in seconds and formatted string
        """

        # Format coordinates
        origin_str = f"{origin['lat']},{origin['lng']}"
        dest_str = f"{destination['lat']},{destination['lng']}"

        # Build request
        params = {
            'origins': origin_str,
            'destinations': dest_str,
            'mode': mode.lower(),
            'key': self.api_key
        }

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()

            data = response.json()

            if data['status'] != 'OK':
                return {
                    'success': False,
                    'error': f"Distance Matrix failed: {data['status']}"
                }

            # Extract duration
            element = data['rows'][0]['elements'][0]

            if element['status'] != 'OK':
                return {
                    'success': False,
                    'error': f"Route not found: {element['status']}"
                }

            return {
                'success': True,
                'duration_seconds': element['duration']['value'],
                'duration_text': element['duration']['text'],
                'distance_meters': element['distance']['value'],
                'distance_text': element['distance']['text'],
                'mode': mode
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def compare_travel_times(
            self,
            origin1: Dict[str, float],
            origin2: Dict[str, float],
            destination: Dict[str, float],
            mode1: str = 'transit',
            mode2: str = 'transit'
    ) -> Dict:
        """
        Compare travel times from two origins to one destination

        :return: Dictionary with both travel times and fairness score
        """

        time1 = self.get_travel_time(origin1, destination, mode1)
        time2 = self.get_travel_time(origin2, destination, mode2)

        if not time1['success'] or not time2['success']:
            return {
                'success': False,
                'error': 'Could not calculate one or more travel times'
            }

        # Calculate fairness (closer to 1.0 = more fair)
        duration1 = time1['duration_seconds']
        duration2 = time2['duration_seconds']
        fairness = min(duration1, duration2) / max(duration1, duration2)

        # Calculate time difference
        time_diff = abs(duration1 - duration2)

        return {
            'success': True,
            'person1': {
                'duration_seconds': duration1,
                'duration_text': time1['duration_text'],
                'distance_text': time1['distance_text'],
                'mode': mode1
            },
            'person2': {
                'duration_seconds': duration2,
                'duration_text': time2['duration_text'],
                'distance_text': time2['distance_text'],
                'mode': mode2
            },
            'fairness_ratio': round(fairness, 2),
            'time_difference_seconds': time_diff,
            'time_difference_minutes': round(time_diff / 60, 1)
        }


# Test
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')

    tool = DistanceMatrixTool(api_key)

    # CN Tower
    origin1 = {'lat': 43.6426, 'lng': -79.3871}
    # Yorkdale
    origin2 = {'lat': 43.7253, 'lng': -79.4513}
    # Midpoint
    midpoint = {'lat': 43.6840, 'lng': -79.4192}

    print("🧪 Testing Distance Matrix Tool\n")

    result = tool.compare_travel_times(
        origin1, origin2, midpoint,
        mode1='walking',
        mode2='driving'
    )

    if result['success']:
        print(f"Person 1 (walking): {result['person1']['duration_text']}")
        print(f"Person 2 (driving): {result['person2']['duration_text']}")
        print(f"Time difference: {result['time_difference_minutes']} minutes")
        print(f"Fairness: {result['fairness_ratio']}")