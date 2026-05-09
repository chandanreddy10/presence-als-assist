from flask import Flask, render_template, request, jsonify, send_file
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

#main API
@app.route("/select", methods=["POST"])
def select():
    data = request.get_json()

    intent = data.get("intent")
    request_id = str(uuid.uuid4())

    #send the request to gemma4 on the VM
    safe_send(json.dumps({
        "request_id": request_id,
        "intent": intent
    }))

    #wait for the response
    timeout = 120
    start = time.time()

    result = None

    while time.time() - start < timeout:
        with responses_lock:
            if request_id in responses:
                result = responses.pop(request_id)
                break
        time.sleep(0.05)

    if result is None:
        return jsonify({"error": "VM timeout"}), 504

    #Text to speech generation.
    #For now the TTS is done on the server, which is not the right way. should return the audio files to the webpage for scalability
    generate_tts_audio(result["text"])
    

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