"""
Meet in the Middle - Main Application
Multi-Agent System for Fair Meeting Locations
"""
import os
from dotenv import load_dotenv
from agents.location_agent import LocationAgent
from agents.place_finder_agent import PlaceFinderAgent
from tools.geocoding_tool import GeocodingTool
from tools.midpoint_tools import MidpointTool
from tools.places_tool import PlacesTool
from tools.distance_matrix_tool import DistanceMatrixTool


def print_header():
    """Print welcome banner"""
    print("\n" + "=" * 60)
    print("🤝 MEET IN THE MIDDLE")
    print("AI-Powered Fair Meeting Location Finder")
    print("=" * 60 + "\n")


def main():
    """Main application flow"""

    # Setup
    load_dotenv()
    gemini_key = os.getenv('GEMINI_API_KEY')
    maps_key = os.getenv('GOOGLE_MAPS_API_KEY')

    if not gemini_key:
        print("Error: GEMINI_API_KEY not found in .env")
        return

    print_header()

    # Initialize agents and tools
    print("🤖 Initializing AI agents...")
    location_agent = LocationAgent(gemini_key)
    print("LocationAgent ready\n")

    print("🤖 Initializing AI tools...")
    geocoder = GeocodingTool(maps_key)
    print("GeocodingTool ready\n")

    midpoint_tool = MidpointTool()
    print("MidpointAgent ready\n")

    places_tool = PlacesTool(maps_key)
    print("PlacesTool ready\n")
    place_finder_agent = PlaceFinderAgent(gemini_key, places_tool)
    print("PlaceFinderAgent ready\n")
    distance_matrix = DistanceMatrixTool(maps_key)
    print("DistanceMatrixTool ready\n")

    # Get user input
    print("Please enter two locations to find a fair meeting point:")
    location_1 = input("📍 Location 1: ").strip()
    mode_1 = input("🚶 Travel mode for Location 1 (walking/transit/driving/bicycling): ").strip().lower() or 'transit'
    location_2 = input("📍 Location 2: ").strip()
    mode_2 = input("🚶 Travel mode for Location 2 (walking/transit/driving/bicycling): ").strip().lower() or 'transit'

    place_type = input("\n☕ What type of place? (cafe/restaurant/park): ").strip().lower() or 'cafe'

    if not location_1 or not location_2:
        print("Both locations are required!")
        return

    # STEP 1: Validate with Location Agent
    print("\nSTEP 1: Understanding your locations...")
    print("-" * 60)

    result_1 = location_agent.location_validator(location_1)
    result_2 = location_agent.location_validator(location_2)

    print(f"Location 1 is {result_1['parsed_json']}")
    print(f"Location 2 is {result_2['parsed_json']}")

    # STEP 2: Geocode to get coordinates
    print("\nSTEP 2: Getting GPS coordinates...")
    print("-" * 60)

    coords_1 = geocoder.geocode(location_1)
    coords_2 = geocoder.geocode(location_2)

    if not coords_1['success'] or not coords_2['success']:
        print("❌ Failed to geocode one or more locations")
        print(f"\n🔍 Debug Info:")
        print(f"Location 1 result: {coords_1}")
        print(f"Location 2 result: {coords_2}")

        return

    print(f"\n✅ Location 1:")
    print(f"   Address: {coords_1['formatted_address']}")
    print(f"   Coordinates: ({coords_1['lat']}, {coords_1['lng']})")

    print(f"\n✅ Location 2:")
    print(f"   Address: {coords_2['formatted_address']}")
    print(f"   Coordinates: ({coords_2['lat']}, {coords_2['lng']})")

    # STEP 3: Calculate Time Fair Midpoint
    print("\nSTEP 3: Calculating Midpoint...")
    print("-" * 60)

    # Use time-based fairness
    midpoint = midpoint_tool.find_time_fair_midpoint(
        {'lat': coords_1['lat'], 'lng': coords_1['lng']},
        {'lat': coords_2['lat'], 'lng': coords_2['lng']},
        mode1=mode_1,
        mode2=mode_2,
        distance_matrix_tool=distance_matrix
    )

    print(f"\n🎯 Fair Meeting Point Found!")
    print(f"   Coordinates: ({midpoint['lat']:.6f}, {midpoint['lng']:.6f})")
    print(f"   Method: {midpoint['method']}")
    # print(f"   Person 1 mode: {midpoint['mode1']} (weight: {midpoint['weight1']})")
    # print(f"   Person 2 mode: {midpoint['mode2']} (weight: {midpoint['weight2']})")
    # print(f"   Adjustment: {midpoint['adjustment_km']} km from simple midpoint")

    # Show travel times (only if time-based method was used)
    if 'travel_time_person1' in midpoint:
        print(f"\n⏱️  Travel Times:")
        print(f"   Person 1 ({mode_1}): {midpoint['travel_time_person1']}")
        print(f"   Person 2 ({mode_2}): {midpoint['travel_time_person2']}")
        print(f"   Time difference: {midpoint['time_difference_minutes']} minutes")
        print(f"   Fairness ratio: {midpoint['fairness_ratio']} (1.0 = perfectly equal)")
    else:
        # Fallback display for weighted geographic midpoint
        print(f"   Person 1 mode: {midpoint['mode1']} (weight: {midpoint.get('weight1', 'N/A')})")
        print(f"   Person 2 mode: {midpoint['mode2']} (weight: {midpoint.get('weight2', 'N/A')})")
        if 'adjustment_km' in midpoint:
            print(f"   Adjustment: {midpoint['adjustment_km']} km from simple midpoint")

    # Calculate distances
    distances = midpoint_tool.calculate_distance_from_midpoint(
        {'lat': coords_1['lat'], 'lng': coords_1['lng']},
        {'lat': coords_2['lat'], 'lng': coords_2['lng']},
        midpoint
    )

    print(f"\n📏 Travel Distances:")
    print(f"   Person 1: {distances['distance1_km']} km")
    print(f"   Person 2: {distances['distance2_km']} km")
    # print(f"   Fairness ratio: {distances['fairness_ratio']} (1.0 = perfectly equal)")

    print(f"\n🗺️  View on Google Maps:")
    print(f"   https://www.google.com/maps?q={midpoint['lat']},{midpoint['lng']}")

    # STEP 4: Find Meeting Places
    print(f"\n☕ Step 4: Finding {place_type}s near the midpoint...")
    print("-" * 60)

    places_result = place_finder_agent.find_places(
        midpoint={'lat': midpoint['lat'], 'lng': midpoint['lng']},
        preference=place_type,
        radius=2000
    )

    if places_result['success']:
        print(f"\n✅ Found {places_result['total_found']} great options!\n")

        # Show top 5 results
        for i, place in enumerate(places_result['places'][:5], 1):
            print(f"{i}. 📍 {place['name']}")
            print(f"   Address: {place['address']}")
            print(f"   Rating: ⭐ {place['rating']} ({place['user_ratings_total']} reviews)")
            print(f"   Price: {'💰' * int(place['price_level']) if isinstance(place['price_level'], int) else '💰'}")
            if place['open_now'] is not None:
                status = "🟢 Open now" if place['open_now'] else "🔴 Closed"
                print(f"   Status: {status}")
            print(f"   Map: https://www.google.com/maps?q={place['lat']},{place['lng']}")
            print()
    else:
        print(f"❌ Could not find places: {places_result['error']}")



if __name__ == "__main__":
    main()

