#!/bin/sh

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Check database migrations
alembic check
echo "Database migrations are successful"

# Start the application
echo "Starting the application..."
exec uvicorn src.main:app --host 0.0.0.0 --port 8000