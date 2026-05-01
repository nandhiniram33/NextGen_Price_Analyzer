# Run production-like server using waitress
Set-Location "${PSScriptRoot}"
if (-not (Test-Path .venv)) {
    python -m venv .venv
}
. .venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:USE_WAITRESS = "1"
$env:PORT = "5000"
python app.py
