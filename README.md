# Antigravity Controller

Controller service for communication between Antigravity Agent and Mobile App.

## Features

- **REST API**: Command management, status queries, and history retrieval
- **WebSocket**: Real-time updates for agent status and task progress
- **JWT Authentication**: Secure token-based authentication
- **PostgreSQL**: Persistent storage for commands and results

## Tech Stack

- FastAPI + Uvicorn
- Pydantic v2
- SQLAlchemy (async)
- PostgreSQL
- python-jose (JWT)

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL database

### Installation

```bash
# Clone repository
cd antigravity-controller

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Configure environment
cp .env.example .env
# Edit .env with your database credentials
```

### Run Server

```bash
# Development mode
uvicorn controller.main:app --reload

# Production mode
uvicorn controller.main:app --host 0.0.0.0 --port 8000
```

### API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
src/controller/
├── main.py           # Application entry point
├── config.py         # Configuration management
├── api/              # REST API endpoints
├── websocket/        # WebSocket handlers
├── models/           # Pydantic models
├── db/               # Database layer
├── services/         # Business logic
└── auth/             # Authentication
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/v1/commands` | Create command |
| GET | `/api/v1/commands/{id}` | Get command |
| GET | `/api/v1/commands` | List commands |
| GET | `/api/v1/agent/status` | Agent status |
| WS | `/ws/v1/stream` | Real-time stream |

## License

Apache-2.0