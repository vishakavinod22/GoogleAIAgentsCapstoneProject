"""
Meet in the Middle - Main Application
Multi-Agent System for Fair Meeting Locations

Following Google ADK patterns from 5-Day Course
"""
import os
from dotenv import load_dotenv
from agents.location_agent import LocationAgent
from tools.geocoding_tool import GeocodingTool
from  tools.midpoint_tools import MidpointTool


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

    # Initialize agents
    print("🤖 Initializing AI agents...")
    location_agent = LocationAgent(gemini_key)
    print("LocationAgent ready\n")

    # Initialize tools
    print("🤖 Initializing AI tools...")
    geocoder = GeocodingTool(maps_key)
    print("GeocodingTool ready\n")
    midpoint_tool = MidpointTool()
    print("MidpointAgent ready\n")

    # Get user input
    print("Please enter two locations to find a fair meeting point:")
    location_1 = input("📍 Location 1: ").strip()
    mode_1 = input("🚶 Travel mode for Location 1 (walking/transit/driving/bicycling): ").strip().lower() or 'transit'
    location_2 = input("📍 Location 2: ").strip()
    mode_2 = input("🚶 Travel mode for Location 2 (walking/transit/driving/bicycling): ").strip().lower() or 'transit'

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
        return

    print(f"\n✅ Location 1:")
    print(f"   Address: {coords_1['formatted_address']}")
    print(f"   Coordinates: ({coords_1['lat']}, {coords_1['lng']})")

    print(f"\n✅ Location 2:")
    print(f"   Address: {coords_2['formatted_address']}")
    print(f"   Coordinates: ({coords_2['lat']}, {coords_2['lng']})")

    # STEP 2: Calculate Weighted Midpoint
    print("\nSTEP 3: Calculating Midpoint...")
    print("-" * 60)

    midpoint = midpoint_tool.calculate_weighted_midpoint(
        {'lat': coords_1['lat'], 'lng': coords_1['lng']},
        {'lat': coords_2['lat'], 'lng': coords_2['lng']},
        mode1=mode_1,
        mode2=mode_2
    )

    print(f"\n🎯 Fair Meeting Point Found!")
    print(f"   Coordinates: ({midpoint['lat']:.6f}, {midpoint['lng']:.6f})")
    print(f"   Method: {midpoint['method']}")
    print(f"   Person 1 mode: {midpoint['mode1']} (weight: {midpoint['weight1']})")
    print(f"   Person 2 mode: {midpoint['mode2']} (weight: {midpoint['weight2']})")
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
    print(f"   Fairness ratio: {distances['fairness_ratio']} (1.0 = perfectly equal)")

    print(f"\n🗺️  View on Google Maps:")
    print(f"   https://www.google.com/maps?q={midpoint['lat']},{midpoint['lng']}")



if __name__ == "__main__":
    main()

