# fashion-ecommerce

Modern full-stack fashion e-commerce platform with payments, order management, and multilingual support.

This repository is currently at the project-setup stage: frontend, backend, and database scaffolding only. No auth, product, or payment features have been implemented yet.

## Project structure

```
frontend/     Next.js (App Router, TypeScript) app
backend/      FastAPI app
  app/
    main.py     FastAPI app instance
    api/        route handlers (currently: /health)
    core/       settings and database session config
    models/     SQLAlchemy models (empty for now)
    schemas/    Pydantic schemas (empty for now)
  alembic/      database migrations
docs/         project documentation
docker-compose.yml
```

## Prerequisites

- [Node.js](https://nodejs.org/) 22+
- [Python](https://www.python.org/) 3.13+
- [PostgreSQL](https://www.postgresql.org/) 16+ (or use Docker)
- [Docker](https://www.docker.com/) and Docker Compose (optional, for containerized setup)

## Quick start with Docker

This brings up Postgres, the backend, and the frontend together:

```bash
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000 (health check at `/health`, docs at `/docs`)
- Postgres: localhost:5432

## Local development (without Docker)

### Frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Open http://localhost:3000.

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
cp .env.example .env
```

Update `DATABASE_URL` in `.env` to point at your local Postgres instance, then run:

```bash
uvicorn app.main:app --reload
```

Open http://localhost:8000/health or http://localhost:8000/docs.

### Database migrations

No tables exist yet. Once models are added under `backend/app/models/`, generate and apply migrations with:

```bash
alembic revision --autogenerate -m "message"
alembic upgrade head
```

## Environment variables

Each app has a `.env.example` describing the variables it needs:

- `frontend/.env.example`
- `backend/.env.example`

Copy each to `.env` in the same directory before running locally.
