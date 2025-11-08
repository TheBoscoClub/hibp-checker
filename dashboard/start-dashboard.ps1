# HIBP Dashboard Startup Script for Windows
# PowerShell script to start the dashboard on Windows

Write-Host "HIBP Dashboard - Windows Startup" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python not found!" -ForegroundColor Red
    Write-Host "Please install Python from https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Check if Flask is installed
Write-Host "Checking for Flask..." -ForegroundColor Cyan
$flaskCheck = python -c "import flask; print('OK')" 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "Flask not installed. Installing..." -ForegroundColor Yellow
    pip install flask
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install Flask" -ForegroundColor Red
        exit 1
    }
    Write-Host "Flask installed successfully!" -ForegroundColor Green
} else {
    Write-Host "Flask is installed" -ForegroundColor Green
}

Write-Host ""
Write-Host "Starting HIBP Dashboard..." -ForegroundColor Cyan
Write-Host "Dashboard will be available at: http://127.0.0.1:5000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# Get script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Start the dashboard
Set-Location $scriptDir
python app.py
