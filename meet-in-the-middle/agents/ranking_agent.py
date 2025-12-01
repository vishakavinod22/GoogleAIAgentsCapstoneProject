"""
Ranking Agent
AI-powered agent that intelligently ranks meeting places based on multiple factors
"""
from google import genai
from google.genai import types
from typing import Dict, List
import json


class RankingAgent:
    """
    Agent that ranks places using AI reasoning and multiple criteria

    This is the core intelligence of the system. It combines:
    1. Travel time fairness (are both people traveling similar times?)
    2. Distance fairness (geographic equity)
    3. Place quality (ratings, reviews)
    4. Practical factors (open now, price level)
    5. User preferences from memory

    The AI weighs all factors and provides human-readable reasoning
    for each ranking decision.
    """

    def __init__(self, api_key: str, distance_matrix_tool=None):
        """
        Initialize with Gemini and optional distance matrix tool

        :param api_key: Gemini API key
        :param distance_matrix_tool: DistanceMatrixTool for calculating travel fairness
        """
        self.client = genai.Client(api_key=api_key)
        self.model_id = 'gemini-2.5-flash'
        self.distance_matrix_tool = distance_matrix_tool

    def rank_places(
            self,
            places: List[Dict],
            person1_location: Dict[str, float],
            person2_location: Dict[str, float],
            mode1: str = 'transit',
            mode2: str = 'transit',
            preferences: Dict = None
    ) -> List[Dict]:
        """
        Rank places using AI and travel time analysis

        :param places: List of place dictionaries from PlaceFinderAgent
        :param person1_location: Person 1's starting coordinates
        :param person2_location: Person 2's starting coordinates
        :param mode1: Person 1's travel mode
        :param mode2: Person 2's travel mode
        :param preferences: Optional user preferences (e.g., {'priority': 'quiet'})

        :return: Ranked list of places with scores and reasoning
        """

        if not places:
            return []

        print(f"   🤖 Ranking {len(places)} places with AI...")

        # Step 1: Calculate travel fairness for each place
        places_with_travel = []

        for place in places:
            place_location = {'lat': place['lat'], 'lng': place['lng']}

            # Get travel times if distance matrix tool available
            travel_info = None
            if self.distance_matrix_tool:
                travel_info = self.distance_matrix_tool.compare_travel_times(
                    person1_location,
                    person2_location,
                    place_location,
                    mode1,
                    mode2
                )

            # Add travel info to place
            place_copy = place.copy()
            if travel_info and travel_info['success']:
                place_copy['travel_fairness'] = travel_info['fairness_ratio']
                place_copy['time_person1'] = travel_info['person1']['duration_text']
                place_copy['time_person2'] = travel_info['person2']['duration_text']
                place_copy['time_difference_min'] = travel_info['time_difference_minutes']
            else:
                place_copy['travel_fairness'] = None

            places_with_travel.append(place_copy)

        # Step 2: Use AI to rank places
        ranked_places = self._rank_with_ai(places_with_travel, preferences)

        return ranked_places

    def _rank_with_ai(self, places: List[Dict], preferences: Dict = None) -> List[Dict]:
        """
        Use Gemini to intelligently rank places

        :param places: Places with travel info added
        :param preferences: User preferences

        :return: Ranked places with AI scores
        """

        # Prepare place summaries for AI
        place_summaries = []
        for i, place in enumerate(places):
            summary = {
                'index': i,
                'name': place['name'],
                'rating': place['rating'],
                'reviews': place['user_ratings_total'],
                'open_now': place['open_now'],
                'price_level': place['price_level'],
                'travel_fairness': place.get('travel_fairness', 'unknown'),
                'time_person1': place.get('time_person1', 'unknown'),
                'time_person2': place.get('time_person2', 'unknown')
            }
            place_summaries.append(summary)

        # Build AI prompt
        preferences_text = ""
        if preferences:
            preferences_text = f"\nUser preferences: {preferences}"

        prompt = f"""You are a meeting place recommendation expert. Rank these places from best to worst for a meetup.

            Consider these factors in order of importance:
            1. Travel fairness (fairness_ratio closer to 1.0 = more fair for both people)
            2. Quality (rating and number of reviews - balance popular vs good)
            3. Currently open (open_now = true is better)
            4. Price level (moderate is usually best)
            {preferences_text}
            
            Places to rank:
            {json.dumps(place_summaries, indent=2)}
            
            Return ONLY a JSON array of indices in ranked order (best first), like: [2, 0, 5, 1, 3, 4]
            Include a brief reason for each ranking.
            
            Format:
            {{
              "ranked_indices": [2, 0, 5, 1, 3, 4],
              "reasoning": {{
                "2": "Best travel fairness (0.85) and excellent rating (4.7 with 200+ reviews)",
                "0": "Good rating but less fair travel times",
                ...
              }}
            }}
            
            Return ONLY valid JSON, no markdown, no extra text.
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                )
            )

            result_text = response.text.strip()

            # Parse AI response
            # Remove markdown code blocks if present
            if result_text.startswith('```'):
                result_text = result_text.split('```')[1]
                if result_text.startswith('json'):
                    result_text = result_text[4:]

            ranking_data = json.loads(result_text)
            ranked_indices = ranking_data.get('ranked_indices', [])
            reasoning = ranking_data.get('reasoning', {})

            # Build ranked list
            ranked_places = []
            for rank, idx in enumerate(ranked_indices, 1):
                if idx < len(places):
                    place = places[idx].copy()
                    place['rank'] = rank
                    place['ai_reasoning'] = reasoning.get(str(idx), 'No reasoning provided')
                    ranked_places.append(place)

            return ranked_places

        except Exception as e:
            print(f"   ⚠️ AI ranking failed: {e}")
            print("   Using fallback scoring...")

            # Fallback: Simple scoring if AI fails
            return self._fallback_ranking(places)

    def _fallback_ranking(self, places: List[Dict]) -> List[Dict]:
        """
        Simple fallback ranking if AI fails

        :param places: Places to rank

        :return: Ranked places using simple scoring
        """

        scored_places = []

        for place in places:
            score = 0

            # Rating score (0-50 points)
            if isinstance(place['rating'], (int, float)):
                score += place['rating'] * 10

            # Reviews score (0-25 points, capped)
            reviews = place['user_ratings_total']
            score += min(reviews / 10, 25)

            # Travel fairness (0-25 points)
            if place.get('travel_fairness'):
                score += place['travel_fairness'] * 25

            # Open now bonus (10 points)
            if place.get('open_now') is True:
                score += 10

            place_copy = place.copy()
            place_copy['score'] = round(score, 2)
            scored_places.append(place_copy)

        # Sort by score
        ranked = sorted(scored_places, key=lambda x: x['score'], reverse=True)

        # Add rank
        for i, place in enumerate(ranked, 1):
            place['rank'] = i
            place['ai_reasoning'] = f"Score: {place['score']} (fallback ranking)"

        return ranked


# Test the agent
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    from tools.distance_matrix_tool import DistanceMatrixTool

    print("🧪 Testing Ranking Agent...")
    print("=" * 50)

    # Load API keys
    load_dotenv()
    gemini_key = os.getenv('GEMINI_API_KEY')
    maps_key = os.getenv('GOOGLE_MAPS_API_KEY')

    if not gemini_key or not maps_key:
        print("❌ API keys not found")
        exit(1)

    # Initialize
    distance_matrix = DistanceMatrixTool(maps_key)
    ranking_agent = RankingAgent(gemini_key, distance_matrix)

    # Test data (sample places)
    test_places = [
        {
            'name': 'Starbucks Reserve',
            'address': '123 Main St',
            'lat': 43.6700,
            'lng': -79.4000,
            'rating': 4.5,
            'user_ratings_total': 320,
            'open_now': True,
            'price_level': 2
        },
        {
            'name': 'Local Coffee Shop',
            'address': '456 Queen St',
            'lat': 43.6750,
            'lng': -79.4100,
            'rating': 4.8,
            'user_ratings_total': 45,
            'open_now': True,
            'price_level': 1
        },
        {
            'name': 'Tim Hortons',
            'address': '789 King St',
            'lat': 43.6800,
            'lng': -79.4050,
            'rating': 3.9,
            'user_ratings_total': 850,
            'open_now': False,
            'price_level': 1
        }
    ]

    # Test locations (CN Tower and Yorkdale)
    person1 = {'lat': 43.6426, 'lng': -79.3871}
    person2 = {'lat': 43.7253, 'lng': -79.4513}

    print("\n📍 Ranking places for meeting between:")
    print(f"   Person 1: CN Tower (walking)")
    print(f"   Person 2: Yorkdale (driving)\n")

    # Rank places
    ranked = ranking_agent.rank_places(
        places=test_places,
        person1_location=person1,
        person2_location=person2,
        mode1='walking',
        mode2='driving'
    )

    print(f"\n✅ Ranked {len(ranked)} places:\n")

    for place in ranked[:3]:
        print(f"{place['rank']}. {place['name']} ⭐ {place['rating']}")
        print(f"   AI Reasoning: {place.get('ai_reasoning', 'N/A')}")
        if 'travel_fairness' in place and place['travel_fairness']:
            print(f"   Travel fairness: {place['travel_fairness']}")
            print(f"   Times: {place.get('time_person1', 'N/A')} / {place.get('time_person2', 'N/A')}")
        print()