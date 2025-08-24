# Azercelli Chatbot Backend

This is the **FastAPI backend** for the Azercelli Chatbot, which integrates with **AWS Bedrock** for large language model (LLM) interactions and a knowledge base retrieval system. It supports streaming responses for chat applications and can be deployed via Docker or on a self-hosted server.

---

## Features

- **Chat endpoint**: `/chat` accepts user queries and streams LLM-generated answers.
- **Knowledge Base integration**: Retrieves Azercell corporate policies, ethics, code of conduct, and CEO messages.
- **Streaming support**: Supports real-time response streaming.
- **Health check endpoint**: `/health` for monitoring the backend.
- Fully compatible with **multi-session chatbot frontends**.

---

## Technology Stack

- **Python 3.12** with `uv` environment
- **FastAPI** for API endpoints
- **Boto3** for AWS Bedrock interactions
- **AWS Bedrock** LLM models
- **StreamingResponse** for incremental outputs
- **Environment variables** for secure secret management

---


## 🏗️ Architecture

### Application Structure

```
├── main.py                # FastAPI application entry point
├── cli.py                 # # Core logic: Bedrock client, knowledge base retrieval, streaming
├── Dockerfile             # Container build instructions
├── pyproject.toml         # UV project configuration & dependencies
├── uv.lock                # Locked dependency versions
└── README.md              # This file
```


## 🐳 Docker Setup

This backend API is fully containerized and designed to work as part of a Docker Compose stack.

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

The backend is part of a larger Docker Compose application:

```bash
# Run the entire stack
docker-compose up -d

# View logs
docker-compose logs backend

# Stop the stack
docker-compose down
```

The API will be available at `http://localhost:8000`

### Option 2: Standalone Docker

```bash
# Build the backend image
docker build -t dataminds-backend .

# Run the container
docker run -p 8000:8000 \
  -e HOST=0.0.0.0 \
  -e PORT=8000 \
  dataminds-backend
```

### Option 3: Local Development

For local development without Docker:

```bash
# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Run the application
uv run uvicorn main:app --reload
```



### Docker Compose Integration

```yaml
# Example docker-compose.yml snippet
services:
  backend:
    build:
      context: .
      dockerfile: backend/Dockerfile
    networks:
      - safe_networks
    restart: always
    image: backend
    container_name: backend
    volumes:
      - ./backend:/app
      - backend_venv:/app/.venv
    ports:
      - "8000:8000"
```

### CORS Configuration

The API is configured to accept requests from any origin:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```