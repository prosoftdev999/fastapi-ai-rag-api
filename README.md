# 🚀 FastAPI AI RAG API

A production-ready Retrieval-Augmented Generation (RAG) API built with FastAPI.

This project provides authentication, document upload, document chunking, vector embeddings, semantic retrieval, and AI-powered question answering using modern open-source components.

---

## Features

- JWT Authentication
- User Registration & Login
- Document Upload
- PDF/Text Extraction
- Automatic Text Chunking
- SentenceTransformer Embeddings
- pgvector Vector Search
- Semantic Retrieval
- AI Chat API
- PostgreSQL
- Redis
- Docker Support
- Alembic Migrations
- Ruff Formatting
- Pytest Test Suite

---

## Technology Stack

- FastAPI
- SQLAlchemy
- PostgreSQL
- pgvector
- Redis
- SentenceTransformers
- Transformers
- Ollama (optional)
- JWT Authentication
- Docker
- Alembic
- Pytest
- Ruff

---

## Project Structure

```
app/
├── api/
├── core/
├── db/
├── models/
├── schemas/
├── services/
├── utils/

tests/

alembic/
```

---

## Installation

Clone the repository

```bash
git clone https://github.com/prosoftdev999/fastapi-ai-rag-api.git

cd fastapi-ai-rag-api
```

Create virtual environment

```bash
python -m venv .venv

source .venv/bin/activate
```

Install packages

```bash
pip install -r requirements.txt
```

---

## Configure Environment

Copy

```bash
cp .env.example .env
```

Configure

```
DATABASE_URL=
REDIS_URL=

JWT_SECRET_KEY=

OPENAI_API_KEY=

OPENAI_MODEL=gpt-4.1-mini

EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
```

---

## Database

```bash
docker compose up -d

alembic upgrade head
```

---

## Run

```bash
uvicorn app.main:app --reload --port 8002
```

Swagger

```
http://localhost:8002/docs
```

---

## Tests

```bash
ruff format app tests alembic

ruff check app tests alembic

pytest -v
```

Expected

```
7 passed
```

---

## API Endpoints

Authentication

```
POST /api/v1/auth/register

POST /api/v1/auth/login
```

Documents

```
POST /api/v1/documents/upload

POST /api/v1/documents/{id}/process

GET /api/v1/documents
```

Chat

```
POST /api/v1/chat
```

---

## License

MIT License

---

## Author

Johan Bergman

GitHub

https://github.com/prosoftdev999