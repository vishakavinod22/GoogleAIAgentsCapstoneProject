"""
Meet in the Middle - Main Application
Multi-Agent System for Fair Meeting Locations
"""
import os
from dotenv import load_dotenv
from agents.location_agent import LocationAgent
from agents.place_finder_agent import PlaceFinderAgent
from agents.ranking_agent import RankingAgent
from tools.geocoding_tool import GeocodingTool
from tools.midpoint_tools import MidpointTool
from tools.places_tool import PlacesTool
from tools.distance_matrix_tool import DistanceMatrixTool
from utils.session_manager import SessionManager
from utils.refinement_helper import RefinementHelper


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

    # Initialize session manager
    session = SessionManager()
    print("Session Manager initialized")

    # Show memory summary if user has history
    if session.memory_bank['total_searches'] > 0:
        print("\n📚 Your Memory Bank:")
        print(session.get_memory_summary())

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

    ranking_agent = RankingAgent(gemini_key, distance_matrix)
    print("RankingAgent ready")

    # Main search loop
    while True:
        # Check if we can use session data
        session_summary = session.get_session_summary()

        if session_summary['has_locations']:
            print("\n🔄 Previous search found!")
            print(f"   Locations: {session_summary['location_1']} ↔ {session_summary['location_2']}")
            use_previous = input("Use previous locations? (y/n): ").strip().lower()

            if use_previous == 'y':
                # Retrieve from session
                location_1 = session.retrieve('location_1')
                location_2 = session.retrieve('location_2')
                mode_1 = session.retrieve('mode_1')
                mode_2 = session.retrieve('mode_2')
                coords_1 = session.retrieve('coords_1')
                coords_2 = session.retrieve('coords_2')

                # Ask for new place type
                place_type = RefinementHelper.get_new_place_type()

                print(f"\n✅ Using previous locations, searching for {place_type}s")

                # Skip to midpoint calculation
                goto_midpoint = True
            else:
                session.clear_session()
                goto_midpoint = False
        else:
            goto_midpoint = False

        # Get user input (if not using session)
        if not goto_midpoint:
            print("Please enter two locations to find a fair meeting point:")
            location_1 = input("📍 Location 1: ").strip()
            mode_1 = input(
                "🚶 Travel mode for Location 1 (walking/transit/driving/bicycling): ").strip().lower() or 'transit'

            location_2 = input("\n📍 Location 2: ").strip()
            mode_2 = input(
                "🚶 Travel mode for Location 2 (walking/transit/driving/bicycling): ").strip().lower() or 'transit'

            place_type = input("\n☕ What type of place? (cafe/restaurant/park/bar/library/mall/beach): ").strip().lower() or 'cafe'

            if not location_1 or not location_2:
                print("❌ Both locations are required!")
                return

            # Store in session
            session.store('location_1', location_1)
            session.store('location_2', location_2)
            session.store('mode_1', mode_1)
            session.store('mode_2', mode_2)
            session.store('place_type', place_type)

            # Record in memory bank
            session.record_location(location_1)
            session.record_location(location_2)

            # STEP 1: Validate with Location Agent
            print("\n🔍 STEP 1: Understanding your locations...")
            print("-" * 60)

            result_1 = location_agent.location_validator(location_1)
            result_2 = location_agent.location_validator(location_2)

            print(f"✅ Location 1 validated")
            print(f"✅ Location 2 validated")

            # STEP 2: Geocode to get coordinates
            print("\n📍 STEP 2: Getting GPS coordinates...")
            print("-" * 60)

            coords_1 = geocoder.geocode(location_1)
            coords_2 = geocoder.geocode(location_2)

            if not coords_1['success'] or not coords_2['success']:
                print("❌ Failed to geocode one or more locations")
                return

            print(f"✅ Location 1: {coords_1['formatted_address']}")
            print(f"✅ Location 2: {coords_2['formatted_address']}")

            # Store coords in session
            session.store('coords_1', coords_1)
            session.store('coords_2', coords_2)

        # STEP 3: Calculate Time-Fair Midpoint
        print("\n🧮 STEP 3: Calculating fair meeting point...")
        print("-" * 60)

        midpoint = midpoint_tool.find_time_fair_midpoint(
            {'lat': coords_1['lat'], 'lng': coords_1['lng']},
            {'lat': coords_2['lat'], 'lng': coords_2['lng']},
            mode1=mode_1,
            mode2=mode_2,
            distance_matrix_tool=distance_matrix
        )

        # Store midpoint in session
        session.store('midpoint', midpoint)

        print(f"\n✅ Fair meeting point found!")
        print(f"   Coordinates: ({midpoint['lat']:.6f}, {midpoint['lng']:.6f})")

        if 'travel_time_person1' in midpoint:
            print(f"\n⏱️  Travel Times:")
            print(f"   Person 1 ({mode_1}): {midpoint['travel_time_person1']}")
            print(f"   Person 2 ({mode_2}): {midpoint['travel_time_person2']}")
            print(f"   Time difference: {midpoint['time_difference_minutes']} minutes")
            print(f"   Fairness ratio: {midpoint['fairness_ratio']}")

            # STEP 4: Find Meeting Places
            print(f"\n☕ STEP 4: Finding {place_type}s near the midpoint...")
            print("-" * 60)

            places_result = place_finder_agent.find_places(
                midpoint={'lat': midpoint['lat'], 'lng': midpoint['lng']},
                preference=place_type,
                radius=session.retrieve('search_radius') or 2000
            )

            if not places_result['success']:
                print(f"❌ Could not find places: {places_result['error']}")
                break

            print(f"✅ Found {places_result['total_found']} places")

            # Store results in session
            session.store('last_results', places_result)
            session.store('place_type', place_type)

            # STEP 5: Rank the places with AI
            print(f"\n🏆 STEP 5: Ranking places with AI...")
            print("-" * 60)

            # Get user preferences from memory
            user_prefs = {
                'priority': session.get_preference('priority', 'balanced'),
                'likes_quiet': session.get_preference('likes_quiet', False),
                'price_preference': session.get_preference('price_preference', 'moderate')
            }

            ranked_places = ranking_agent.rank_places(
                places=places_result['places'],
                person1_location={'lat': coords_1['lat'], 'lng': coords_1['lng']},
                person2_location={'lat': coords_2['lat'], 'lng': coords_2['lng']},
                mode1=mode_1,
                mode2=mode_2,
                preferences=user_prefs
            )

            # Store ranked results
            session.store('last_ranked', ranked_places)
            session.record_search()

            print(f"\n✅ Top {min(5, len(ranked_places))} Recommendations:\n")

            for place in ranked_places[:5]:
                print(f"#{place['rank']}. 📍 {place['name']}")
                print(f"    Address: {place['address']}")
                print(f"    Rating: ⭐ {place['rating']} ({place['user_ratings_total']} reviews)")

                # Enhanced travel display with person labels and modes
                if 'time_person1' in place and place['time_person1'] != 'unknown':
                    print(f"    Travel Times:")
                    print(f"      • Person 1 ({mode_1}): {place['time_person1']}")
                    print(f"      • Person 2 ({mode_2}): {place['time_person2']}")
                    print(f"      • Fairness Score: {place.get('travel_fairness', 'N/A')} (1.0 = perfectly equal)")

                print(f"    💡 Why: {place.get('ai_reasoning', 'No reasoning')}")

                price_display = '💰' * int(place['price_level']) if isinstance(place['price_level'], int) else '💰'
                print(f"    Price: {price_display}")
                if place['open_now'] is not None:
                    status = "🟢 Open now" if place['open_now'] else "🔴 Closed"
                    print(f"    Status: {status}")

                # Use place name + address for map link instead of coordinates
                map_query = f"{place['name']}, {place['address']}"
                # URL encode the query
                import urllib.parse
                encoded_query = urllib.parse.quote(map_query)
                print(f"    🗺️  Map: https://www.google.com/maps/search/?api=1&query={encoded_query}")
                print()

            # Refinement menu
            print("\n" + "=" * 60)
            refine = input("Would you like to refine this search? (y/n): ").strip().lower()

            if refine == 'y':
                choice = RefinementHelper.show_refinement_menu()

                if choice == '1':
                    # Change place type
                    continue  # Loop will ask for new place type
                elif choice == '2':
                    # Change radius
                    new_radius = RefinementHelper.get_new_radius()
                    session.store('search_radius', new_radius)
                    print(f"✅ Updated search radius to {new_radius}m")
                    # Re-run search with new radius
                    continue
                elif choice == '3':
                    # Set preference
                    pref = RefinementHelper.get_preference()
                    for key, value in pref.items():
                        session.update_preference(key, value)
                    # Re-run with new preferences
                    continue
                elif choice == '4':
                    # New search
                    session.clear_session()
                    continue
                elif choice == '5':
                    # Show memory
                    print("\n" + session.get_memory_summary())
                    input("\nPress Enter to continue...")
                    continue
                else:
                    # Exit
                    break
            else:
                # Done
                break


if __name__ == "__main__":
    main()

