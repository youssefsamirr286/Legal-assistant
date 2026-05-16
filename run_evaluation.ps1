$ErrorActionPreference = "Stop"

Write-Host "Preparing environment..." -ForegroundColor Cyan
powershell -ExecutionPolicy Bypass -File ".\fix_python_env.ps1"
if ($LASTEXITCODE -ne 0) {
    throw "Environment setup failed. Evaluation aborted."
}

Write-Host "Running capstone evaluation..." -ForegroundColor Green
& ".\.venv\Scripts\python.exe" "tests\evaluate_agent.py"

Write-Host ""
Write-Host "Done. Open:" -ForegroundColor Green
Write-Host " - tests\evaluation_results.json"
Write-Host " - tests\evaluation_report.md"
