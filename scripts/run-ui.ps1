$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
$venvPython = Join-Path $repoRoot '.venv\Scripts\python.exe'

if (-not (Test-Path $venvPython)) {
    throw 'Local virtual environment not found. Run scripts/bootstrap-ui.ps1 first.'
}

$env:PYTHONNOUSERSITE = '1'
Set-Location $repoRoot
$uiHost = if ($env:AELON_UI_HOST) { $env:AELON_UI_HOST } else { '127.0.0.1' }
$port = if ($env:AELON_UI_PORT) { $env:AELON_UI_PORT } else { '8010' }

& $venvPython -m uvicorn api.main:app --host $uiHost --port $port --reload
