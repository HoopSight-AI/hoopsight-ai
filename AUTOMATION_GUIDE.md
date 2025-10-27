# 🤖 HoopSight AI - Automated Prediction System Guide

## Overview
This document explains how the automated daily prediction system works, ensuring predictions are generated fresh each day without overwriting historical data.

---

## 📅 Daily Workflow Schedule

**GitHub Actions runs at 6:00 AM EST (11:00 AM UTC) every day**

This timing ensures:
- Previous night's NBA games are finalized
- Fresh injury data is available
- Next day's predictions are generated before users wake up

---

## 🔄 Automated Process Flow

### Step 1: Fetch Current Injury Data
**File:** `Data_Gathering_&_Cleaning/FetchInjuryAndExternalNews.py`

**What it does:**
- Scrapes ESPN injury reports for all 30 NBA teams
- Fetches current player statistics from NBA API
- Uses Groq AI to analyze basketball news articles
- Calculates player impact scores based on:
  - Player efficiency metrics (PER, Usage%, Win Shares)
  - AI-detected momentum from news articles
  - Team context adjustments

**Outputs:**
- `injuries.csv` - Current injury status for all players
- `individual_player_scores.csv` - AI-adjusted player impact ratings
- `team_player_scores.csv` - Aggregated team strength from players

---

### Step 2: Update Actual Game Results
**File:** `Models/update_prediction_results.py`

**What it does:**
- Fetches actual scores from completed NBA games (up to 5 days back)
- Matches predictions with actual outcomes
- Calculates prediction accuracy metrics:
  - **Correct/Incorrect**: Did we pick the right winner?
  - **Margin Error**: How close was our projected margin?
  - **Alignment**: "Tight" (<3 pts error), "Moderate" (3-7 pts), "Wide" (>7 pts)

**Important:** This step ONLY updates games that are completed ("Final" status). It does NOT modify future predictions.

**Updates in `prediction_history.json`:**
```json
{
  "actual_home_score": 112,
  "actual_away_score": 108,
  "actual_winner": "Boston",
  "completed": true,
  "correct": true,
  "actual_margin": 4,
  "margin_error": 1.2,
  "alignment_bucket": "Tight"
}
```

---

### Step 3: Generate Next-Day Predictions
**File:** `Models/RandomForest.py`

**What it does:**
- Loads historical training data (2004-2025 seasons)
- Trains RandomForestRegressor on 15+ team statistics
- **CRITICAL:** Only predicts games for **tomorrow's date** (`current_date + 1 day`)
- Applies injury adjustments using fresh injury data from Step 1
- Fetches ESPN predictions for cross-validation

**Key Protection Logic:**
```python
# In RandomForest.py main()
current_date = date.today()
target_date = current_date + timedelta(days=1)  # Only predict tomorrow
prediction_history_manager.prune_before_date(target_date.isoformat())

# In predict_outcomes()
if game_date < current_date:
    continue  # Skip past games
if target_date is not None and game_date != target_date:
    continue  # Skip all games except target date
```

**Prevention of Overwriting:**
```python
# In prediction_history.py - upsert_prediction()
if existing and existing.completed:
    print(f"⚠️  Skipping prediction update for completed game")
    return  # DO NOT overwrite completed predictions
```

**Outputs:**
- `prediction_results.csv` - Game-by-game predictions for tomorrow
- `win_loss_records.csv` - Season-long win/loss projections
- `prediction_history.json` - Complete archive with metadata

---

## 🛡️ Data Integrity Safeguards

### 1. **No Overwriting Completed Games**
Once a game is marked `completed: true` in `prediction_history.json`, the prediction is **locked permanently**.

```python
if existing.completed:
    return  # Prediction is frozen forever
```

### 2. **Only Tomorrow's Games**
The `target_date` filter ensures only games scheduled for the next calendar day are predicted.

```python
target_date = current_date + timedelta(days=1)
prediction_history_manager.prune_before_date(target_date.isoformat())
```

This also **removes predictions older than tomorrow** from the CSV exports, keeping the dashboard clean.

### 3. **Preserving Existing Predictions**
If a prediction already exists for an upcoming game, the system:
- ✅ Updates HSS scores with fresh injury data
- ✅ Refreshes win percentages with latest model
- ❌ **Does NOT** overwrite `actual_home_score`, `actual_winner`, `completed`, etc.

### 4. **ESPN Cross-Validation**
ESPN predictions are fetched and stored separately, allowing post-game comparison:
- `espn_home_pct` / `espn_away_pct`
- `espn_alignment`: "Agree" or "Disagree" with HoopSight
- `espn_model_delta_pct`: Confidence gap between models

---

## 📊 CSV Export Logic

### `prediction_results.csv`
**Purpose:** Display in main predictions table (index.php)

**Filtering:**
- Only includes games **on or after tomorrow's date**
- Excludes completed games (they move to history)

**Columns:**
```csv
Team,Date,Tipoff (ET),Opponent,Location,Team HSS (Adj),Opponent HSS (Adj),Team Win %,Opponent Win %,Predicted Winner,Projected Margin (pts),Confidence Gap %,Team ESPN Win %,Opponent ESPN Win %
```

### `prediction_history.json`
**Purpose:** Complete historical archive for analytics

**Retention:**
- All predictions since start of season
- Both pending and completed games
- Full ESPN comparison data
- Actual results when available

**Never Deleted:** This file grows continuously throughout the season.

---

## 🔍 Example Timeline

### October 26, 2025 (Today)
**6:00 AM EST - GitHub Actions Runs:**

1. ✅ Fetch injuries for Oct 26
2. ✅ Update results for Oct 21-25 games (if available)
3. ✅ Generate predictions for **October 27 only**
4. ✅ Commit updates to repository

**Result:**
- `prediction_results.csv` contains only Oct 27 games
- Oct 26 predictions remain in `prediction_history.json` but are removed from CSV
- Oct 25 and earlier games have `completed: true` with actual scores

### October 27, 2025 (Tomorrow)
**6:00 AM EST - GitHub Actions Runs:**

1. ✅ Fetch injuries for Oct 27
2. ✅ Update results for Oct 22-26 games (Oct 26 predictions now have actual scores)
3. ✅ Generate predictions for **October 28 only**
4. ✅ Commit updates

**Result:**
- `prediction_results.csv` now shows Oct 28 games
- Oct 27 predictions move to history
- Oct 26 predictions are **permanently locked** with actual results

---

## 🧪 Manual Testing Commands

### Run Full Pipeline Locally
```powershell
# 1. Fetch injuries
cd Data_Gathering_&_Cleaning
python FetchInjuryAndExternalNews.py
cd ..

# 2. Update actual results
cd Models
python update_prediction_results.py

# 3. Generate predictions
python RandomForest.py
cd ..
```

### Test Specific Components
```powershell
# Test injury fetching only
python Data_Gathering_&_Cleaning/FetchInjuryAndExternalNews.py

# Test result updates only (without predictions)
python Models/update_prediction_results.py

# Generate predictions (will use existing injury data)
python Models/RandomForest.py
```

### Verify Data Integrity
```python
# Check prediction_history.json for completed games
import json
with open('Front/CSVFiles/prediction_history.json') as f:
    history = json.load(f)

completed = [p for p in history if p['completed']]
print(f"Completed games: {len(completed)}")

# Verify no completed games in prediction_results.csv
import pandas as pd
results = pd.read_csv('Front/CSVFiles/prediction_results.csv')
print(f"Active predictions: {len(results)}")
```

---

## 🚨 Troubleshooting

### Issue: Predictions Not Updating
**Check:**
1. GitHub Actions secrets (GROQ_API_KEY) are set
2. Workflow completed successfully (check Actions tab)
3. Git push succeeded (check commit history)

### Issue: Old Predictions Still Showing
**Cause:** `prune_before_date()` not running

**Fix:**
```python
# In RandomForest.py main()
target_date = current_date + timedelta(days=1)
prediction_history_manager.prune_before_date(target_date.isoformat())
```

### Issue: Completed Games Being Re-Predicted
**Cause:** Missing completed check

**Fix:** Ensure this code exists in `prediction_history.py`:
```python
if existing and existing.completed:
    print(f"⚠️  Skipping prediction update for completed game")
    return
```

---

## 📝 Key Configuration Variables

### `Models/config.py`
```python
CURRENT_SEASON = "2025-26"
CURRENT_SEASON_START_YEAR = 2025
MODEL_VERSION = "rf-1.1.0"
```

### `.github/workflows/update_predictions.yml`
```yaml
schedule:
  - cron: "0 11 * * *"  # 6:00 AM EST
```

---

## ✅ Data Flow Verification Checklist

- [ ] Injury data refreshes daily before predictions run
- [ ] Actual results update before new predictions generate
- [ ] Only tomorrow's games appear in `prediction_results.csv`
- [ ] Completed games have locked predictions in `prediction_history.json`
- [ ] ESPN predictions fetch for upcoming games
- [ ] Git commits include all CSV and JSON files
- [ ] No errors in GitHub Actions logs

---

## 📈 Metrics to Monitor

### Accuracy Tracking
- Overall prediction accuracy (% correct winners)
- Average margin error (pts difference)
- ESPN alignment rate (% agreement)
- Confidence calibration (High/Medium/Low buckets)

### Data Freshness
- Latest injury update timestamp
- Most recent prediction generation time
- Last actual result update date

---

## 🔗 Related Files

- **Workflow:** `.github/workflows/update_predictions.yml`
- **Prediction Engine:** `Models/RandomForest.py`
- **History Manager:** `Models/prediction_history.py`
- **Result Updater:** `Models/update_prediction_results.py`
- **Injury Fetcher:** `Data_Gathering_&_Cleaning/FetchInjuryAndExternalNews.py`
- **Configuration:** `Models/config.py`

---

**Last Updated:** October 26, 2025  
**System Status:** ✅ Fully Automated
