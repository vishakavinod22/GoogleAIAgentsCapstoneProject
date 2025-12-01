"""
Location understanding agent.
Agent that understand location and checks for validity based on user input.
It handles parsing and validating user location inputs.
"""
from google import genai
from google.genai import types


class LocationAgent:
    """
    Agent that understands and validates location inputs

    This agent uses Gemini AI to:
    - Parse natural language location descriptions
    - Validate that locations are real places
    - Extract structured data (address, city) from user input

    """

    def __init__(self, api_key: str):
        """Initialize agent with gemini client"""
        self.client = genai.Client(api_key=api_key)
        self.model_id = 'gemini-2.5-flash'

    def location_validator(self, user_input: str) -> dict:
        """
        Parse user's location input using Gemini
        :param user_input: Location string (example: "CN Tower, Toronto" or "123 Queen St West, Toronto")
        :return: Dictionary (dict) with parsed location data
        """

        prompt = f"""
            You are a location parsing agent assistant.
            
            Analyze this location input and return ONLY a JSON object of the following structure:
            - "address": the full address or landmark name
            - "city": the city name
            - "state": the state or province name
            - "country": the country name
            - "is_valid": true if user input is a real location, otherwise false
            
            Location: {user_input}
            
            Return ONLY a valid JSON, no markdown and no extra text.
        """

        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1 # Low temperature for structured output
            )
        )

        # Extract response
        result_text = response.text

        return {
            'raw_input': user_input,
            'parsed_json': result_text,
            'agent_name': 'LocationAgent',
            'model_used': self.model_id
        }

# Testing the agent
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    print("🧪 Testing Location Agent...")
    print("=" * 50)

    # Load API key
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')

    # Create agent
    agent = LocationAgent(api_key)

    # Test cases
    test_locations = [
        "CN Tower, Toronto",
        "Union Station",
        "123 Main Street, Toronto, ON",
        "15 Ellerslie Ave, North York"
    ]

    for loc in test_locations:
        print(f"\n📍 Input: {loc}")
        result = agent.location_validator(loc)
        print(f"✅ Result: {result['parsed_json']}")
        print(f"🤖 Agent: {result['agent_name']}")