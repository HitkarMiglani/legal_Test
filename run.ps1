# Run both Flask backend and Streamlit frontend
# This script starts both servers in separate processes

Write-Host "Starting LuminaryAI..." -ForegroundColor Cyan

# Check if virtual environment is activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & ".\env\Scripts\Activate.ps1"
}

Write-Host "`nStarting Flask backend..." -ForegroundColor Yellow
$backend = Start-Process -FilePath "python" -ArgumentList "app.py" -PassThru -NoNewWindow

Start-Sleep -Seconds 2

Write-Host "Starting Streamlit frontend..." -ForegroundColor Yellow
$frontend = Start-Process -FilePath "streamlit" -ArgumentList "run", "main.py" -PassThru -NoNewWindow

Write-Host "`nLuminaryAI is running!" -ForegroundColor Green
Write-Host "   Backend: http://localhost:5000" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:8501" -ForegroundColor Cyan
Write-Host "`nPress Ctrl+C to stop both servers" -ForegroundColor Yellow

try {
    # Wait for user to stop
    while ($true) {
        Start-Sleep -Seconds 1
    }
}
finally {
    Write-Host "`nStopping servers..." -ForegroundColor Red
    Stop-Process -Id $backend.Id -Force -ErrorAction SilentlyContinue
    Stop-Process -Id $frontend.Id -Force -ErrorAction SilentlyContinue
    Write-Host "Servers stopped" -ForegroundColor Green
}
