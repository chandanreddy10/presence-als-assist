from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import time
import uuid
import json
import threading

from ws import safe_send, responses, responses_lock, init_ws
from tts_service import generate_tts_audio
import base64
import numpy as np
import cv2
import os
import yaml
from pathlib import Path

import json
from jsonschema import validate, ValidationError

# -------------------------CONFIG----------------------------------
ROOT_DIR = Path(__file__).parents[1]
CONFIG_FILE = ROOT_DIR / "config.yaml"

with open(CONFIG_FILE, "r") as file:
    CONFIG = yaml.safe_load(file)

DATA_FOLDER = ROOT_DIR / CONFIG["DATA_STORE_FOLDER"]
IMAGE_FOLDER = DATA_FOLDER / CONFIG["IMAGE_STORE_FOLDER"]
PAIN_LOG_FOLDER = DATA_FOLDER / "pain_log"
POSITION_LOG_FOLDER = DATA_FOLDER / "position_log"
BREATHING_LOG_FOLDER = DATA_FOLDER / "breathing_log"
MEDICATION_LOG_FOLDER = DATA_FOLDER / "medication_log"

global LATEST_FRAME, POSITION_STATUS, BREATHING_STATUS, MEDICATION_STATUS

LATEST_FRAME = None
POSITION_STATUS = None
BREATHING_STATUS = None
MEDICATION_STATUS = None
PREVIOUS_QA = {}

TIMESTAMP = time.strftime("%Y%m%d_%H%M%S")

# Initialize the websocket.
init_ws()

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

lock = threading.Lock()
story_history = []

SCHEMA = {
    "type": "object",
    "properties": {
        "safety_status": {"type": "string", "enum": ["safe", "unsafe"]},
        "count_people": {"type": "integer", "minimum": 0},
        "reason": {"type": "string", "minLength": 3, "maxLength": 50},
    },
    "required": ["safety_status", "count_people", "reason"],
    "additionalProperties": False,
}


def make_dir(dest:str):
    os.makedirs(dest, exist_ok=True)

make_dir(DATA_FOLDER)
make_dir(IMAGE_FOLDER)
make_dir(PAIN_LOG_FOLDER)
make_dir(POSITION_LOG_FOLDER)
make_dir(BREATHING_LOG_FOLDER)
make_dir(MEDICATION_LOG_FOLDER)

def send_vm_request(
    socketio,
    sid,
    safe_send,
    responses,
    responses_lock,
    request_type: str,
    text: str = "",
    image: str = None,
    timeout: int = 120,
):
    """
    Function to send a request to VM / Remote machine that hosts gemma4.
    """
    request_id = str(uuid.uuid4())

    payload = {
        "request_id": request_id,
        "text": text,
        "request": request_type,
    }

    if image is not None:
        payload["image_for_intent"] = image

    safe_send(json.dumps(payload))

    start = time.time()
    result = None

    while time.time() - start < timeout:
        socketio.sleep(0.05)

        with responses_lock:
            if request_id in responses:
                result = responses.pop(request_id)
                break

    if result is None:
        socketio.emit("error", {"message": "VM timeout"}, to=sid)
        return None

    return result


# webpage
@app.route("/")
def index():
    return render_template("home.html")


@socketio.on("gaze_data")
def handle_gaze(data):
    socketio.emit("cursor_move", data, broadcast=True)


@socketio.on("sentence")
def select(data):
    intent = data.get("sentence")
    intent = ",".join(intent)
    print(intent)
    if not intent:
        socketio.emit("sentence_error", {"error": "Empty sentence"})
        return

    request_id = str(uuid.uuid4())

    # send to VM
    safe_send(
        json.dumps({"request_id": request_id, "text": intent, "request": "sentence"})
    )

    # wait for response
    timeout = 120
    start = time.time()
    result = None

    while time.time() - start < timeout:
        with responses_lock:
            if request_id in responses:
                result = responses.pop(request_id)
                break
        time.sleep(0.05)

    # timeout case
    if result is None:
        socketio.emit("sentence_error", {"error": "VM timeout"})
        return

    # generate TTS
    generate_tts_audio(result["text"])

    # # send back to UI
    # socketio.emit("sentence_result", {
    #     "text": result["text"],
    #     "audio": audio_path
    # })


@socketio.on("phrase_selected")
def handle_phrase(data):
    print(data)
    phrase = data.get("sentence")
    phrase = ",".join(phrase)
    if not phrase:
        socketio.emit("error", {"message": "No phrase provided"}, to=request.sid)
        return

    request_id = str(uuid.uuid4())

    # 🔹 Send request to VM
    safe_send(
        json.dumps({"request_id": request_id, "text": phrase, "request": "phrase"})
    )

    # 🔹 Tell UI we're processing (important for gaze UX)
    socketio.emit("loading", {"status": "processing"}, to=request.sid)

    # 🔹 Wait for response (non-blocking style)
    timeout = 120
    start = time.time()

    result = None

    while time.time() - start < timeout:
        socketio.sleep(0.05)  # ✅ IMPORTANT: non-blocking

        with responses_lock:
            if request_id in responses:
                result = responses.pop(request_id)
                break

    # 🔴 Timeout case
    if result is None:
        socketio.emit("error", {"message": "VM timeout"}, to=request.sid)
        return

    # 🟢 Success case
    socketio.emit("new_phrases", {"phrases": result}, to=request.sid)


@socketio.on("select_text")
def handle_select_text(data):
    """
    Receives gaze-selected text from frontend
    """

    text = (data.get("text") or "").strip()

    global POSITION_STATUS

    if "position" in text.lower():

        result = send_vm_request(
            socketio=socketio,
            sid=request.sid,
            safe_send=safe_send,
            responses=responses,
            responses_lock=responses_lock,
            request_type="position",
            text="",
            image=LATEST_FRAME,
            timeout=120,
        )

        if result is None:
            return

        POSITION_STATUS = result.get("text")
        print(POSITION_STATUS)

    elif "breathing" in text.lower():
        global BREATHING_STATUS

        result = send_vm_request(
            socketio=socketio,
            sid=request.sid,
            safe_send=safe_send,
            responses=responses,
            responses_lock=responses_lock,
            request_type="breathing",
            text="",
            image=LATEST_FRAME,
            timeout=120,
        )

        if result is None:
            return

        BREATHING_STATUS = result.get("text")
        print(BREATHING_STATUS)

    elif "medication" in text.lower():
        global MEDICATION_STATUS

        result = send_vm_request(
            socketio=socketio,
            sid=request.sid,
            safe_send=safe_send,
            responses=responses,
            responses_lock=responses_lock,
            request_type="medication",
            text="",
            image=LATEST_FRAME,
            timeout=120,
        )

        if result is None:
            return

        MEDICATION_STATUS = result.get("text")
        print(MEDICATION_STATUS)


@socketio.on("pain_gq")
def handle_select_text(data):
    """
    Function to handle Guided Questioning for Pain related Issues.

    """
    question = data.get("question")
    answer = data.get("answer")

    answer = answer.replace("\n", "")

    PREVIOUS_QA.update({question: answer})

    query_to_llm = [
        f"Previous Question-{index} : {key}, Previous Answer-{index}: {value}"
        for index, (key, value) in enumerate(PREVIOUS_QA.items())
    ]

    query_to_llm = " ".join(query_to_llm)

    image_in_str = LATEST_FRAME

    request_id = str(uuid.uuid4())
    if answer.strip().lower() == "end":
        safe_send(
            json.dumps(
                {
                    "request_id": request_id,
                    "text": query_to_llm,
                    "image_for_intent": image_in_str,
                    "request": "pain_end",
                }
            )
        )
    else:
        safe_send(
            json.dumps(
                {
                    "request_id": request_id,
                    "text": query_to_llm,
                    "image_for_intent": image_in_str,
                    "request": "pain",
                }
            )
        )

    ##Not Implemented
    socketio.emit("loading", {"status": "processing"}, to=request.sid)

    timeout = 120
    start = time.time()

    result = None

    while time.time() - start < timeout:

        with responses_lock:
            if request_id in responses:
                result = responses.pop(request_id)
                break

    if result is None:
        socketio.emit("error", {"message": "VM timeout"}, to=request.sid)
        return

    socketio.emit("new_question", {"question": result}, to=request.sid)

    if answer.strip().lower() == "end":
        with open(f"{PAIN_LOG_FOLDER}\\logs.txt", "a+") as file:
            message = f"{TIMESTAMP}\n{result["text"]}"
            file.write(message)
        print("Saved to file.")


def process_story_request(sid, request_id, text):
    try:
        # Send to VM / model
        safe_send(
            json.dumps({"request_id": request_id, "text": text, "request": "story"})
        )

        timeout = 120
        start = time.time()
        result = None

        while time.time() - start < timeout:

            with responses_lock:
                if request_id in responses:
                    result = responses.pop(request_id)
                    break

        # ❌ TIMEOUT
        if result is None:
            socketio.emit("error", {"message": "VM timeout"}, to=sid)
            socketio.emit("story_ack", {}, to=sid)
            return

        # ✅ SUCCESS
        story_history.append(result["text"])

        generate_tts_audio(result["text"], voice="not default")

        socketio.emit(
            "update_options",
            {
                "options": [
                    "Tell me more about the live longer",
                    "Tell me more about the live longer",
                    "Also more about the live longer.",
                ]
            },
            to=sid,
        )

        # 🔑 UNLOCK CLIENT
        socketio.emit("story_ack", {}, to=sid)

    except Exception as e:
        print("❌ Error:", e)
        socketio.emit("error", {"message": "Server error"}, to=sid)
        socketio.emit("story_ack", {}, to=sid)


@socketio.on("story_text")
def handle_select_text(data):
    sid = request.sid
    text = (data.get("text") or "").strip()

    if not text:
        socketio.emit("error", {"message": "No phrase provided"}, to=sid)
        socketio.emit("story_ack", {}, to=sid)
        return

    if "option" in text.lower():
        socketio.emit("story_ack", {}, to=sid)
        return

    story_history.append(text)

    request_id = str(uuid.uuid4())

    socketio.emit("loading", {"status": "processing"}, to=sid)

    # 🔥 IMPORTANT: run async
    socketio.start_background_task(process_story_request, sid, request_id, text)

def write_output_to_file(FILE_PATH : str, text:str, TIMESTAMP=TIMESTAMP):
    with open(FILE_PATH, "a+") as file:
        message = f"{TIMESTAMP}\n{text}"
        file.write(message)
    
# Gaze Tracker
# Connection between the gaze detection file and the webpage.
# this socket helps in  communicating the gaze data to the webpage.
@socketio.on("gaze_data")
def handle_gaze(data):
    x = data.get("x")
    y = data.get("y")

    print("Received gaze:", x, y)

    socketio.emit("cursor_move", {"x": x, "y": y})


def enforce_schema(llm_output: str):
    try:
        data = json.loads(llm_output)
        validate(instance=data, schema=SCHEMA)
        return data  # valid
    except (json.JSONDecodeError, ValidationError):
        return None  #


@socketio.on("frame_data")
def handle_frame(data):
    global LATEST_FRAME
    global POSITION_STATUS
    global BREATHING_STATUS
    global MEDICATION_STATUS 

    try:
        print("Frame received")

        if not data:
            return

        LATEST_FRAME = data["image"]
        print("Saved Latest Frame")

        request_id = str(uuid.uuid4())
        safe_send(
            json.dumps(
                {
                    "request_id": request_id,
                    "text": "",
                    "image_as_str": LATEST_FRAME,
                    "request": "image",
                }
            )
        )

        print("Frame sent to VM")

        timeout = 120
        start = time.time()
        result = None

        while time.time() - start < timeout:
            socketio.sleep(1)
            with responses_lock:
                if request_id in responses:
                    result = responses.pop(request_id)
                    break

        # ❗ TIMEOUT HANDLING
        if result is None:
            print("VM timeout for frame")
            socketio.emit("error", {"message": "Image processing timeout"})
            return

        #
        text = result.get("text") or result.get("response")
        if not text:
            print("Invalid VM response:", result)
            return
        text = enforce_schema(text)
        safety_status = text.get("safety_status")
        num_people = text.get("count_people")
        num_people = int(num_people)

        if (num_people >= 0) and (POSITION_STATUS is not None):

            generate_tts_audio(POSITION_STATUS)
            write_output_to_file(f"{POSITION_LOG_FOLDER}\\logs.txt", text=POSITION_STATUS)
       
            POSITION_STATUS = None
        
        if (num_people >= 0) and (BREATHING_STATUS is not None):
            
            generate_tts_audio(BREATHING_STATUS)
            write_output_to_file(f"{BREATHING_LOG_FOLDER}\\logs.txt", text=BREATHING_STATUS)

            BREATHING_STATUS = None
        
        if (num_people >= 0) and (MEDICATION_STATUS is not None):
            
            generate_tts_audio(MEDICATION_STATUS)
            write_output_to_file(f"{MEDICATION_LOG_FOLDER}\\logs.txt", text=MEDICATION_STATUS)

            MEDICATION_STATUS = None

        if safety_status.lower() == "unsafe":
            pass
            ## Caretaker Integration

    except Exception as e:
        print("Error handling frame:", e)

@socketio.on("get_summary")
def handle_get_summary(data:dict)->dict:

    breathing_related_info = data.get("bc")
    pain_related_info = data.get("pc")
    medication_related_info = data.get("mc")
    position_related_info = data.get("oc")

    message = f"""Breathing Logs: {breathing_related_info}\n
                  Pain Logs: {pain_related_info}\n
                  Medication Logs: {medication_related_info}\n
                  Position Logs: {position_related_info}"""
    result = send_vm_request(
            socketio=socketio,
            sid=request.sid,
            safe_send=safe_send,
            responses=responses,
            responses_lock=responses_lock,
            request_type="summary",
            text=message,
            image=None,
            timeout=120,
    )
    if result is None:
        return

    socketio.emit("analysis_result", result)

if __name__ == "__main__":
    socketio.run(app, host="127.0.0.1", port=5050, debug=True)
