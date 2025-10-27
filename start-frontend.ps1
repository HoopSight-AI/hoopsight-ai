# HoopSight AI - Frontend Quick Start
# This script starts the Next.js development server

Write-Host "=== HoopSight AI - Frontend Quick Start ===" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the project root
if (-not (Test-Path ".\frontend\package.json")) {
    Write-Host "ERROR: Please run this script from the project root directory" -ForegroundColor Red
    Write-Host "Expected path: C:\Users\adity\Downloads\Repositories\hoopsight-ai" -ForegroundColor Yellow
    exit 1
}

# Navigate to frontend
Push-Location frontend

# Check for node_modules
if (-not (Test-Path ".\node_modules")) {
    Write-Host "[1/2] Installing npm dependencies (first time only)..." -ForegroundColor Yellow
    npm install
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "[1/2] Dependencies already installed" -ForegroundColor Green
}

# Start dev server
Write-Host "[2/2] Starting development server..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Frontend will be available at:" -ForegroundColor White
Write-Host "  http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

npm run dev

Pop-Location
