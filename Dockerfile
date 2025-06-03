FROM python:3.12.4-slim

WORKDIR /app

# Install system dependencies
COPY requirements.txt requirements.txt
RUN apt-get update && apt-get install -y \
    libpq-dev gcc libffi-dev libssl-dev \
    curl vim supervisor \
 && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --upgrade pip && \
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

# Supervisord config to run Airflow scheduler and webserver
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

