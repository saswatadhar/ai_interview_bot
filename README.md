# AI Interview System

Full-stack application for interview sessions, answer scoring, candidate rankings and reports.
Includes a FastAPI backend and a Next.js frontend.

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
frontend/
  app/
  public/
  package.json
  next.config.ts
  tsconfig.json
  Dockerfile
docker-compose.yml
.env
.gitignore
README.md
```
## Quick Setup

For the fastest way to get everything running via Docker:

```bash
cp env.example .env
chmod +x setup.sh
./setup.sh
```

This interactive script will configure your ports, set up the environment variables, initialize the database, and build/start all Docker containers.

## Local development

### Backend

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

### Frontend

Ensure you have Node.js v24 or newer installed:

```bash
cd frontend
cp env.example .env
npm install
npm run dev
```

The frontend application will be available at: http://localhost:3000

## Docker

Set `BACKEND_PORT=8000` and `FRONTEND_PORT=3000` in the root `.env` file. On a fresh checkout, create
the database file before starting Compose:

```bash
touch backend/interview.db
docker compose up --build -d
```

This will build and start both the backend and frontend servers.
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/docs

Compose persists the database using the host file and caches the scoring model
in a named volume. The first startup downloads `all-MiniLM-L6-v2` and requires
internet access. Stop the services with `docker compose down`.
