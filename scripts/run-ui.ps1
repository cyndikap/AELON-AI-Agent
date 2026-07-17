$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
$uiPath = Join-Path $repoRoot 'ui'
$venvPython = Join-Path $repoRoot '.venv\Scripts\python.exe'

if (-not (Test-Path $venvPython)) {
    throw 'Local virtual environment not found. Run scripts/bootstrap-ui.ps1 first.'
}

$env:PYTHONNOUSERSITE = '1'
Set-Location $uiPath
& $venvPython -m streamlit run app.py
