# Meet in the Middle

AI-Powered Fair Meeting Location Finder using Multi-Agent System

- **Competition:** Google 5-Day AI Agents Intensive Capstone Project  
- **Track:** Concierge Agents

---

## Problem Statement

When friends meet up from different locations, finding a fair meeting point is challenging:
- Traditional geographic midpoints ignore travel time differences
- One person walking 90 minutes while the other drives 15 minutes is unfair
- No intelligent recommendations for actual meeting places

**This is a real problem:** Millions of people coordinate meetups daily, and finding a fair meeting point lead to frustration and cancelled plans.

---

## Solution

**Meet in the Middle** uses a multi-agent AI system to:
1. Calculate time-fair midpoints (not just geographic centers)
2. Find highly-rated meeting spots (cafes, restaurants, parks, etc)
3. Rank recommendations intelligently using AI

### Key Innovation: Time-Based Fairness

Unlike traditional midpoint calculators, we calculate **actual travel times** to find locations where both people arrive at approximately the same time.

**Example:**
- Geographic midpoint: Person A walks 90 mins, Person B drives 15 mins ❌
- Time-fair midpoint: Person A walks 45 mins, Person B drives 20 mins ✅

---


## Demo

- Demo Video: https://youtu.be/jQxHne0hI2U
- Live Demo: https://meetinthemiddle.streamlit.app
- GitHub: https://github.com/vishakavinod22/GoogleAIAgentsCapstoneProject/

---

## Competition Criteria Met

| Criteria | Implementation                             | Status |
|----------|--------------------------------------------|--------|
| **Multi-Agent System** | Agent powered by an LLM, Sequential agents | ✅ |
| **Tools** | 4 Custom tools                             | ✅ |
| **Sessions & Memory** | Sessions & state management               | ✅ |
| **Agent deployment** |       https://meetinthemiddle.streamlit.app        | ✅

---

## Architecture

### Multi-Agent System
```
User Input
    ↓
LocationAgent (Gemini) → Validates locations
    ↓
GeocodingTool → Gets GPS coordinates
    ↓
DistanceMatrixTool → Calculates travel times
    ↓
MidpointTool → Finds time-fair midpoint
    ↓
PlaceFinderAgent (Gemini) → Searches nearby places
    ↓
RankingAgent (Gemini) → Ranks by fairness + quality
    ↓
Results with intelligent recommendations
```

### Agents (AI-Powered)
- **LocationAgent**: Validates and parses location inputs
- **PlaceFinderAgent**: Understands preferences, finds meeting spots
- **RankingAgent**: Intelligently ranks places by multiple factors

### Custom Tools
- **GeocodingTool**: Converts addresses to coordinates (Google Maps API)
- **MidpointTool**: Calculates weighted and time-fair midpoints
- **PlacesTool** : Searches nearby places (Google Places API)
- **DistanceMatrixTool** : Gets actual travel times (Google Distance Matrix API)

### Sessions & Memory
- **Session State**: Remembers current search (locations, modes, results)
- **Memory Bank**: Learns user preferences across sessions
- **Refinement Flow**: Users can refine searches without re-entering data

**Implementation Status:**

#### ✅ Fully Implemented in CLI Version (`main.py`)
The command-line interface includes complete session and memory features:
- **Session State**: Remembers current search (locations, modes, results) within the active session
- **Memory Bank**: Learns user preferences across sessions via `user_memory.json`
  - Tracks frequent locations
  - Stores user preferences (quiet places, budget-friendly, etc.)
  - Records search history
- **Refinement Flow**: Users can refine searches without re-entering data
  - Change place type while keeping same locations
  - Adjust search radius
  - Set preferences that persist

**Example CLI Memory Features:**
```bash
$ python main.py

📚 Your Memory Bank:
Total searches: 3
Learned preferences:
  - likes_quiet: True
  - preferred_mode: walking
Frequent locations:
  - CN Tower (3 times)
  - Yorkdale Mall (2 times)

🔄 Previous search found!
   Locations: CN Tower ↔ Yorkdale Mall
Use previous locations? (y/n): y
```

#### 🚧 Work In Progress for Streamlit Web Interface (`app.py`)
The web interface currently maintains:
- ✅ Active session state during use (via Streamlit's session management)
- ✅ Input persistence while app is open
- ⚠️ **Not yet implemented**: Cross-session memory persistence

**Why the difference?**
- CLI version: File-based storage is simple and works perfectly for local use
- Web version: Requires database for multi-user, stateless cloud deployment
- Current priority: Core functionality and deployment (memory DB integration planned for v2.0)

---

## ADK Features Demonstrated

This project demonstrates **3+ required criteria:**

### 1. Multi-Agent System ✅
- 3 LLM-powered agents (LocationAgent, PlaceFinderAgent, RankingAgent)
- Sequential agent flow
- Agents collaborate to solve complex problem

### 2. Tools ✅
- 4 custom/built-in tools
- External API integration (Google Maps)
- Custom algorithms (time-fair midpoint calculation)

### 3. Sessions & Memory ✅
- Session state management (InMemorySessionService pattern)
- Long-term memory (Memory Bank with file persistence)
- Context retention across refinements

### 4. Agent deployment ✅
- The agent is deployed with Streamlit and can be accessed [here](https://meetinthemiddle.streamlit.app)

### Example Output
```
✅ Fair meeting point found!
   Method: time_based_fairness

⏱️  Travel Times:
   Person 1 (walking): 48 mins
   Person 2 (driving): 21 mins
   Time difference: 27 minutes
   Fairness ratio: 0.69

✅ Top 5 Recommendations:

#1. 📍 Balzac's Coffee
    Rating: ⭐ 4.7 (892 reviews)
    Travel Times:
      • Person 1 (walking): 45 mins
      • Person 2 (driving): 19 mins
      • Fairness Score: 0.73
    💡 Why: Excellent travel fairness and high-quality ratings
    Status: 🟢 Open now
```

---

## Key Features

### 1. Time-Based Fairness Based on Travel Modes
- Calculates actual travel times, not just distance
- Tests 7 candidate midpoints to find fairest option
- Considers different travel modes (walking, driving, transit, bicycling)

### 2. Intelligent Ranking
- AI analyzes multiple factors: quality, popularity, fairness, price
- Considers user preferences from memory
- Provides reasoning for each recommendation

### 3. Smart Memory System
- Remembers frequent locations
- Learns preferences (quiet places, budget-friendly, etc.)
- Enables quick refinement without re-entering data

### 4. Refinement Flow
- Change place type without re-entering locations
- Adjust search radius
- Set preferences that persist across sessions

---

## Prerequisites

- Python 3.11 or higher
- Google Cloud account (for Maps APIs)
- Gemini API access

---

## Local Development Setup

### 1. Clone the Repository
```bash
git clone https://github.com/vishakavinod22/GoogleAIAgentsCapstoneProject.git
cd meet-in-the-middle
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API Keys

Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
```

**Get API Keys:**
- **Gemini API:** https://aistudio.google.com/apikey
- **Google Maps API:** https://console.cloud.google.com/apis/credentials

**Enable Required Google Maps APIs:**
1. Go to Google Cloud Console
2. Enable:
   - Directions API 
   - Distance Matrix API 
   - Geocoding API 
   - Places API 
   - Places API (New)

### 5. Run the Application

**Terminal Interface:**
```bash
python main.py
```

**Web Interface (Streamlit):**
```bash
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

---

## Testing

Run individual components:
```bash
# Test agents
python agents/location_agent.py
python agents/place_finder_agent.py
python agents/ranking_agent.py

# Test tools
python tools/geocoding_tool.py
python tools/midpoint_tools.py
python tools/distance_matrix_tool.py

# Test utilities
python utils/session_manager.py
```
---

## Project Structure Explained
```
meet-in-the-middle/
├── agents/                     # AI-powered decision makers
│   ├── location_agent.py       # Validates location inputs with Gemini
│   ├── place_finder_agent.py   # Finds meeting spots using AI reasoning
│   └── ranking_agent.py        # Ranks results intelligently
├── tools/                      # Utility tools (no AI)
│   ├── geocoding_tool.py       # Address → GPS conversion
│   ├── midpoint_tools.py       # Calculates fair midpoints
│   ├── places_tool.py          # Searches nearby places
│   └── distance_matrix_tool.py # Gets real travel times
├── utils/                      # Support infrastructure
│   ├── session_manager.py      # Manages state & memory
│   └── refinement_helper.py    # UI helper functions
├── main.py                     # CLI interface
├── app.py                      # Web interface (Streamlit)
├── requirements.txt            # Python dependencies    
└── README.md                  # This file
```

---

## 🐛 Troubleshooting

**Issue: "API keys not found"**
- Make sure `.env` file exists in project root
- Check that keys are correctly formatted (no quotes, no spaces)

**Issue: "Geocoding failed"**
- Verify Google Maps APIs are enabled
- Check that billing is set up (required for Maps APIs)
- Ensure API key has no restrictions blocking the APIs

**Issue: "Module not found"**
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt` again

---

## Deployment

- **Platform:** Streamlit Community Cloud  
- **Live URL:** https://meetinthemiddle.streamlit.app
- **Status:** ✅ Deployed and publicly accessible

The application is deployed on Streamlit's cloud platform, providing:
- Public access via web browser
- Automatic deployment from GitHub (CI/CD)
- Secure secrets management for API keys
- Cross-device compatibility (desktop, mobile, tablet)

**Deployment Architecture:**
- Code hosted on GitHub (version control)
- Streamlit Cloud monitors repository for changes
- Auto-redeploys on push to main branch
- Environment variables managed via Streamlit secrets

No infrastructure management required - fully serverless deployment.

### Deployment Instructions

#### Deploy Your Own Instance on Streamlit Cloud

1. **Fork this repository** to your GitHub account

2. **Go to Streamlit Cloud:** https://share.streamlit.io/

3. **Sign in** with GitHub

4. **Click "New app"**

5. **Configure:**
   - Repository: `your-username/meet-in-the-middle`
   - Branch: `main`
   - Main file path: `app.py`

6. **Add Secrets** (Click "Advanced settings"):
```toml
   GEMINI_API_KEY = "your_gemini_api_key"
   GOOGLE_MAPS_API_KEY = "your_google_maps_api_key"
```

7. **Click "Deploy"**

8. **Wait 2-3 minutes** for deployment to complete

9. **Access your app** at: `https://your-app-name.streamlit.app`

### Environment Variables Required

- `GEMINI_API_KEY` - Get from: https://aistudio.google.com/apikey
- `GOOGLE_MAPS_API_KEY` - Get from: https://console.cloud.google.com/apis/credentials

---

## Technical Highlights

- **Python 3.11+** with Google ADK
- **Gemini 2.5 Flash** for AI reasoning
- **Google Maps APIs** for real-world data
- **Haversine formula** for distance calculations
- **File-based persistence** for memory
- **Clean agent architecture** following ADK patterns

---

## Future Enhancements

### High Priority: Persistent Database Integration 
Currently, session state and memory are managed only in the backend Python layer. Plan to integrate a database (MongoDB or PostgreSQL) to:
  - Store previous searches across sessions
  - Enable search history retrieval
  - Sync state between frontend and backend
  - Allow users to bookmark favorite meeting spots
  
### Additional Features
- **Cloud Deployment**: Deploy to Google Cloud Run for improved scalability
- **Multi-Person Support**: Extend to 3+ people with optimized fair midpoints
- **Real-Time Traffic**: Integrate live traffic data for more accurate travel times
- **Weather Integration**: Factor weather conditions into recommendations
- **International Support**: Expand beyond local regions for global meetups

---

## Author

Vishaka Vinod 

- Competition: Google 5-Day AI Agents Intensive  
- Date: 14 Nov 2025 - 1 Dec 2025

---

## Acknowledgments
I want to thank the creators of the Google AI Agents Intensive Course for the structured curriculum that shaped this project’s foundation.

I received valuable support from Claude AI, especially for idea refinement, debugging, and development guidance throughout the build. I also relied on the Google Maps Platform for accurate location, routing, and distance APIs that power the core functionality of this app.

And finally, a heartfelt thank you to my friends and family for their constant encouragement and for pushing me to complete this submission even when I had doubts.