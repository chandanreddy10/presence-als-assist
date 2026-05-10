from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import time
import uuid
import json
import threading

from ws import safe_send, responses, responses_lock, init_ws
from tts_service import generate_tts_audio

#Initialize the websocket.
init_ws()

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

lock = threading.Lock()

#webpage
@app.route("/")
def index():
    return render_template("home.html")

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

if __name__ == "__main__":
    socketio.run(app, host="127.0.0.1", port=5050, debug=True)