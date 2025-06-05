# Binance API Streamer and Dashboard

This project streams real-time market data from the Binance WebSocket API, stores it in TimescaleDB, and displays it in a live dashboard using Flask, Socket.IO, and JavaScript. Airflow is integrated for scheduled data operations and orchestration.

---

## 🚀 Features

- 📡 Real-time Binance Futures WebSocket stream
- 🛢️ Data storage in TimescaleDB (PostgreSQL extension)
- 📊 Live dashboard with WebSocket updates
- 🐳 Dockerized with `docker-compose`
- 📅 Apache Airflow integration for periodic tasks (ETL, snapshots, cleanup)

---

## 🧱 Tech Stack

- **Backend**: Python (Flask, Socket.IO)
- **Frontend**: HTML + JS
- **Database**: PostgreSQL + TimescaleDB
- **Scheduler**: Apache Airflow
- **Streaming**: Binance WebSocket
- **Deployment**: Docker & Docker Compose

---

## 📁 Project Structure
binance-api/
├── dags/ # Airflow DAGs
│ └── snapshot_dag.py # Example scheduled DAG
├── app.py # Flask app for the dashboard
├── stream/ # Binance stream handler
│ └── BinanceStreamHandler.py
├── db/ # TimescaleDB setup
│ └── init.sql
├── docker-compose.yml # Multi-container setup
├── Dockerfile # Flask app Dockerfile
├── airflow/ # Airflow configuration
│ ├── Dockerfile
│ └── requirements.txt
├── requirements.txt
└── README.md

---

## 🚀 Getting Started

### Prerequisites

Make sure you have the following installed:

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

### Clone the Repo

```bash
git clone https://github.com/ngdinhhoang1205/binance-api.git
cd binance-api

navigate to redis_to_timescaledb_etl.py, look for run_mark_price_latest_etl, the mounts=[], update the absolute paths source='D:\Projects\BinanceAPI\dbt_binance' and source='D:\Projects\BinanceAPI\dbt_binance/.dbt' to the one that matches your machine

### Build and Run with Docker Compose
docker-compose up --build
This will:
- Build the Docker image
- Start the streaming service
- Monitor processes using Supervisor

🧰 Technologies Used
- Python 3.x
- Binance WebSocket API
- Docker & Docker Compose
- Redis and timescaledb for DB
- Supervisor
- Airflow
- dbt
