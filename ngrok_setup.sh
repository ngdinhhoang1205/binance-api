#!/bin/bash

set -e  # Exit on any error
echo "Starting Flask app..."
python app.py &

sleep 3
echo "Starting ngrok..."
ngrok config add-authtoken "$NGROK_AUTHTOKEN"
ngrok http 5000 > /dev/null &

# Wait for ngrok tunnel to be ready
echo "Waiting for ngrok to be ready..."
NGROK_URL=""
until [[ $NGROK_URL == https* ]]; do
    NGROK_URL=$(curl -s http://localhost:4040/api/tunnels \
                 | grep -o 'https://[a-zA-Z0-9.-]*\.ngrok.io' | head -n 1)
    sleep 1
done

echo "NGROK_URL detected: $NGROK_URL"
echo "$NGROK_URL" > /app/public_url.txt
ls -l /app/public_url.txt
cat /app/public_url.txt

wait  # keep both processes running
