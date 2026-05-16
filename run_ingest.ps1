$ErrorActionPreference = "Stop"

Write-Host "Building FAISS indexes from data/ ..." -ForegroundColor Cyan

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    throw "Virtual environment missing. Run .\fix_python_env.ps1 first."
}

& ".\.venv\Scripts\python.exe" "src\ingest.py"
Write-Host "Ingest complete." -ForegroundColor Green
