#!/bin/bash

# Deployment script for doc_processor

set -e

echo "🚀 Starting deployment..."

# Check if .env.prod exists
if [ ! -f .env.prod ]; then
    echo "❌ .env.prod file not found. Please create it from .env.prod template"
    exit 1
fi

# Build and start services
echo "🔨 Building Docker images..."
docker-compose -f docker-compose.prod.yml build --no-cache

echo "🏃 Starting services..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Run migrations
echo "🗃️ Running database migrations..."
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Collect static files
echo "📦 Collecting static files..."
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

echo "✅ Deployment complete!"
echo "🌐 Application is running at http://localhost"
echo "📊 ChromaDB is available at http://localhost:8001"

# Show running containers
docker-compose -f docker-compose.prod.yml ps