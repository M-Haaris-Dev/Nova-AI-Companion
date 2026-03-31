import os
import json
import time

EMOTION_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "miyuki_emotion.json")
COMMAND_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "miyuki_command_bridge.json")

def send_emotion(emotion, message="", duration=5000):
    data = {
        "emotion": emotion,
        "message": message,
        "timestamp": time.time(),
        "duration": duration
    }
    try:
        with open(EMOTION_FILE, "w") as f:
            json.dump(data, f)
    except Exception:
        pass

def read_emotion():
    try:
        if os.path.exists(EMOTION_FILE):
            with open(EMOTION_FILE, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return {"emotion": "neutral", "message": "", "timestamp": 0, "duration": 0}

def reset_emotion():
    send_emotion("neutral", "", 0)

def send_command(action, params="", source="companion"):
    data = {
        "action": action,
        "params": params,
        "source": source,
        "timestamp": time.time(),
        "executed": False
    }
    try:
        with open(COMMAND_FILE, "w") as f:
            json.dump(data, f)
    except Exception:
        pass

def read_command():
    try:
        if os.path.exists(COMMAND_FILE):
            with open(COMMAND_FILE, "r") as f:
                data = json.load(f)
            if not data.get("executed", True):
                return data
    except Exception:
        pass
    return None

def mark_command_executed():
    try:
        if os.path.exists(COMMAND_FILE):
            with open(COMMAND_FILE, "r") as f:
                data = json.load(f)
            data["executed"] = True
            with open(COMMAND_FILE, "w") as f:
                json.dump(data, f)
    except Exception:
        pass

def clear_command():
    try:
        if os.path.exists(COMMAND_FILE):
            os.remove(COMMAND_FILE)
    except Exception:
        pass