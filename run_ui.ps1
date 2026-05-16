$ErrorActionPreference = "Stop"

Write-Host "Starting Legal Assistant UI..." -ForegroundColor Cyan
Write-Host "Preparing environment..." -ForegroundColor Yellow

powershell -ExecutionPolicy Bypass -File ".\fix_python_env.ps1"
if ($LASTEXITCODE -ne 0) {
    throw "Environment setup failed. UI launch aborted."
}

Write-Host "Launching Streamlit UI..." -ForegroundColor Green
& ".\.venv\Scripts\python.exe" -m streamlit run "ui_app.py"
