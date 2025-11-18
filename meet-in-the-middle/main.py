"""
Meet in the Middle - Main Application
Multi-Agent System for Fair Meeting Locations

Following Google ADK patterns from 5-Day Course
"""
import os
from dotenv import load_dotenv
from google import genai
from agents.location_agent import LocationAgent


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

    # Initialize agents (following Day 2 patterns)
    print("🤖 Initializing AI agents...")
    location_agent = LocationAgent(gemini_key)
    print("LocationAgent ready\n")

    # Get user input
    print("Please enter two locations to find a fair meeting point:")
    location_1 = input("📍 Location 1: ").strip()
    location_2 = input("📍 Location 2: ").strip()

    if not location_1 or not location_2:
        print("Both locations are required!")
        return

    # Process with Location Agent
    print("\n🔍 Understanding your locations...")
    print("-" * 60)

    result_1 = location_agent.location_validator(location_1)
    result_2 = location_agent.location_validator(location_2)

    print(f"\n✅ Location 1 Analysis:")
    print(f"   Raw Input: {result_1['raw_input']}")
    print(f"   Parsed: {result_1['parsed_json']}")

    print(f"\n✅ Location 2 Analysis:")
    print(f"   Raw Input: {result_2['raw_input']}")
    print(f"   Parsed: {result_2['parsed_json']}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()