import json
import os

CHAT_STORE_FILE = "data/chat_store.json"

def load_history():
    if os.path.exists(CHAT_STORE_FILE):
        try:
            with open(CHAT_STORE_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            return {}
    return {}

def save_history(data):
    try:
        with open(CHAT_STORE_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        return f"[Error] Failed to save chat history: {e}"
