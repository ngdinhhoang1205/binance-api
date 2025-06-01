import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template
from flask_socketio import SocketIO
import redis
import time
import threading
import os



app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

redis_host = os.getenv("REDIS_HOST", "127.0.0.1")  # Defaults to localhost if not set
r = redis.Redis(host=redis_host, port=6379, decode_responses=True)

@app.route("/")
def index():
    return render_template("index.html")

def redis_listener():
    """Background thread to continuously fetch latest Redis data and emit it."""
    last_key = None
    while True:
        print("Listening to Redis...")
        keys = sorted(r.keys("agg_trade:*"))
        print("Keys found:", keys[-1])
        if keys:
            latest_key = keys[-1]
            if latest_key != last_key:
                data = r.hgetall(latest_key)
                data["timestamp"] = latest_key.split(":")[-1]
                socketio.emit('update', data)
                print("Emitted data:", data)
                last_key = latest_key
        time.sleep(1)  # Adjust as needed

@socketio.on('connect')
def handle_connect():
    print("Client connected")

if __name__ == "__main__":
    # Start the Redis listener thread
    thread = threading.Thread(target=redis_listener)
    thread.daemon = True
    thread.start()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
