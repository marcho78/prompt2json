# Dependency installation script for Windows PowerShell

Write-Host "Installing JSON2Prompt API Dependencies..." -ForegroundColor Green

# Activate virtual environment
& ".\venv\Scripts\Activate.ps1"

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies from requirements.txt
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-asyncio httpx black flake8

Write-Host "Dependencies installed successfully!" -ForegroundColor Green
Write-Host "Run './scripts/dev.ps1' to start the development server" -ForegroundColor Yellow
