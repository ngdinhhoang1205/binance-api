# Binance Real-Time Market Data Stream

A data engineering portfolio project that connects to the Binance WebSocket API to stream real-time cryptocurrency market data. The project is containerized using Docker and is built with production readiness in mind.

---

## 📌 Features

- Connects to Binance WebSocket API
- Streams real-time cryptocurrency price data
- Containerized with Docker & orchestrated with Docker Compose
- Uses Supervisor for process monitoring
- Easy deployment and scalability
- (Optional) Exposes a web API or data visualization dashboard

---

## 📁 Project Structure
├── BinanceStreamHandler.py # Stream handler for Binance WebSocket
├── app.py # Main app logic (e.g., Web server or data processing entrypoint)
├── main.py # Alternate entry point
├── main.ipynb # Jupyter notebook for EDA or testing
├── Dockerfile # Docker image definition
├── docker-compose.yml # Docker orchestration
├── supervisord.conf # Process supervisor configuration
├── requirements.txt # Python dependencies
├── Frequently-Used-Commands.txt
└── READ.txt # Notes or logs

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
- Redis for DB
- Supervisor
