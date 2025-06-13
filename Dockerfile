# FROM python:3.12.4-slim

# WORKDIR /app

# # Install system dependencies
# COPY requirements.txt requirements.txt
# RUN apt-get update && apt-get install -y \
#     libpq-dev gcc libffi-dev libssl-dev \
#     curl vim supervisor \
#  && rm -rf /var/lib/apt/lists/*

# # Install Python dependencies
# RUN pip install --upgrade pip && \
#     pip install docker && \
#     pip install -r requirements.txt

# # Set Airflow environment variables
# ENV AIRFLOW_HOME=/app/airflow
# ENV AIRFLOW__CORE__LOAD_EXAMPLES=False
# ENV AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=sqlite:////app/airflow/airflow.db

# # Copy your project
# COPY . .

# # Initialize the Airflow DB
# RUN airflow db init

# # Optionally create an Airflow admin user (skip if already created)
# RUN airflow users create \
#     --username admin \
#     --password admin \
#     --firstname Airflow \
#     --lastname Admin \
#     --role Admin \
#     --email admin@example.com

# # Supervisord config to run Airflow scheduler and webserver
# COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

FROM python:3.12.4-slim

WORKDIR /app

# Install system dependencies (including ngrok support)
COPY requirements.txt requirements.txt
RUN apt-get update && apt-get install -y \
    libpq-dev gcc libffi-dev libssl-dev \
    curl vim supervisor gnupg2 \
 && curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null \
 && echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | tee /etc/apt/sources.list.d/ngrok.list \
 && apt-get update && apt-get install -y ngrok \
 && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install docker && \
    pip install -r requirements.txt

# Set Airflow environment variables
ENV AIRFLOW_HOME=/app/airflow
ENV AIRFLOW__CORE__LOAD_EXAMPLES=False
ENV AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=sqlite:////app/airflow/airflow.db

# Copy your project
COPY . .

# Initialize the Airflow DB
RUN airflow db init

# Optionally create an Airflow admin user (skip if already created)
RUN airflow users create \
    --username admin \
    --password admin \
    --firstname Airflow \
    --lastname Admin \
    --role Admin \
    --email admin@example.com

# Set your ngrok authtoken here or through ENV in docker run
ENV NGROK_AUTHTOKEN=2yPlDQAH0fqQ7hO8iHplZE66Sod_5bq99LM1oktdqty2VTNPK

# Copy supervisord config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Copy the ngrok startup script
COPY ngrok_setup.sh /app/ngrok_setup.sh
RUN chmod +x /app/ngrok_setup.sh

# Entry point: Start both Airflow and ngrok via supervisord
# CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
CMD ["/bin/bash", "/app/ngrok_setup.sh"]

