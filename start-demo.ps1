$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

docker info *> $null
if ($LASTEXITCODE -ne 0) {
    throw "Docker Desktop or the Docker Linux engine is not running. Start Docker Desktop, wait until it reports running, then retry."
}

docker compose up --build -d
if ($LASTEXITCODE -ne 0) {
    throw "FloodGuard containers could not be started. Run 'docker compose logs' for details."
}

Write-Host "FloodGuard frontend: http://localhost:5173"
Write-Host "FloodGuard API docs: http://localhost:8000/docs"
Start-Process "http://localhost:5173"
