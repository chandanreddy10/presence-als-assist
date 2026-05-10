window.socket = io("http://127.0.0.1:5050", {
  transports: ["websocket", "polling"]
});