# HoopSight AI - Setup and Run Guide

This guide provides step-by-step instructions for setting up and running the complete HoopSight AI system, including both the Python backend (ML models) and the Next.js frontend.

---

## Prerequisites

- **Python 3.9+** (recommended: 3.11)
- **Node.js 18+** and **npm** (or yarn/pnpm)
- **Git** (for version control)
- **Windows PowerShell** (or your preferred terminal)

---

## Part 1: Python Backend Setup (ML Models & Data Processing)

### Step 1: Create Python Virtual Environment

Open PowerShell and navigate to the project root:

```powershell
cd C:\Users\adity\Downloads\Repositories\hoopsight-ai
```

Create a virtual environment:

```powershell
python -m venv venv
```

Activate the virtual environment:

```powershell
.\venv\Scripts\Activate.ps1
```

**Note:** If you encounter an execution policy error, run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try activating again.

### Step 2: Install Python Dependencies

Create a `requirements.txt` file in the project root if it doesn't exist:

```powershell
@"
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
beautifulsoup4>=4.12.0
requests>=2.31.0
nba-api>=1.4.0
python-dotenv>=1.0.0
lxml>=4.9.0
"@ | Out-File -FilePath requirements.txt -Encoding utf8
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

### Step 3: Set Up Environment Variables

Make sure you have the `.env` file in `Data_Gathering_&_Cleaning/`:

```powershell
# Check if .env exists
Test-Path .\Data_Gathering_&_Cleaning\.env
```

If it doesn't exist, create it:

```powershell
@"
GROQ_API_KEY=your_groq_api_key_here
"@ | Out-File -FilePath .\Data_Gathering_&_Cleaning\.env -Encoding utf8
```

### Step 4: Update Injury and Player Data

**Important:** Run this regularly (daily) to keep injury data fresh:

```powershell
cd Data_Gathering_&_Cleaning
python FetchInjuryAndExternalNews.py
```

This will:
- Fetch current NBA injuries from ESPN
- Scrape NBA news articles
- Calculate player scores with AI adjustments
- Generate `injuries.csv`, `individual_player_scores.csv`, and `team_player_scores.csv`

### Step 5: Train the Model and Generate Predictions

Navigate to the Models directory:

```powershell
cd ..\Models
python RandomForest.py
```

This will:
- Load historical team stats from `Cleaned_Data/`
- Load current season stats from `Current_Data/`
- Apply injury adjustments from `injuries.csv`
- Train the Random Forest model
- Generate predictions for all teams
- Fetch ESPN predictions for comparison
- Output files:
  - `Front/CSVFiles/prediction_results.csv` - Game-by-game predictions
  - `Front/CSVFiles/win_loss_records.csv` - Season win/loss projections
  - `Front/CSVFiles/prediction_history.json` - Full prediction archive with ESPN comparison

**Expected output:**
```
Loaded 108 injury records from C:\Users\adity\Downloads\Repositories\hoopsight-ai\Data_Gathering_&_Cleaning\injuries.csv
Loaded 521 player scores from C:\Users\adity\Downloads\Repositories\hoopsight-ai\Data_Gathering_&_Cleaning\individual_player_scores.csv
Training model...
Predicting outcomes for Atlanta...
Predicting outcomes for Boston...
...
Done!
```

### Step 6: Update Actual Game Results (After Games Complete)

After NBA games have been played, update the prediction history with actual results:

```powershell
python update_prediction_results.py
```

This will:
- Query NBA API for completed game scores
- Match them to predictions in `prediction_history.json`
- Calculate prediction accuracy
- Update the JSON with actual scores and outcomes

---

## Part 2: Frontend Setup (Next.js Website)

### Step 1: Install Node.js Dependencies

Open a **new PowerShell window** (keep Python venv active in the other one):

```powershell
cd C:\Users\adity\Downloads\Repositories\hoopsight-ai\frontend
npm install
```

Or if using yarn:

```powershell
yarn install
```

### Step 2: Set Up Frontend Environment Variables

Create a `.env.local` file in the `frontend/` directory if needed:

```powershell
@"
NEXT_PUBLIC_APP_URL=http://localhost:3000
"@ | Out-File -FilePath .env.local -Encoding utf8
```

### Step 3: Run the Development Server

```powershell
npm run dev
```

Or with yarn:

```powershell
yarn dev
```

The website will be available at: **http://localhost:3000**

### Step 4: Build for Production (Optional)

To create an optimized production build:

```powershell
npm run build
npm start
```

---

## Part 3: PHP Legacy Frontend (Optional)

If you want to run the older PHP-based frontend:

### Requirements:
- **PHP 7.4+**
- **Apache** or **XAMPP**

### Steps:

1. Copy the `Front/` directory to your web server's document root (e.g., `C:\xampp\htdocs\hoopsight`)

2. Access via browser:
   - **http://localhost/hoopsight/index.php**

3. The PHP pages will read from:
   - `Front/CSVFiles/prediction_results.csv`
   - `Front/CSVFiles/win_loss_records.csv`

---

## Daily Workflow

### Morning Routine (Before Games):

1. **Activate Python venv:**
   ```powershell
   cd C:\Users\adity\Downloads\Repositories\hoopsight-ai
   .\venv\Scripts\Activate.ps1
   ```

2. **Update injuries and player data:**
   ```powershell
   cd Data_Gathering_&_Cleaning
   python FetchInjuryAndExternalNews.py
   ```

3. **Generate fresh predictions:**
   ```powershell
   cd ..\Models
   python RandomForest.py
   ```

4. **Check frontend (new window):**
   ```powershell
   cd ..\frontend
   npm run dev
   ```
   Visit: http://localhost:3000/predictions

### Evening Routine (After Games Complete):

1. **Update actual results:**
   ```powershell
   cd C:\Users\adity\Downloads\Repositories\hoopsight-ai
   .\venv\Scripts\Activate.ps1
   cd Models
   python update_prediction_results.py
   ```

2. **Refresh frontend to see updated accuracy metrics**

---

## File Structure Overview

```
hoopsight-ai/
├── Data_Gathering_&_Cleaning/
│   ├── FetchInjuryAndExternalNews.py  # Fetch injuries & player scores
│   ├── injuries.csv                    # Current NBA injuries
│   ├── individual_player_scores.csv    # AI-adjusted player scores
│   └── team_player_scores.csv          # Team aggregate scores
│
├── Models/
│   ├── RandomForest.py                 # Main ML model (WITH INJURY INTEGRATION)
│   ├── injury_adjustments.py           # NEW: Injury HSS adjustment logic
│   ├── prediction_history.py           # Prediction archive manager
│   ├── espn_predictor.py               # ESPN data scraper
│   ├── update_prediction_results.py    # Result sync script
│   ├── config.py                       # Season config
│   └── team_mappings.py                # Team name normalization
│
├── Front/
│   ├── CSVFiles/
│   │   ├── prediction_results.csv      # OUTPUT: Game predictions
│   │   ├── win_loss_records.csv        # OUTPUT: Season records
│   │   └── prediction_history.json     # OUTPUT: Full archive
│   └── *.php                           # Legacy PHP frontend
│
├── frontend/                           # Next.js modern frontend
│   ├── src/
│   │   ├── app/[locale]/(unauth)/predictions/page.tsx  # Predictions page
│   │   └── locales/                    # Translations (en, fr)
│   ├── package.json
│   └── ...
│
├── Cleaned_Data/                       # Historical stats (2004-2024)
├── Current_Data/                       # 2025-26 season stats
├── Schedule/                           # Team schedules
└── venv/                              # Python virtual environment
```

---

## Troubleshooting

### Python Issues

**ModuleNotFoundError:**
```powershell
# Make sure venv is activated
.\venv\Scripts\Activate.ps1
# Reinstall dependencies
pip install -r requirements.txt
```

**CSV not found errors:**
- Ensure you ran `FetchInjuryAndExternalNews.py` first
- Check that `Data_Gathering_&_Cleaning/injuries.csv` exists

**No predictions generated:**
- Verify `Current_Data/` has stat folders (win_pct, efg_pct, etc.)
- Check `Schedule/` has CSV files for each team

### Frontend Issues

**Port 3000 already in use:**
```powershell
# Use different port
npm run dev -- -p 3001
```

**prediction_history.json not found:**
- Run `python Models/RandomForest.py` first to generate it

**Stale data on predictions page:**
- Hard refresh browser: Ctrl+Shift+R
- Restart dev server

---

## Key Features of Injury Integration

✅ **Automatic HSS Adjustment:** The model now subtracts player injury penalties from team HSS before making predictions

✅ **Date-Aware:** Checks if injured players will be back before game date

✅ **Status-Based Penalties:**
- **Out:** Full player score penalty
- **Day-To-Day:** 50% penalty (might play)

✅ **Scaling:** Injury penalties are scaled appropriately so major stars have bigger impact

✅ **Real-Time:** Uses latest injuries.csv from ESPN scraper

---

## Next Steps / Enhancements

1. **Automate Daily Updates:** Set up Windows Task Scheduler to run scripts automatically
2. **Deploy Frontend:** Host on Vercel/Netlify for public access
3. **API Endpoint:** Create REST API to serve predictions to mobile apps
4. **Enhanced Player Model:** Implement `PlayerModel.py` for deeper per-player predictions
5. **Historical Backtesting:** Validate injury adjustment accuracy on past seasons

---

## Support

For issues or questions:
- Check the repo: https://github.com/HoopSight-AI/hoopsight-ai
- Review code comments in `Models/injury_adjustments.py`
- Verify all CSV files in `Front/CSVFiles/` are recent

---

**Happy Predicting! 🏀📊**
