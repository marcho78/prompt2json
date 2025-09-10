# Development server startup script for Windows PowerShell

Write-Host "Starting AI JSON Prompt Generator API Development Server..." -ForegroundColor Green

# Activate virtual environment
& ".\venv\Scripts\Activate.ps1"

# Create database tables
Write-Host "Initializing database..." -ForegroundColor Yellow
python -c "from src.models.database import create_tables; create_tables()"

# Start the server with hot reload
Write-Host "Starting server on http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "API Documentation: http://127.0.0.1:8000/docs" -ForegroundColor Cyan
uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload --log-level debug
