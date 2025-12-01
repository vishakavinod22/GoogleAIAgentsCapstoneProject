"""
Meet in the Middle - Streamlit Web Interface
"""
import streamlit as st
import os
from agents.location_agent import LocationAgent
from agents.place_finder_agent import PlaceFinderAgent
from agents.ranking_agent import RankingAgent
from tools.geocoding_tool import GeocodingTool
from tools.midpoint_tools import MidpointTool
from tools.places_tool import PlacesTool
from tools.distance_matrix_tool import DistanceMatrixTool
from PIL import Image


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(BASE_DIR, "images", "logo.png")
logo = Image.open(logo_path)

# Page config
st.set_page_config(
    page_title="Meet in the Middle",
    page_icon=logo_path,
    layout="wide"
)

# Title

col1, col2 = st.columns([1, 10])

st.image(logo, width=50)
st.title("Meet in the Middle")

st.subheader("AI-Powered Fair Meeting Location Finder")
st.markdown("Find the perfect meeting spot with time-based fairness!")

with st.expander("💡 Tips for Best Results"):
    st.markdown("""
    **Location Input Guidelines:**
    
    Be specific! 
    
    Include street address, landmark name, and city for best results!

    ✅ **Good Examples:**
    - "Yorkdale Shopping Centre, Toronto, ON"
    - "CN Tower, 301 Front Street West, Toronto"
    - "Union Station, 65 Front St W, Toronto, ON M5J 1E6"

    ❌ **Avoid:**
    - "Yorkdale" (too vague)
    - "downtown" (ambiguous)
    - "the mall" (which mall?)

    **Why it matters:** 
    Detailed locations help our AI agents accurately geocode your starting points 
    and calculate fair travel times. The more specific you are, the better your results!
    """)

st.markdown("---")

# Sidebar for API keys
st.sidebar.header("Agents Status")

# Get API keys from Streamlit secrets or sidebar
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    GOOGLE_MAPS_API_KEY = st.secrets["GOOGLE_MAPS_API_KEY"]
except:
    st.error("⚠️ API keys not configured")
    st.stop()

if not GEMINI_API_KEY or not GOOGLE_MAPS_API_KEY:
    st.warning("⚠️ Please add API keys in the sidebar or configure Streamlit secrets")
    st.info("""
    **To deploy publicly:**
    1. Fork this repo
    2. Deploy on Streamlit Community Cloud
    3. Add secrets in Streamlit dashboard

    **Get API Keys:**
    - Gemini: https://aistudio.google.com/apikey
    - Google Maps: https://console.cloud.google.com/apis/credentials
    """)
    st.stop()


# Initialize agents and tools
@st.cache_resource
def init_agents():
    location_agent = LocationAgent(GEMINI_API_KEY)
    midpoint_tool = MidpointTool()
    geocoder = GeocodingTool(GOOGLE_MAPS_API_KEY)
    places_tool = PlacesTool(GOOGLE_MAPS_API_KEY)
    place_finder_agent = PlaceFinderAgent(GEMINI_API_KEY, places_tool)
    distance_matrix = DistanceMatrixTool(GOOGLE_MAPS_API_KEY)
    ranking_agent = RankingAgent(GEMINI_API_KEY, distance_matrix)

    return location_agent, midpoint_tool, geocoder, place_finder_agent, distance_matrix, ranking_agent


with st.spinner("🤖 Initializing AI agents..."):
    location_agent, midpoint_tool, geocoder, place_finder_agent, distance_matrix, ranking_agent = init_agents()

st.sidebar.success("✅ All agents ready!")

# Input form
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📍 Person 1")
    location_1 = st.text_input("Location", placeholder="CN Tower, Toronto", key="loc1")
    mode_1 = st.selectbox("Travel Mode", ["walking", "transit", "driving", "bicycling"], key="mode1")

with col2:
    st.markdown("### 📍 Person 2")
    location_2 = st.text_input("Location", placeholder="Yorkdale Mall, Toronto", key="loc2")
    mode_2 = st.selectbox("Travel Mode", ["walking", "transit", "driving", "bicycling"], key="mode2")

place_type = st.selectbox("☕ What type of place?", ["cafe", "restaurant", "park", "bar", "library", "mall"])

# Search button
if st.button("🔍 Find Meeting Spots", type="primary", use_container_width=True):

    if not location_1 or not location_2:
        st.error("Please enter both locations!")
        st.stop()

    # Progress tracking
    progress_bar = st.progress(0)
    status = st.empty()

    try:
        # Step 1: Validate
        status.text("🔍 Step 1/5: Validating locations...")
        progress_bar.progress(20)

        result_1 = location_agent.location_validator(location_1)
        result_2 = location_agent.location_validator(location_2)

        # Step 2: Geocode
        status.text("📍 Step 2/5: Getting GPS coordinates...")
        progress_bar.progress(40)

        coords_1 = geocoder.geocode(location_1)
        coords_2 = geocoder.geocode(location_2)

        if not coords_1['success'] or not coords_2['success']:
            st.error("❌ Could not geocode one or more locations")
            st.stop()

        # Step 3: Calculate midpoint
        status.text("🧮 Step 3/5: Calculating fair meeting point...")
        progress_bar.progress(60)

        midpoint = midpoint_tool.find_time_fair_midpoint(
            {'lat': coords_1['lat'], 'lng': coords_1['lng']},
            {'lat': coords_2['lat'], 'lng': coords_2['lng']},
            mode1=mode_1,
            mode2=mode_2,
            distance_matrix_tool=distance_matrix
        )

        # Step 4: Find places
        status.text(f"☕ Step 4/5: Finding {place_type}s...")
        progress_bar.progress(80)

        places_result = place_finder_agent.find_places(
            midpoint={'lat': midpoint['lat'], 'lng': midpoint['lng']},
            preference=place_type,
            radius=2000
        )

        if not places_result['success']:
            st.error(f"❌ Could not find places: {places_result['error']}")
            st.stop()

        # Step 5: Rank
        status.text("🏆 Step 5/5: Ranking with AI...")
        progress_bar.progress(90)

        ranked_places = ranking_agent.rank_places(
            places=places_result['places'],
            person1_location={'lat': coords_1['lat'], 'lng': coords_1['lng']},
            person2_location={'lat': coords_2['lat'], 'lng': coords_2['lng']},
            mode1=mode_1,
            mode2=mode_2
        )

        progress_bar.progress(100)
        status.text("✅ Complete!")

        # Display results
        st.success("🎉 Found your perfect meeting spots!")

        # Show midpoint info
        st.markdown("---")
        st.markdown("## 🎯 Fair Meeting Point")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Person 1 Travel ~", midpoint.get('travel_time_person1', 'N/A'))
        with col2:
            st.metric("Person 2 Travel ~", midpoint.get('travel_time_person2', 'N/A'))
        with col3:
            st.metric("Time Difference ~", f"{midpoint.get('time_difference_minutes', 'N/A')} min")

        # # Map link
        # st.markdown(f"📍 **Coordinates:** {midpoint['lat']:.6f}, {midpoint['lng']:.6f}")
        # st.markdown(f"🗺️ [View on Google Maps](https://www.google.com/maps?q={midpoint['lat']},{midpoint['lng']})")

        # Display ranked places
        st.markdown("---")
        st.markdown(f"## ☕ Top {min(5, len(ranked_places))} Recommendations")

        for place in ranked_places[:5]:
            with st.expander(f"**#{place['rank']}. {place['name']}** ⭐ {place['rating']}",
                             expanded=(place['rank'] == 1)):

                col1, col2 = st.columns([2, 1])

                with col1:
                    st.markdown(f"📍 **Address:** {place['address']}")
                    st.markdown(f"⭐ **Rating:** {place['rating']} ({place['user_ratings_total']} reviews)")

                    if 'time_person1' in place and place['time_person1'] != 'unknown':
                        st.markdown("**Travel Times:**")
                        st.markdown(f"- Person 1 ({mode_1}): {place['time_person1']}")
                        st.markdown(f"- Person 2 ({mode_2}): {place['time_person2']}")
                        st.markdown(f"- Fairness: {place.get('travel_fairness', 'N/A')}")

                    price = '💰' * int(place['price_level']) if isinstance(place['price_level'], int) else '💰'
                    st.markdown(f"💰 **Price:** {price}")

                    if place['open_now'] is not None:
                        status_emoji = "🟢" if place['open_now'] else "🔴"
                        status_text = "Open now" if place['open_now'] else "Closed"
                        st.markdown(f"{status_emoji} **Status:** {status_text}")

                with col2:
                    # Map link
                    import urllib.parse

                    map_query = urllib.parse.quote(f"{place['name']}, {place['address']}")
                    st.markdown(f"[🗺️ View on Map](https://www.google.com/maps/search/?api=1&query={map_query})")

                st.markdown(f"💡 **Why ranked #{place['rank']}:** {place.get('ai_reasoning', 'No reasoning')}")

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.exception(e)

# Footer
st.markdown("---")
st.markdown("""
**Built with:**
- Google ADK Multi-Agent System
- Gemini AI for intelligent reasoning
- Google Maps Platform APIs
- Streamlit for web interface
- Tour icons created by Freepik - [Flaticon](https://www.flaticon.com/free-icons/tour) 

[View Code on GitHub](https://github.com/vishakavinod22/GoogleAIAgentsCapstoneProject) | Google AI Agents Capstone Project
""")