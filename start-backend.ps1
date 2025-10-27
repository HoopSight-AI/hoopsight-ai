# HoopSight AI - Quick Start Script
# This script sets up and runs the Python backend

Write-Host "=== HoopSight AI - Python Backend Quick Start ===" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the project root
if (-not (Test-Path ".\Models\RandomForest.py")) {
    Write-Host "ERROR: Please run this script from the project root directory" -ForegroundColor Red
    Write-Host "Expected path: C:\Users\adity\Downloads\Repositories\hoopsight-ai" -ForegroundColor Yellow
    exit 1
}

# Step 1: Check Python
Write-Host "[1/6] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python not found. Please install Python 3.9+" -ForegroundColor Red
    exit 1
}

# Step 2: Create/Activate venv
Write-Host "[2/6] Setting up virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path ".\venv")) {
    Write-Host "  Creating new venv..." -ForegroundColor Gray
    python -m venv venv
}

Write-Host "  Activating venv..." -ForegroundColor Gray
& .\venv\Scripts\Activate.ps1

# Step 3: Install dependencies
Write-Host "[3/6] Installing Python dependencies..." -ForegroundColor Yellow
pip install -q --upgrade pip
pip install -q -r requirements.txt
Write-Host "Dependencies installed" -ForegroundColor Green

# Step 4: Fetch injuries and player data
Write-Host "[4/6] Fetching current injuries and player data..." -ForegroundColor Yellow
Push-Location "Data_Gathering_&_Cleaning"
python FetchInjuryAndExternalNews.py
$injurySuccess = $LASTEXITCODE -eq 0
Pop-Location

if ($injurySuccess) {
    Write-Host "Injury data updated" -ForegroundColor Green
} else {
    Write-Host "Warning: Injury fetch had issues (continuing anyway)" -ForegroundColor Yellow
}

# Step 5: Train model and generate predictions
Write-Host "[5/6] Training model and generating predictions..." -ForegroundColor Yellow
Write-Host "  This may take 1-2 minutes..." -ForegroundColor Gray
Push-Location Models
python RandomForest.py
$modelSuccess = $LASTEXITCODE -eq 0
Pop-Location

if ($modelSuccess) {
    Write-Host "Predictions generated successfully!" -ForegroundColor Green
} else {
    Write-Host "Model training failed" -ForegroundColor Red
    exit 1
}

# Step 6: Summary
Write-Host ""
Write-Host "=== Setup Complete! ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Generated files:" -ForegroundColor White
Write-Host "  - Front/CSVFiles/prediction_results.csv" -ForegroundColor Gray
Write-Host "  - Front/CSVFiles/win_loss_records.csv" -ForegroundColor Gray
Write-Host "  - Front/CSVFiles/prediction_history.json" -ForegroundColor Gray
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "  1. Review predictions in Front/CSVFiles/" -ForegroundColor Gray
Write-Host "  2. Start frontend: cd frontend; npm run dev" -ForegroundColor Gray
Write-Host "  3. After games: python Models/update_prediction_results.py" -ForegroundColor Gray
Write-Host ""
Write-Host "View full instructions: SETUP_AND_RUN.md" -ForegroundColor Yellow
Write-Host ""
