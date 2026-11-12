param([switch]$Lan)
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$python = Join-Path $PSScriptRoot 'backend/.venv/Scripts/python.exe'
$ollama = Join-Path $PSScriptRoot 'backend/tools/ollama/ollama.exe'
if (-not (Test-Path $ollama)) { $ollama = (Get-Command ollama -ErrorAction Stop).Source }
try { Invoke-RestMethod 'http://127.0.0.1:11434/api/tags' | Out-Null }
catch {
    New-Item -ItemType Directory -Force backend/data/logs | Out-Null
    Start-Process -FilePath $ollama -ArgumentList 'serve' -WindowStyle Hidden -RedirectStandardOutput 'backend/data/logs/ollama.out.log' -RedirectStandardError 'backend/data/logs/ollama.err.log'
    Start-Sleep -Seconds 3
}
if (-not (Test-Path 'frontend/dist/index.html')) {
    Push-Location frontend
    npm.cmd run build
    if ($LASTEXITCODE -ne 0) { throw 'Frontend build failed; run npm.cmd ci in frontend first.' }
    Pop-Location
}
Write-Host 'Open http://127.0.0.1:8000 after startup completes. Ctrl+C stops the app.'
$bindAddress = if ($Lan) { '0.0.0.0' } else { '127.0.0.1' }
if ($Lan) { Write-Host 'LAN mode: open http://<laptop-private-IP>:8000 from a device on the same Wi-Fi.' }
& $python -m uvicorn app.main:app --app-dir backend --host $bindAddress --port 8000
