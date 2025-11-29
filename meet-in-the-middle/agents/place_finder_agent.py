"""
Place Finder Agent
AI-powered agent that understands user preferences and finds suitable meeting places
"""
from google import genai
from google.genai import types
from typing import Dict, List


class PlaceFinderAgent:
    """Agent that intelligently finds and recommends meeting places"""

    def __init__(self, api_key: str, places_tool):
        """Initialize agent with Gemini and Places tool"""
        self.client = genai.Client(api_key=api_key)
        self.model_id = 'gemini-2.5-flash'
        self.places_tool = places_tool

    def understand_preference(self, user_input: str) -> Dict:
        """
        Use AI to understand what type of place the user wants

        :param user_input: User's description (e.g., "quiet cafe", "good restaurant")
        :return: Dictionary with interpreted preferences
        """

        prompt = f"""You are a meeting place recommendation assistant.

            Analyze this user request and return ONLY a JSON object with:
            - "place_type": one of [cafe, restaurant, park, bar, library]
            - "keywords": list of 2-3 keywords describing preferences
            - "priority": what matters most (options: quiet, popular, cheap, quality)
            
            User request: {user_input}
            
            Return ONLY valid JSON, no markdown, no extra text.
        """

        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
            )
        )

        result_text = response.text

        return {
            'raw_input': user_input,
            'ai_interpretation': result_text,
            'agent_name': 'PlaceFinderAgent'
        }

    def find_places(
            self,
            midpoint: Dict[str, float],
            preference: str = "cafe",
            radius: int = 2000
    ) -> Dict:
        """
        Find suitable meeting places near the midpoint

        :param midpoint: {'lat': float, 'lng': float}
        :param preference: Type of place or description
        :param radius: Search radius in meters
        :return: Dict with found places and AI analysis
        """

        # Understand user preference with AI
        print(f"   🤖 Agent analyzing preference: '{preference}'...")
        interpretation = self.understand_preference(preference)

        # Search for places using the tool
        print(f"   🔍 Searching for places...")
        search_result = self.places_tool.search_nearby(
            location=midpoint,
            place_type=preference.lower(),
            radius=radius,
            max_results=10
        )

        if not search_result['success']:
            return {
                'success': False,
                'error': search_result['error']
            }

        # Return results with AI interpretation
        return {
            'success': True,
            'preference_analysis': interpretation,
            'places': search_result['results'],
            'total_found': search_result['total_found'],
            'search_params': {
                'midpoint': midpoint,
                'place_type': preference,
                'radius_km': radius / 1000
            }
        }


# Test the agent
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    from tools.places_tool import PlacesTool

    print("🧪 Testing Place Finder Agent...")
    print("=" * 50)

    # Load API keys
    load_dotenv()
    gemini_key = os.getenv('GEMINI_API_KEY')
    maps_key = os.getenv('GOOGLE_MAPS_API_KEY')

    if not gemini_key or not maps_key:
        print("❌ API keys not found")
        exit(1)

    # Initialize tool and agent
    places_tool = PlacesTool(maps_key)
    agent = PlaceFinderAgent(gemini_key, places_tool)

    # Test location
    test_midpoint = {'lat': 43.6840, 'lng': -79.4192}

    print(f"\n📍 Midpoint: ({test_midpoint['lat']}, {test_midpoint['lng']})")
    print("🔍 User wants: 'quiet cafe for studying'\n")

    # Find places
    result = agent.find_places(
        midpoint=test_midpoint,
        preference="cafe",
        radius=2000
    )

    if result['success']:
        print(f"\n✅ Found {result['total_found']} places:")
        print(f"🤖 AI Analysis: {result['preference_analysis']['ai_interpretation']}\n")

        for i, place in enumerate(result['places'][:5], 1):
            print(f"{i}. {place['name']}")
            print(f"   📍 {place['address']}")
            print(f"   ⭐ {place['rating']} ({place['user_ratings_total']} reviews)")
            print()
    else:
        print(f"❌ Failed: {result['error']}")