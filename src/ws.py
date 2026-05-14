import websocket
import json
import threading
import time

#The VM URL
VM_WS_URL = "ws://35.185.60.59:8000/ws"

ws = None
connected = False

# shared response store (thread-safe)
responses = {}
responses_lock = threading.Lock()

# send safety lock
send_lock = threading.Lock()


def safe_send(message: str):
    global ws

    with send_lock:
        if ws and connected:
            try:
                ws.send(message)
            except Exception as e:
                print("WS send failed:", e)
        else:
            print("WS not connected, cannot send")


def on_open(wsapp):
    global connected
    connected = True
    print("✅ VM WebSocket connected")


def on_message(wsapp, message):
    print("VM RAW:", message)

    try:
        data = json.loads(message)
        request_id = data.get("request_id")

        if request_id:
            with responses_lock:
                responses[request_id] = data

    except Exception as e:
        print("Parse error:", e)


def on_error(wsapp, error):
    print("WS error:", error)


def on_close(wsapp, close_status_code, close_msg):
    global connected
    connected = False
    print("❌ VM WebSocket closed")


def start_ws():
    global ws

    ws = websocket.WebSocketApp(
        VM_WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )

    ws.run_forever()


def init_ws():
    thread = threading.Thread(target=start_ws, daemon=True)
    thread.start()

    timeout = 5
    start = time.time()

    while not connected and time.time() - start < timeout:
        time.sleep(0.1)

    if not connected:
        print("❌ WebSocket NOT connected to VM")
    else:
        print("✅ WebSocket ready")