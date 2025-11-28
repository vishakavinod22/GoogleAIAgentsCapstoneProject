"""
Weighted Midpoint Calculator Tool
Calculates the fair midpoints points with weighted travel-time consideration based on the mode of travel to reach from location
"""
import math
from typing import Dict, Tuple

class MidpointTool:
    """Tool that calculates the fair midpoints based on modes of transport"""

    TRAVEL_WEIGHTS = {
        'walking': 1.0, # Slowest - pull midpoint closer to this
        'bicycling': 0.8,
        'transit': 0.7,
        'driving': 0.5 # Fastest
    }

    def __init__(self):
        """Initialize the midpoint calculator"""
        self.default_mode = 'transit'

    def calculate_simple_midpoint(self, coord1: Dict[str, float], coord2: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate the simple geographic midpoint (no weights)
        :param coord1: Coordinates of location 1 {'lat': float, 'lng': float}
        :param coord2: Coordinates of location 2 {'lat': float, 'lng': float}
        :return: Coordinates of the midpoint {'lat': float, 'lng': float}
        """
        mid_lat = (coord1['lat'] + coord2['lat']) / 2
        mid_lng = (coord1['lng'] + coord2['lng']) / 2

        return {
            'lat': mid_lat,
            'lng': mid_lng,
            'method': 'simple_geographic'
        }

    def calculate_weighted_midpoint(self, coord1: Dict[str, float], coord2: Dict[str, float], mode1: str = 'transit', mode2: str = 'transit') -> Dict[str, float]:
        """
        Calculate the weighted geographic midpoint based on travel modes
        :param coord1: Coordinates of location 1 {'lat': float, 'lng': float}
        :param coord2: Coordinates of location 2 {'lat': float, 'lng': float}
        :param mode1: Mode of transport for person 1 (walking/transit/driving/bicycling)
        :param mode2: Mode of transport for person 2 (walking/transit/driving/bicycling)
        :return: Coordinates of the weighted midpoint with fairness information
        """

        # Get weights (default to transit if mode not recognized)
        weight1 = self.TRAVEL_WEIGHTS.get(mode1.lower(), self.TRAVEL_WEIGHTS['transit'])
        weight2 = self.TRAVEL_WEIGHTS.get(mode2.lower(), self.TRAVEL_WEIGHTS['transit'])

        total_weight = weight1 + weight2

        weighted_lat = (coord1['lat'] * weight1 + coord2['lat'] * weight2) / total_weight
        weighted_lng = (coord1['lng'] * weight1 + coord2['lng'] * weight2) / total_weight

        simple_mid = self.calculate_simple_midpoint(coord1, coord2)
        adjustment = self._calculate_distance(simple_mid['lat'], simple_mid['lng'], weighted_lat, weighted_lng)

        return {
            'lat': weighted_lat,
            'lng': weighted_lng,
            'method': 'weighted_by_travel_mode',
            'mode1': mode1,
            'mode2': mode2,
            'weight1': weight1,
            'weight2': weight2,
            'adjustment_km': round(adjustment, 2)
        }

    def find_time_fair_midpoint(
            self,
            coord1: Dict[str, float],
            coord2: Dict[str, float],
            mode1: str = 'transit',
            mode2: str = 'transit',
            distance_matrix_tool=None
    ) -> Dict[str, float]:
        """
        Find midpoint where TRAVEL TIMES are most equal (not just distance)

        This is the SECRET WEAPON feature - calculates actual travel times
        to find the fairest meeting point.

        :param coord1: First location coordinates
        :param coord2: Second location coordinates
        :param mode1: Travel mode for person 1 (walking/transit/driving/bicycling)
        :param mode2: Travel mode for person 2
        :param distance_matrix_tool: DistanceMatrixTool instance for calculating travel times
        :return: Midpoint coordinates with travel time information
        """

        if distance_matrix_tool is None:
            # Fall back to weighted geographic midpoint
            print("   ⚠️  No DistanceMatrixTool provided, using geographic weighting")
            return self.calculate_weighted_midpoint(coord1, coord2, mode1, mode2)

        # Generate candidate points along the line between the two locations
        num_candidates = 7
        candidates = []

        for i in range(num_candidates):
            ratio = i / (num_candidates - 1)  # Creates ratios from 0.0 to 1.0
            candidate_lat = coord1['lat'] + (coord2['lat'] - coord1['lat']) * ratio
            candidate_lng = coord1['lng'] + (coord2['lng'] - coord1['lng']) * ratio
            candidates.append({'lat': candidate_lat, 'lng': candidate_lng})

        print(f"   🔍 Testing {num_candidates} candidate midpoints for time fairness...")

        # Find candidate with most equal travel times
        best_candidate = None
        best_fairness = 0
        best_comparison = None

        for candidate in candidates:
            # Get actual travel times from both people to this candidate point
            comparison = distance_matrix_tool.compare_travel_times(
                coord1, coord2, candidate,
                mode1, mode2
            )

            if comparison['success']:
                fairness = comparison['fairness_ratio']

                # Keep track of the most fair option
                if fairness > best_fairness:
                    best_fairness = fairness
                    best_candidate = candidate
                    best_comparison = comparison

        if best_candidate is None:
            print("   ⚠️  Could not calculate time-based fairness, using geographic midpoint")
            return self.calculate_weighted_midpoint(coord1, coord2, mode1, mode2)

        print(f"   ✅ Found time-fair midpoint (fairness: {best_fairness})")

        return {
            'lat': best_candidate['lat'],
            'lng': best_candidate['lng'],
            'method': 'time_based_fairness',
            'mode1': mode1,
            'mode2': mode2,
            'travel_time_person1': best_comparison['person1']['duration_text'],
            'travel_time_person2': best_comparison['person2']['duration_text'],
            'time_difference_minutes': best_comparison['time_difference_minutes'],
            'fairness_ratio': best_fairness
        }


    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """
        Calculate the distance between two points using Haversine formula
        :param lat1: Latitude of simple midpoint
        :param lng1: Longitude of simple midpoint
        :param lat2: Latitude of weighted midpoint
        :param lng2: Longitude of weighted midpoint
        :return: Distance is kilometers (km)
        """

        # Earths radius in kilometers
        R = 6371.0

        # Convert coordinates to radius
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)

        # Delta latitude and longitude - How far north/south are the points from each other
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)

        # Haversine formula: a -> angular distance, c -> central angle
        a = (
            math.sin(dlat / 2) ** 2 +
            math.cos(lat1_rad) * math.cos(lat2_rad) *
            math.sin(dlng / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        distance = R * c
        return distance

    def calculate_distance_from_midpoint(self, coord1: Dict[str, float], coord2: Dict[str, float], midpoint: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate how far each person is from the midpoint
        :param coord1: Coordinates of location 1
        :param coord2: Coordinates of location 2
        :param midpoint: Coordinates of midpoint
        :return: {'distance1_km': float, 'distance2_km': float, 'fairness_ratio': float}
        """

        dist1 = self._calculate_distance(coord1['lat'], coord1['lng'], midpoint['lat'], midpoint['lng'])
        dist2 = self._calculate_distance(coord2['lat'], coord2['lng'], midpoint['lat'], midpoint['lng'])

        # Fairness ratio: closer to 1.0 is more fair so that both people travel similar distance
        if dist1 > 0 and dist2 > 0:
            fairness = min(dist1, dist2) / max(dist1, dist2)
        else:
            fairness = 1.0

        return {
            'distance1_km': round(dist1, 2),
            'distance2_km': round(dist2, 2),
            'fairness_ratio': round(fairness, 2)
        }


# Test the tool
if __name__ == "__main__":
    print("🧪 Testing Midpoint Calculator Tool...")
    print("=" * 50)

    # Create agent
    tool = MidpointTool()

    # Test coordinates (CN Tower and Yorkdale Mall)
    coord1 = {'lat': 43.6426, 'lng': -79.3871}  # CN Tower
    coord2 = {'lat': 43.7253, 'lng': -79.4513}  # Yorkdale Mall

    print("\n📍 Location 1: CN Tower (43.6426, -79.3871)")
    print("📍 Location 2: Yorkdale Mall (43.7253, -79.4513)")

    # Test simple midpoint
    print("\n--- Simple Geographic Midpoint ---")
    simple = tool.calculate_simple_midpoint(coord1, coord2)
    print(f"Midpoint: ({simple['lat']:.4f}, {simple['lng']:.4f})")

    distances = tool.calculate_distance_from_midpoint(coord1, coord2, simple)
    print(f"Person 1 travels: {distances['distance1_km']} km")
    print(f"Person 2 travels: {distances['distance2_km']} km")
    print(f"Fairness ratio: {distances['fairness_ratio']}")

    # Test weighted midpoint
    print("\n--- Weighted Midpoint (Person 1 walking, Person 2 driving) ---")
    weighted = tool.calculate_weighted_midpoint(
        coord1, coord2,
        mode1='walking',
        mode2='driving'
    )
    print(f"Midpoint: ({weighted['lat']:.4f}, {weighted['lng']:.4f})")
    print(f"Adjustment from simple midpoint: {weighted['adjustment_km']} km")

    distances_weighted = tool.calculate_distance_from_midpoint(coord1, coord2, weighted)
    print(f"Person 1 travels: {distances_weighted['distance1_km']} km")
    print(f"Person 2 travels: {distances_weighted['distance2_km']} km")
    print(f"Fairness ratio: {distances_weighted['fairness_ratio']}")

    print("\n✅ Midpoint Calculator working!")