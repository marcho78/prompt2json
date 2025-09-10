# Test runner script for Windows PowerShell

Write-Host "Running JSON2Prompt API Tests..." -ForegroundColor Green

# Activate virtual environment
& ".\venv\Scripts\Activate.ps1"

# Install pytest if not already installed
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/ -v --tb=short
