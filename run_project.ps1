$ErrorActionPreference = "Stop"

function Get-PythonCommand {
    $candidates = @(
        "py -3.13",
        "py -3.12",
        "py -3.11",
        "py -3.10",
        "py -3",
        "python"
    )

    foreach ($candidate in $candidates) {
        try {
            Invoke-Expression "$candidate --version" | Out-Null
            return $candidate
        } catch {
            # Try next candidate
        }
    }

    throw "No usable Python found. Install Python 3.10+ from python.org and reopen terminal."
}

Write-Host "=== Project Startup ===" -ForegroundColor Cyan

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    $pythonCmd = Get-PythonCommand
    Write-Host "Creating virtual environment with $pythonCmd..." -ForegroundColor Yellow
    Invoke-Expression "$pythonCmd -m venv .venv"
}

$venvPython = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    throw "Virtual environment is broken (.venv\Scripts\python.exe missing). Run .\fix_python_env.ps1"
}

Write-Host "Installing/updating dependencies..." -ForegroundColor Cyan
& $venvPython -m pip install -r requirements.txt

if (-not (Test-Path ".env")) {
    Write-Host "Creating .env template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
}

$hasContractsIndex = Test-Path "faiss_index\contracts"
$hasCaseLawIndex = Test-Path "faiss_index\case_law"
$hasContractsData = (Get-ChildItem "data\contracts\*.txt" -ErrorAction SilentlyContinue).Count -gt 0
$hasCaseLawData = (Get-ChildItem "data\case_law\*.txt" -ErrorAction SilentlyContinue).Count -gt 0

if ((-not $hasContractsIndex -or -not $hasCaseLawIndex) -and ($hasContractsData -or $hasCaseLawData)) {
    Write-Host "Building FAISS indexes (first run only)..." -ForegroundColor Cyan
    & $venvPython "src\ingest.py"
}

Write-Host "Starting Legal Agent..." -ForegroundColor Green
& $venvPython "src\agent.py"
