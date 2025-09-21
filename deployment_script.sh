#!/bin/bash

set -e

echo "Deploying FastAPI application..."

# Pull latest changes
git pull origin main

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Restart the application
sudo systemctl restart fastapi-app

echo "Deployment completed successfully!"
