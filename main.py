# Libraries
import websocket
import json
import requests
import time
from BinanceStreamHandler import BinanceStreamHandler
###############################################################################################################################################
# Base stream
base_url = 'wss://fstream.binance.com'
# Combined streams
combined_streams = 'wss://fstream.binance.com/stream' # output {"stream":"<streamName>","data":<rawPayload>}
# Aggregate Trade Streams: The Aggregate Trade Streams push market trade information that is aggregated for fills with same price and taking side every 100 milliseconds. Only market trades will be aggregated, which means the insurance fund trades and ADL trades won't be aggregated.
agg_trade_str_name = '<symbol>@aggTrade'
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
###############################################################################################################################################
# agg_trade_str processing
stream_list = ["btcusdt@aggTrade", "ethusdt@aggTrade"]
handler = BinanceStreamHandler(streams=stream_list, key_map=agg_trade_keys_map)
combined_stream_url = "wss://fstream.binance.com/stream?streams=" + "/".join(stream_list)
ws = websocket.WebSocketApp(
    combined_stream_url,
    on_message=handler.on_message,
    on_error=handler.on_error,
    on_close=handler.on_close,
    on_open=handler.on_open
)
ws.run_forever()
