$ErrorActionPreference = "Stop"

Write-Host "Repairing Python virtual environment..." -ForegroundColor Cyan

if (Test-Path ".venv") {
    Write-Host "Removing existing .venv..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force ".venv"
}

$pythonCmd = $null
if (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonCmd = "py -3"
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
} else {
    throw "Python is not installed or not on PATH. Install Python 3.10+ first."
}

Write-Host "Creating .venv using $pythonCmd..." -ForegroundColor Cyan
Invoke-Expression "$pythonCmd -m venv .venv"

$venvPython = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    throw "Virtual environment created but $venvPython is missing. Reinstall Python from python.org and disable App Execution Alias for Python in Windows Settings."
}

Write-Host "Upgrading pip..." -ForegroundColor Cyan
& $venvPython -m pip install --upgrade pip wheel "setuptools<82"

if (Test-Path "requirements.txt") {
    Write-Host "Installing dependencies from requirements.txt..." -ForegroundColor Cyan
    & $venvPython -m pip install -r requirements.txt
}

Write-Host ""
Write-Host "Virtual environment is ready." -ForegroundColor Green
Write-Host "Activate it in PowerShell with:" -ForegroundColor Green
Write-Host "  .\.venv\Scripts\Activate.ps1"
Write-Host ""
Write-Host "If activation is blocked, run once in PowerShell:" -ForegroundColor Yellow
Write-Host "  Set-ExecutionPolicy -Scope CurrentUser RemoteSigned"
Write-Host ""
