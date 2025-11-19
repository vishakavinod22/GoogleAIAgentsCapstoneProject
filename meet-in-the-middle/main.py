"""
Meet in the Middle - Main Application
Multi-Agent System for Fair Meeting Locations

Following Google ADK patterns from 5-Day Course
"""
import os
from dotenv import load_dotenv
from google import genai
from agents.location_agent import LocationAgent
from tools.geocoding_tool import GeocodingTool


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

    # Get user input
    print("Please enter two locations to find a fair meeting point:")
    location_1 = input("📍 Location 1: ").strip()
    location_2 = input("📍 Location 2: ").strip()

    if not location_1 or not location_2:
        print("Both locations are required!")
        return

    # STEP 1: Validate with Location Agent
    print("\nSTEP 1: Understanding your locations...")
    print("-" * 60)

    result_1 = location_agent.location_validator(location_1)
    result_2 = location_agent.location_validator(location_2)

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


if __name__ == "__main__":
    main()