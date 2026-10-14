#!/bin/bash

echo "==============================="
echo "   AI Interview Bot Setup"
echo "==============================="
echo ""

# 1. Prompt for Public IP/Domain
read -p "Enter your Server IP or Domain (e.g., 192.168.1.100 or mydomain.com): " SERVER_HOST
if [ -z "$SERVER_HOST" ]; then
    SERVER_HOST="localhost"
fi

# 2. Prompt for ports with defaults
read -p "Enter Frontend Port [default 3000]: " FRONTEND_PORT
FRONTEND_PORT=${FRONTEND_PORT:-3000}

read -p "Enter Backend Port [default 8000]: " BACKEND_PORT
BACKEND_PORT=${BACKEND_PORT:-8000}

echo ""
# Preserve an existing API key without displaying it.
GEMINI_API_KEY=$(sed -n 's/^GEMINI_API_KEY=//p' backend/.env 2>/dev/null | head -n 1)
if [ -z "$GEMINI_API_KEY" ]; then
    read -r -s -p "Enter Gemini API key: " GEMINI_API_KEY
    echo ""
fi
GEMINI_MODEL=${GEMINI_MODEL:-gemini-2.5-flash}

echo "Generating root .env..."
cat > .env <<EOF
GEMINI_API_KEY=${GEMINI_API_KEY}
GEMINI_MODEL=${GEMINI_MODEL}
BACKEND_PORT=${BACKEND_PORT}
FRONTEND_PORT=${FRONTEND_PORT}
CORS_ORIGINS=http://${SERVER_HOST}:${FRONTEND_PORT},http://127.0.0.1:${FRONTEND_PORT},http://localhost:${FRONTEND_PORT}
EOF

echo "Generating frontend/.env..."
cat > frontend/.env <<EOF
NEXT_PUBLIC_API_URL=http://${SERVER_HOST}:${BACKEND_PORT}
EOF

echo "Setting up database..."
touch backend/interview.db

echo "Copying root .env to backend for Docker..."
cp .env backend/.env
chmod 600 .env backend/.env

echo "Stopping any exisiting containers..."
docker compose down

echo "Starting Docker containers..."
docker compose up --build -d

echo ""
echo "==============================="
echo "   Setup Complete!"
echo "==============================="
echo "Frontend is running at: http://${SERVER_HOST}:${FRONTEND_PORT}"
echo "Backend API is at:      http://${SERVER_HOST}:${BACKEND_PORT}/docs"
