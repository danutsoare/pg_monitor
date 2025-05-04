#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.

echo "Building Docker images..."
docker compose build

echo "Starting services in detached mode..."
docker compose up -d

echo "Waiting for database service to initialize... (10 seconds)"
sleep 10

echo "Applying database migrations..."
docker compose exec backend alembic upgrade head

echo "Deployment complete! Current status:"
docker compose ps 