$ErrorActionPreference = "Stop"

function Get-PythonExePath {
    $versions = @("-3.13", "-3.12", "-3.11", "-3.10", "-3")
    foreach ($v in $versions) {
        try {
            $path = & py $v -c "import sys; print(sys.executable)" 2>$null
            if ($path -and (Test-Path $path.Trim())) {
                return $path.Trim()
            }
        } catch {
            # Try next version
        }
    }

    try {
        $cmd = Get-Command python -ErrorAction Stop
        if ($cmd.Path -and (Test-Path $cmd.Path)) {
            return $cmd.Path
        }
    } catch {
        # Fall through to final error
    }

    throw "No usable Python executable found. Install Python 3.10+ from python.org and reopen terminal."
}

Write-Host "=== Python Environment Repair ===" -ForegroundColor Cyan

$venvPath = (Resolve-Path "." ).Path + "\.venv"
$activeVenv = $env:VIRTUAL_ENV
if ($activeVenv -and $activeVenv.TrimEnd('\') -eq $venvPath.TrimEnd('\')) {
    Write-Host "Detected active .venv in this terminal." -ForegroundColor Yellow
    Write-Host "Skipping full recreation to avoid deleting an active environment." -ForegroundColor Yellow
    Write-Host "Open a new terminal if you want a full rebuild." -ForegroundColor Yellow
}

$pythonExe = Get-PythonExePath
Write-Host "Using interpreter: $pythonExe" -ForegroundColor Green

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Cyan
    & $pythonExe -m venv .venv
}

$venvPython = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    throw "Failed to create .venv\Scripts\python.exe. Disable Windows Python App Execution Aliases and rerun."
}

Write-Host "Upgrading pip/setuptools/wheel..." -ForegroundColor Cyan
& $venvPython -m pip install --upgrade pip wheel "setuptools<82"

if (Test-Path "requirements.txt") {
    Write-Host "Installing requirements..." -ForegroundColor Cyan
    & $venvPython -m pip install -r requirements.txt
}

Write-Host "Verifying imports..." -ForegroundColor Cyan
& $venvPython -c "import langchain_core, langchain_community, langchain_text_splitters, langchain_google_genai, langchain_openai, tiktoken; import src.agent, src.retriever, src.ingest, src.prompts, src.llm_providers, src.classic_rag, src.security; print('OK: imports verified')"

Write-Host ""
Write-Host "SUCCESS: Environment is ready." -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Green
Write-Host "1) .\.venv\Scripts\Activate.ps1"
Write-Host "2) In VS Code/Cursor: Python: Select Interpreter -> .venv\\Scripts\\python.exe"
Write-Host ""
Write-Host "If Activate.ps1 is blocked, run once:" -ForegroundColor Yellow
Write-Host "Set-ExecutionPolicy -Scope CurrentUser RemoteSigned"
