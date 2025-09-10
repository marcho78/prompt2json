#!/bin/bash

# AI JSON Prompt Generator API - Codespaces Setup Script
# This script securely sets up the development environment using environment variables only

set -e

echo "🚀 Setting up AI JSON Prompt Generator API in Codespaces..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file from template if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
    
    echo ""
    echo "🔧 IMPORTANT: Please configure your .env file with proper values:"
    echo "   - Set a secure SECRET_KEY"
    echo "   - Configure database connection (SQLite works for development)"
    echo "   - Set Redis configuration"
    echo ""
    echo "📝 Edit .env file:"
    echo "   code .env"
    echo ""
else
    echo "✅ .env file already exists"
fi

# Create database directory if needed
echo "🗄️  Setting up database directory..."
mkdir -p data

# Set up git configuration for Codespaces
echo "🔧 Configuring git for Codespaces..."
git config --global --add safe.directory /workspaces/prompt2json

# Start Redis server
echo "🔴 Starting Redis server..."
redis-server --daemonize yes --port 6379

# Verify Redis is running
echo "✅ Verifying Redis connection..."
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is running successfully"
else
    echo "⚠️  Redis may not be running - check configuration"
fi

# Create test database tables (development only)
echo "🗄️  Setting up development database..."
python -c "
import os
import sys
sys.path.append('src')
from models.database import Base, engine
try:
    Base.metadata.create_all(bind=engine)
    print('✅ Database tables created successfully')
except Exception as e:
    print(f'⚠️  Database setup warning: {e}')
    print('This is normal if using environment-specific database settings')
"

echo ""
echo "🎉 Setup completed!"
echo ""
echo "🚀 To start the API server:"
echo "   python main.py"
echo ""
echo "🌐 The API will be available at:"
echo "   - Application: https://{CODESPACE_NAME}-8000.{GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
echo "   - Docs: https://{CODESPACE_NAME}-8000.{GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}/docs"
echo ""
echo "📖 For more information, see README.md and API_DOCUMENTATION.md"
echo ""
