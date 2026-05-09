from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO
import time
import uuid
import json
import threading

from src.ws import safe_send, responses, responses_lock, init_ws
from src.tts_service import generate_tts_audio

# -----------------------------
# INIT
# -----------------------------
init_ws()

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

lock = threading.Lock()


# -----------------------------
# WEB PAGE
# -----------------------------
@app.route("/")
def index():
    return render_template("index.html")


# -----------------------------
# MAIN API
# -----------------------------
@app.route("/select", methods=["POST"])
def select():
    data = request.get_json()

    intent = data.get("intent")
    request_id = str(uuid.uuid4())

    # -----------------------------
    # SEND TO VM (SAFE)
    # -----------------------------
    safe_send(json.dumps({
        "request_id": request_id,
        "intent": intent
    }))

    # -----------------------------
    # WAIT FOR RESPONSE (thread-safe)
    # -----------------------------
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

    # -----------------------------
    # TTS GENERATION
    # -----------------------------
    audio_file = generate_tts_audio(result["text"])
    audio_file.seek(0)

    # -----------------------------
    # RETURN AUDIO
    # -----------------------------
    return send_file(
        audio_file,
        mimetype="audio/wav",
        as_attachment=False
    )


# -----------------------------
# GAZE TRACKING (SocketIO)
# -----------------------------
@socketio.on("gaze_data")
def handle_gaze(data):
    x = data.get("x")
    y = data.get("y")

    print("Received gaze:", x, y)

    socketio.emit("cursor_move", {
        "x": x,
        "y": y
    })


# -----------------------------
# RUN SERVER
# -----------------------------
if __name__ == "__main__":
    socketio.run(app, host="127.0.0.1", port=5050, debug=True)