import socketio
import yaml 
from pathlib import Path 

import json
from jsonschema import validate, ValidationError


ROOT_DIR = Path(__file__).parents[2]
CONFIG_FILE = ROOT_DIR / "config.yaml"

with open(CONFIG_FILE, "r") as file:
    CONFIG = yaml.safe_load(file)

BREATHING_LOG_PATH = ROOT_DIR / "data" / "breathing_log" / "log.txt"
PAIN_LOG_PATH = ROOT_DIR / "data" / "pain_log" / "log.txt"
POSITION_LOG_PATH = ROOT_DIR / "data" / "position_log" / "log.txt"
MEDICATION_LOG_PATH = ROOT_DIR / "data" / "medication_log" / "log.txt"
DATA_DIR = ROOT_DIR / CONFIG["DATA_STORE_FOLDER"]

DECISION = False 
SCHEMA = {
  "type": "object",
  "additionalProperties": False,
  "required": [
    "total_events",
    "posture_events",
    "breathing_events",
    "medication_events",
    "time_series",
    "intervention_trend"
  ],
  "properties": {
    "total_events": { "type": "integer", "minimum": 0 },
    "posture_events": { "type": "integer", "minimum": 0 },
    "breathing_events": { "type": "integer", "minimum": 0 },
    "medication_events": { "type": "integer", "minimum": 0 },

    "time_series": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties":False,
        "required": ["timestamp", "event_count"],
        "properties": {
          "timestamp": { "type": "string" },
          "event_count": { "type": "integer", "minimum": 0 }
        }
      }
    },

    "intervention_trend": {
      "type": "object",
      "additionalProperties": False,
      "required": ["posture", "breathing", "medication"],
      "properties": {
        "posture": {
          "type": "array",
          "items": { "type": "integer", "minimum": 0 }
        },
        "breathing": {
          "type": "array",
          "items": { "type": "integer", "minimum": 0 }
        },
        "medication": {
          "type": "array",
          "items": { "type": "integer", "minimum": 0 }
        }
      }
    }
  }
}

sio = socketio.Client()
sio.connect("http://127.0.0.1:5050", namespaces=["/"])


@sio.event
def connect():
    print("✅ Connected to Flask server")


def validate_als_summary(output: str):
    try:
        print(output)
        data = json.loads(output)
        validate(instance=data, schema=SCHEMA)
        
        return data
    except (json.JSONDecodeError, ValidationError):
        
        return None
    
def load_text_file(loc:str)->str:
    
    with open(loc, "r") as file:
        contents = file.read()

    return contents 

breathing_contents = load_text_file(BREATHING_LOG_PATH)
pain_contents = load_text_file(PAIN_LOG_PATH)
medication_contents = load_text_file(MEDICATION_LOG_PATH)
position_contents = load_text_file(POSITION_LOG_PATH)

@sio.on("analysis_result")
def on_result(data):

    try:
        print("Received from server:", data)
        text = data["text"].replace("```","")
        text = text.replace("\n","")
        text = text.replace("json","")
        text = text + "}"
        result = validate_als_summary(text)

        with open(f"{DATA_DIR}/outputs.json", "w") as file:
            json.dump(result, file)

        print("Saved to JSON File.")

    except Exception as e:
        print("An Error Occured :", e)
    

if __name__ == "__main__":

    print("Request Sent !")
    sio.emit("get_summary", {
        "bc": breathing_contents,
        "pc": pain_contents,
        "mc": medication_contents,
        "oc": position_contents
    })

    sio.wait()
