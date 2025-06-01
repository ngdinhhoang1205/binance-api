import json
import redis
import time
import os
# Connect to your Redis server (adjust host and port if needed)



class BinanceStreamHandler:
    def __init__(self, streams, key_map=None):
        self.streams = streams                      # e.g., ['btcusdt@aggTrade']
        self.key_map = key_map or {}                # Default: no mapping if None

    def on_message(self, ws, message):
        raw = json.loads(message)
        redis_host = os.getenv('REDIS_HOST', "host.docker.internal") # Default to localhost for local testing
        r = redis.Redis(host=redis_host, port=6379, decode_responses=True)
        # Handle combined vs direct stream format
        data = raw.get("data", raw)
        stream = raw.get("stream", "unknown")

        # Apply key mapping
        mapped = {self.key_map.get(k, k): v for k, v in data.items()}
        mapped["stream"] = stream  # Optional: include stream name
        for k, v in mapped.items():
            r.hset(f"agg_trade:{int(time.time())}", mapping={k: str(v) for k, v in mapped.items()})
        print(mapped)

    def on_error(self, ws, error):
        print("Error:", error)

    def on_close(self, ws, close_status_code, close_msg):
        print("Closed")

    def on_open(self, ws):
        payload = {
            "method": "SUBSCRIBE",
            "params": self.streams,
            "id": 1
        }
        ws.send(json.dumps(payload))
