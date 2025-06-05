import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template
from flask_socketio import SocketIO
import redis
import time
import threading
import os
import psycopg2
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

redis_host = os.getenv("REDIS_HOST", "host.docker.internal")  # Defaults to localhost if not set
r = redis.Redis(host=redis_host, port=6379, decode_responses=True)

PG_HOST = 'timescaledb'
PG_PORT = '5432'
PG_USER = 'joeynguyen'
PG_PASSWORD = 'joeynguyen'
PG_DB = 'binance-api'

@app.route("/")
def index():
    return render_template("index.html")

def redis_listener():
    """Background thread to continuously fetch latest Redis data and emit it."""
    last_key = None
    while True:
        print("Listening to Redis...")
        keys = sorted(r.keys("agg_trade:*"))
        if keys:
            print("Keys found:", keys[-1])
            latest_key = keys[-1]
            if latest_key != last_key:
                data = r.hgetall(latest_key)
                data["timestamp"] = latest_key.split(":")[-1]
                socketio.emit('update', data)
                print("Emitted data:", data)
                last_key = latest_key
        time.sleep(1)  # Adjust as needed


def connect_pg():
    return psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        dbname=PG_DB,
        user=PG_USER,
        password=PG_PASSWORD
    )

def mark_price_latest():
    """Fetch latest snapshot or summary from TimescaleDB."""
    while True:
        try:
            conn = connect_pg()
            cursor = conn.cursor()

            # Example query: get latest mark price per symbol
            cursor.execute("""
                SELECT *
                FROM mark_price_latest
                ;
            """)

            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            result = []
            for row in rows:
                row_dict = dict(zip(columns, row))

                # Convert datetime fields to ISO 8601 strings if present
                if 'event_time' in row_dict and isinstance(row_dict['event_time'], datetime):
                    row_dict['event_time'] = row_dict['event_time'].isoformat()

                if 'next_funding_time' in row_dict and isinstance(row_dict['next_funding_time'], datetime):
                    row_dict['next_funding_time'] = row_dict['next_funding_time'].isoformat()
                result.append(row_dict)
            socketio.emit('mark_price_latest', result)
            print("mark_price_latest data:", result)
            cursor.close()
            conn.close()
            # return result

        except Exception as e:
            print("Error fetching from TimescaleDB:", e)
            return []
        time.sleep(1)

@socketio.on('connect')
def handle_connect():
    print("Client connected")

if __name__ == "__main__":
    # Start the Redis listener thread
    thread = threading.Thread(target=redis_listener)
    thread.daemon = True
    thread.start()

    # Start TimescaleDB polling
    mark_price_thread = threading.Thread(target=mark_price_latest)
    mark_price_thread.daemon = True
    mark_price_thread.start()

    socketio.run(app, host='0.0.0.0', port=5000, debug=True)

