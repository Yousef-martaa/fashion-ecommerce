# Backend

FastAPI backend for the fashion e-commerce platform.

See the [root README](../README.md) for full setup instructions.

## Structure

```
app/
  main.py      # FastAPI app instance and router registration
  api/         # route handlers
  core/        # settings, database session
  models/      # SQLAlchemy models (empty for now)
  schemas/     # Pydantic schemas (empty for now)
alembic/       # database migrations
```

## Development

```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
cp .env.example .env

uvicorn app.main:app --reload
```

Open [http://localhost:8000/health](http://localhost:8000/health) or [http://localhost:8000/docs](http://localhost:8000/docs).

## Migrations

```bash
alembic revision --autogenerate -m "message"
alembic upgrade head
```
