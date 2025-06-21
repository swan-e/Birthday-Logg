#!/bin/bash

echo "Waiting for Postgres to be ready..."
while !nc -z db 5432; do
    sleep 0.5
done 
echo "Postgres is up!"

echo "Starting FastAPI app..."
uvicorn src.core.main:app --host 0.0.0.0 --port 8000