# AI Interview System — Backend

FastAPI backend for interview sessions, answer scoring, candidate rankings and reports.
Frontend development is outside this repository's current scope.

```text
backend/
  app/
    __init__.py
    main.py
    database.py
    models.py
    schemas.py
    interview_engine.py
    scoring.py
    questions.json
  requirements.txt
  Dockerfile
  .dockerignore
docker-compose.yml
.env
.gitignore
README.md
```

## Local development

Run from the repository root with Python 3.10 or newer:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
cd backend
uvicorn app.main:app --reload
```

API documentation: http://127.0.0.1:8000/docs

The database defaults to `backend/interview.db`, independent of the working directory.
Set `DATABASE_URL` in the process environment to override it.
The existing database has been moved into `backend/` to preserve interview data.

## Docker

Set `BACKEND_PORT=8000` in the root `.env` file. On a fresh checkout, create
the database file before starting Compose:

```bash
touch backend/interview.db
docker compose up --build -d
```

Compose persists the database using the host file and caches the scoring model
in a named volume. The first startup downloads `all-MiniLM-L6-v2` and requires
internet access. Stop the service with `docker compose down`.
