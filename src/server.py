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

ROOT_DIR = Path(__file__).parents[1]
CONFIG_FILE = ROOT_DIR / "config.yaml"

with open(CONFIG_FILE, "r") as file:
    CONFIG = yaml.safe_load(file)

DATA_FOLDER = ROOT_DIR / CONFIG["DATA_STORE_FOLDER"]
IMAGE_FOLDER = DATA_FOLDER / CONFIG["IMAGE_STORE_FOLDER"]
PAIN_LOG_FOLDER = DATA_FOLDER / "pain_log"

os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(IMAGE_FOLDER, exist_ok=True) 
os.makedirs(PAIN_LOG_FOLDER, exist_ok=True) 
#Initialize the websocket.
init_ws()

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

lock = threading.Lock()
story_history = []

PREVIOUS_QA = {}
#webpage
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
    safe_send(json.dumps({
        "request_id": request_id,
        "text": intent,
        "request": "sentence"
    }))

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
        socketio.emit("sentence_error", {
            "error": "VM timeout"
        })
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
    safe_send(json.dumps({
        "request_id": request_id,
        "text": phrase,
        "request":"phrase"
    }))

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
        socketio.emit("error", {
            "message": "VM timeout"
        }, to=request.sid)
        return

    # 🟢 Success case
    socketio.emit("new_phrases", {
        "phrases": result
    }, to=request.sid)

@socketio.on("select_text")
def handle_select_text(data):
    """
    Receives gaze-selected text from frontend
    """

    text = (data.get("text") or "").strip()
    if "Position" in text:
        generate_tts_audio("I have a problem with my seating position.")
    elif "Breathing" in text:
        generate_tts_audio("I cannot breathe properly !")
    elif "Others" in text:
        generate_tts_audio("I am thirsty !")
    elif "Medication" in text:
        generate_tts_audio("I need to take my medication.") 
    else:
        generate_tts_audio("I need to") 

@socketio.on("pain_gq")
def handle_select_text(data):

    """
    Function to handle Guided Questioning for Pain related Issues.
    
    """
    question = data.get("question")
    answer = data.get("answer")
    
    answer = answer.replace("\n","")
    print(answer.strip().lower())
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    PREVIOUS_QA.update({question:answer})
    print(PREVIOUS_QA)
    query_to_llm = [f"Previous Question-{index} : {key}, Previous Answer-{index}: {value}" for index, (key, value) in enumerate(PREVIOUS_QA.items())]

    query_to_llm= " ".join(query_to_llm)
    
    with open(f"{IMAGE_FOLDER}\\frame_latest.txt", "r") as file:
        image_in_str = file.read()

    request_id = str(uuid.uuid4())
    if answer.strip().lower()=="end":
        safe_send(json.dumps({
        "request_id": request_id,
        "text": query_to_llm,
        "image_for_intent": image_in_str,
        "request":"pain_end"
    }))
    else:
        safe_send(json.dumps({
            "request_id": request_id,
            "text": query_to_llm,
            "image_for_intent": image_in_str,
            "request":"pain"
        }))

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
        socketio.emit("error", {
            "message": "VM timeout"
        }, to=request.sid)
        return
    
    socketio.emit("new_question", {
        "question": result
    }, to=request.sid)

    if answer.strip().lower() == "end":
        with open(f"{PAIN_LOG_FOLDER}\\logs.txt","a+") as file:
            message = f"{timestamp}\n{result["text"]}"
            file.write(message)
        print("Saved to file.")

def process_story_request(sid, request_id, text):
    try:
        # Send to your VM / model
        safe_send(json.dumps({
            "request_id": request_id,
            "text": text,
            "request": "story"
        }))

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
                    "Also more about the live longer."
                ]
            },
            to=sid
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
    socketio.start_background_task(
        process_story_request,
        sid,
        request_id,
        text
    )

#Gaze Tracker
#Connection between the gaze detection file and the webpage.
#this socket helps in  communicating the gaze data to the webpage.
@socketio.on("gaze_data")
def handle_gaze(data):
    x = data.get("x")
    y = data.get("y")

    print("Received gaze:", x, y)

    socketio.emit("cursor_move", {
        "x": x,
        "y": y
    })

@socketio.on("frame_data")
def handle_frame(data):
    try:
        print("Frame received")

        if not data:
            return
        
        with open(f"{IMAGE_FOLDER}/frame_latest.txt","w") as file:
            file.write(data["image"])
        print("Saved Latest Frame")

        request_id = str(uuid.uuid4())
        safe_send(json.dumps({
        "request_id": request_id,
        "text": data["image"],
        "request":"image"
        }))
    
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

        # ❗ SAFETY CHECK
        text = result.get("text") or result.get("response")
        if not text:
            print("Invalid VM response:", result)
            return
        print(text)
        # generate_tts_audio(text, voice="not default")

    except Exception as e:
        print("Error handling frame:", e)


if __name__ == "__main__":
    socketio.run(
    app,
    host="127.0.0.1",
    port=5050,
    debug=True
)