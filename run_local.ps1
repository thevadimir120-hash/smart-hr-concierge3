$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example - edit it and run again."
    exit 1
}

New-Item -ItemType Directory -Force -Path "data", "data\images" | Out-Null

Write-Host "Installing dependencies..."
python -m pip install -r requirements.txt

Write-Host "Checking environment..."
python scripts/check_env.py

Write-Host "Starting Smart HR Concierge..."
python main.py
