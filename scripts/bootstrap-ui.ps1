$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
$venvPython = Join-Path $repoRoot '.venv\Scripts\python.exe'

if (-not (Test-Path $venvPython)) {
    Write-Host 'Creating local virtual environment...'
    python -m venv (Join-Path $repoRoot '.venv')
}

Write-Host 'Upgrading pip in local virtual environment...'
& $venvPython -m ensurepip --upgrade
& $venvPython -m pip install --upgrade pip

Write-Host 'Installing project dependencies...'
& $venvPython -m pip install -r (Join-Path $repoRoot 'requirements.txt')

Write-Host 'Installing spaCy language models...'
& $venvPython -m spacy download en_core_web_sm
& $venvPython -m spacy download fr_core_news_sm

Write-Host 'Environment is ready.'
