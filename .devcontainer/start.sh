#!/bin/bash

# Quick Start Script for GitHub Codespaces
# Runs the AI JSON Prompt Generator API with proper Codespaces configuration

set -e

echo "🚀 Starting AI JSON Prompt Generator API in Codespaces..."

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from Codespaces template..."
    cp .devcontainer/.env.codespaces .env
    echo "✅ Created .env file with Codespaces defaults"
    echo "🔧 Edit .env to customize configuration: code .env"
fi

# Ensure Redis is running
echo "🔴 Checking Redis server..."
if ! redis-cli ping > /dev/null 2>&1; then
    echo "🔴 Starting Redis server..."
    redis-server --daemonize yes --port 6379
    sleep 2
fi

if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is running"
else
    echo "❌ Redis failed to start"
    exit 1
fi

# Create database tables if needed
echo "🗄️  Initializing database..."
python -c "
import sys
sys.path.append('src')
try:
    from models.database import Base, engine
    Base.metadata.create_all(bind=engine)
    print('✅ Database initialized')
except Exception as e:
    print(f'⚠️  Database initialization: {e}')
"

# Get Codespaces URL information
if [ ! -z "$CODESPACE_NAME" ] && [ ! -z "$GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN" ]; then
    API_URL="https://${CODESPACE_NAME}-8000.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
    DOCS_URL="https://${CODESPACE_NAME}-8000.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}/docs"
    
    echo ""
    echo "🌐 Your API will be available at:"
    echo "   API:  $API_URL"
    echo "   Docs: $DOCS_URL"
    echo ""
else
    echo ""
    echo "🌐 Running locally - API will be at http://localhost:8000"
    echo ""
fi

# Start the API server
echo "🚀 Starting FastAPI server..."
echo "   Press Ctrl+C to stop"
echo ""

# Run with proper Codespaces configuration
python main.py
