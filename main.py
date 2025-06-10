# Libraries
import websocket
import json
import requests
import time
import os
import redis
import threading

# Base stream
base_url = 'wss://fstream.binance.com'
###############################################################################################################################################
# All Symbols
all_symbol_url = "https://fapi.binance.com/fapi/v1/exchangeInfo"
all_symbol_url_response = requests.get(all_symbol_url)
all_symbols = all_symbol_url_response.json()
all_symbols = [item['symbol'] for item in all_symbols['symbols']]
###############################################################################################################################################

# Combined streams
combined_streams = 'wss://fstream.binance.com/stream' # output {"stream":"<streamName>","data":<rawPayload>}
# Aggregate Trade Streams: The Aggregate Trade Streams push market trade information that is aggregated for fills with same price and taking side every 100 milliseconds. Only market trades will be aggregated, which means the insurance fund trades and ADL trades won't be aggregated.
agg_trade_str_name = '<symbol>@aggTrade'
# agg_trade_str processing
def agg_trade_socket():
  stream_list = ["btcusdt@aggTrade", "ethusdt@aggTrade"] # 2 most common symbols to show
  combined_stream_url = "wss://fstream.binance.com/stream?streams=" + "/".join(stream_list)
  agg_trade_keys_map = {
  "e": 'Event type',
  "E": 'Event time',
  "s": 'Symbol',
  "a": 'Aggregate trade ID',
  "p": 'Price',
  "q": 'Quantity',
  "f": 'First trade ID',
  "l": 'Last trade ID',
  "T": 'Trade time',
  "m": 'Is the buyer the market maker?',
  }
  def on_message(ws, message):
        raw = json.loads(message)
        redis_host = os.getenv('REDIS_HOST', "host.docker.internal") # Default to localhost for local testing
        r = redis.Redis(host=redis_host, port=6379, decode_responses=True)
        # Handle combined vs direct stream format
        data = raw.get("data", raw)
        stream = raw.get("stream", "unknown")
        # Apply key mapping
        mapped = {agg_trade_keys_map.get(k, k): v for k, v in data.items()}
        mapped["stream"] = stream  # Optional: include stream name
        # for k, v in mapped.items():
        # try:
        r.hset(f"agg_trade:{int(time.time())}", mapping={k: str(v) for k, v in mapped.items()})
        print(mapped)
        # except:
        #     print(f'ERROR, CLOSING...{mapped}')
        #     ws.close()

  def on_error(ws, error):
      print("Error:", error)

  def on_close(ws, close_status_code, close_msg):
      print("Closed")

  def on_open(ws):
      payload = {
          "method": "SUBSCRIBE",
          "params": stream_list,
          "id": 1
      }
      ws.send(json.dumps(payload))

  ws = websocket.WebSocketApp(
      combined_stream_url,
      on_message=on_message,
      on_error=on_error,
      on_close=on_close,
      on_open=on_open
  )
  ws.run_forever()
##############################################################################################################################################
def mark_price_socket():
  mark_price_stream_name = ['!markPrice@arr']
  mark_price_key_map = {
      "e": 'Event type',
      "E": 'Event time',
      "s": 'Symbol',
      "p": 'Mark price',
      "i": 'Index price',
      "P": 'Estimated Settle Price', # only useful in the last hour before the settlement starts
      "r": 'Funding rate',
      "T": 'Next funding time'
    }
  mark_price_url = "wss://fstream.binance.com/stream?streams=" + "/".join(mark_price_stream_name)

  def on_message(ws, message, key_map = mark_price_key_map):
      data = json.loads(message)['data']
      data_mapped = []
      redis_host = os.getenv('REDIS_HOST', "host.docker.internal") # Default to localhost for local testing
      r = redis.Redis(host=redis_host, port=6379, decode_responses=True)
      times_stamp = int(time.time())
      for i in data:
        mapped = {key_map.get(k, k): v for k, v in i.items()}
        data_mapped.append(mapped)
      for i in data_mapped:
        # data_db = (f'!markPrice@arr:{times_stamp}', mapping={k: str(v) for k, v in i.items()})
        try:
            r.hset(f'!markPrice@arr:{times_stamp}', mapping={k: str(v) for k, v in i.items()})
            print(i)
        except:
            print(f"ERROR, CLOSING {i}")
            ws.close()

  def on_error(ws, error):
      print("Error:", error)

  def on_close(ws, close_status_code, close_msg):
      print("Closed")

  def on_open(ws, stream_name = mark_price_stream_name):
      # Subscribe to BTC/USDT perpetual trades
      payload = {
          "method": "SUBSCRIBE",
          "params": stream_name,
          "id": 1
      }
      ws.send(json.dumps(payload))

  ws = websocket.WebSocketApp(
      combined_streams,
      on_message=on_message,
      on_error=on_error,
      on_close=on_close,
      on_open=on_open
  )
  ws.run_forever()

# Run threads
t1 = threading.Thread(target=agg_trade_socket, daemon=True)
t2 = threading.Thread(target=mark_price_socket, daemon=True)

t1.start()
t2.start()

# To allow cancel threads
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Interrupted by user. Exiting...")