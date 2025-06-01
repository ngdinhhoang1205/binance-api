FROM python:3.12.4-slim

WORKDIR /app

# Install Python dependencies first
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# --- Install supervisord ---
RUN apt-get update && apt-get install -y supervisor && rm -rf /var/lib/apt/lists/*
# RUN pip install --no-cache-dir supervisor # Install supervisord

# Copy your project files
COPY . .
# Create a supervisord configuration file
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# CMD ["python", "app.py"]
CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
