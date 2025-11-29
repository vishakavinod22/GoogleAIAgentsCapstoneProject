"""
Refinement Helper
Handles user refinement requests, i.e, changing search without re-entering everything
"""
from typing import Dict, Optional


class RefinementHelper:
    """Helper for refining searches based on session state"""

    @staticmethod
    def show_refinement_menu() -> str:
        """
        Display refinement options

        :return: User's choice
        """
        print("\n" + "=" * 60)
        print("🔄 REFINEMENT OPTIONS")
        print("=" * 60)
        print("1. Change place type (cafe/restaurant/park/etc.)")
        print("2. Adjust search radius")
        print("3. Set preference (quiet/popular/cheap)")
        print("4. New search (different locations)")
        print("5. View learned preferences")
        print("6. Exit")
        print("-" * 60)

        choice = input("Choose an option (1-6): ").strip()
        return choice

    @staticmethod
    def get_new_place_type() -> str:
        """Get new place type from user"""
        print("\n📍 Available place types:")
        print("   cafe, restaurant, park, bar, library, mall, beach")
        new_type = input("Enter new place type: ").strip().lower()
        return new_type if new_type else 'cafe'

    @staticmethod
    def get_new_radius() -> int:
        """Get new search radius from user"""
        print("\n📏 Current radius: 2km")
        print("   Options: 1km (1000m), 2km (2000m), 5km (5000m)")
        radius_input = input("Enter radius in meters (e.g., 1000, 2000, 5000): ").strip()

        try:
            radius = int(radius_input)
            if radius < 500:
                radius = 500
            elif radius > 10000:
                radius = 10000
            return radius
        except:
            return 2000  # Default

    @staticmethod
    def get_preference() -> Dict[str, str]:
        """Get user preference"""
        print("\n💡 What matters most to you?")
        print("   1. Quiet atmosphere")
        print("   2. Popular/busy places")
        print("   3. Budget-friendly")
        print("   4. High quality")

        choice = input("Choose (1-4): ").strip()

        preference_map = {
            '1': {'priority': 'quiet', 'likes_quiet': True},
            '2': {'priority': 'popular', 'likes_popular': True},
            '3': {'priority': 'cheap', 'price_preference': 'low'},
            '4': {'priority': 'quality', 'quality_focused': True}
        }

        return preference_map.get(choice, {'priority': 'balanced'})