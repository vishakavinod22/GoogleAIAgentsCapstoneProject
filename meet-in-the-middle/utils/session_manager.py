"""
Session Manager
Handles session state and memory for multi-turn conversations (back and forth conversation)
"""
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
import os


class SessionManager:
    """Manages session state and user memory"""

    def __init__(self, memory_file: str = 'user_memory.json'):
        """
        Initialize session manager

        :param memory_file: Path to file for persistent memory storage
        """
        self.session_state = {}
        self.memory_file = memory_file
        self.memory_bank = self._load_memory()

    def store(self, key: str, value: Any) -> None:
        """
        Store data in current session

        :param key: Key to store under
        :param value: Data to store
        """
        self.session_state[key] = value

    def retrieve(self, key: str) -> Optional[Any]:
        """
        Retrieve data from current session

        :param key: Key to retrieve
        :return: Stored value or None if not found
        """
        return self.session_state.get(key)

    def has(self, key: str) -> bool:
        """Check if key exists in session"""
        return key in self.session_state

    def clear_session(self) -> None:
        """Clear current session state"""
        self.session_state = {}

    def get_session_summary(self) -> Dict:
        """Get summary of current session"""
        return {
            'has_locations': self.has('location_1') and self.has('location_2'),
            'has_coords': self.has('coords_1') and self.has('coords_2'),
            'has_midpoint': self.has('midpoint'),
            'has_results': self.has('last_results'),
            'location_1': self.retrieve('location_1'),
            'location_2': self.retrieve('location_2'),
            'place_type': self.retrieve('place_type')
        }

    # Memory Bank Methods (Long-term memory)

    def _load_memory(self) -> Dict:
        """Load memory bank from file"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
            except:
                pass

        # Default memory structure
        return {
            'user_preferences': {},
            'frequent_locations': {},
            'search_history': [],
            'total_searches': 0
        }

    def _save_memory(self) -> None:
        """Save memory bank to file"""
        try:
            with open(self.memory_file, 'w') as f:
                json.dump(self.memory_bank, f, indent=2)
        except Exception as e:
            print(f"⚠️  Could not save memory: {e}")

    def update_preference(self, key: str, value: Any) -> None:
        """
        Update user preference in memory bank

        :param key: Preference key (e.g., 'preferred_mode', 'likes_quiet')
        :param value: Preference value
        """
        self.memory_bank['user_preferences'][key] = value
        self._save_memory()
        print(f"   ✅ Saved preference: {key} = {value}")

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get user preference from memory bank"""
        return self.memory_bank['user_preferences'].get(key, default)

    def record_location(self, location: str) -> None:
        """Record a location in frequent locations"""
        freq = self.memory_bank['frequent_locations']
        freq[location] = freq.get(location, 0) + 1
        self._save_memory()

    def record_search(self) -> None:
        """Record that a search was performed"""
        self.memory_bank['total_searches'] += 1
        self.memory_bank['search_history'].append({
            'location_1': self.retrieve('location_1'),
            'location_2': self.retrieve('location_2'),
            'place_type': self.retrieve('place_type'),
            'timestamp': datetime.now().isoformat()
        })

        # Keep only last 10 searches
        if len(self.memory_bank['search_history']) > 10:
            self.memory_bank['search_history'] = self.memory_bank['search_history'][-10:]

        self._save_memory()

    def get_memory_summary(self) -> str:
        """Get a summary of learned preferences"""
        prefs = self.memory_bank['user_preferences']
        total = self.memory_bank['total_searches']

        if not prefs and total == 0:
            return "No preferences learned yet."

        summary = f"Total searches: {total}\n"

        if prefs:
            summary += "Learned preferences:\n"
            for key, value in prefs.items():
                summary += f"  - {key}: {value}\n"

        freq_locs = self.memory_bank['frequent_locations']
        if freq_locs:
            top_locs = sorted(freq_locs.items(), key=lambda x: x[1], reverse=True)[:3]
            summary += "Frequent locations:\n"
            for loc, count in top_locs:
                summary += f"  - {loc} ({count} times)\n"

        return summary


# Test
if __name__ == "__main__":
    print("🧪 Testing Session Manager...")
    print("=" * 50)

    # Create session manager
    session = SessionManager('test_memory.json')

    # Test session state
    print("\n--- Testing Session State ---")
    session.store('location_1', 'CN Tower')
    session.store('location_2', 'Yorkdale')
    session.store('mode_1', 'walking')

    print(f"Stored location_1: {session.retrieve('location_1')}")
    print(f"Has midpoint? {session.has('midpoint')}")
    print(f"Session summary: {session.get_session_summary()}")

    # Test memory bank
    print("\n--- Testing Memory Bank ---")
    session.update_preference('preferred_mode', 'walking')
    session.update_preference('likes_quiet', True)
    session.record_location('CN Tower')
    session.record_location('CN Tower')
    session.record_location('Yorkdale')
    session.record_search()

    print(f"\nMemory Summary:\n{session.get_memory_summary()}")

    # Test retrieval
    print("\n--- Testing Preference Retrieval ---")
    print(f"Preferred mode: {session.get_preference('preferred_mode')}")
    print(f"Likes quiet: {session.get_preference('likes_quiet')}")
    print(f"Unknown pref: {session.get_preference('unknown', 'default_value')}")

    print("\n✅ Session Manager working!")