# 🏀 HoopSight AI - Quick Reference

## TL;DR - Run Everything

### Option 1: PowerShell Scripts (Easiest)

```powershell
# 1. Backend (Python ML Model)
.\start-backend.ps1

# 2. Frontend (Next.js - in NEW terminal)
.\start-frontend.ps1
```

### Option 2: Manual Commands

**Backend:**
```powershell
.\venv\Scripts\Activate.ps1
cd Data_Gathering_&_Cleaning; python FetchInjuryAndExternalNews.py; cd ..
cd Models; python RandomForest.py; cd ..
```

**Frontend:**
```powershell
cd frontend
npm run dev
```

---

## 📁 Key Files & Outputs

| File | Purpose |
|------|---------|
| `Data_Gathering_&_Cleaning/injuries.csv` | **INPUT**: Current NBA injuries from ESPN |
| `Data_Gathering_&_Cleaning/individual_player_scores.csv` | **INPUT**: AI-adjusted player impact scores |
| `Models/injury_adjustments.py` | **NEW**: Injury HSS adjustment logic |
| `Front/CSVFiles/prediction_results.csv` | **OUTPUT**: Game-by-game predictions |
| `Front/CSVFiles/win_loss_records.csv` | **OUTPUT**: Season win/loss projections |
| `Front/CSVFiles/prediction_history.json` | **OUTPUT**: Full archive with ESPN comparison |

---

## 🩹 Injury Integration - How It Works

### Before (Old Model):
```python
team_hss = load_hss("Atlanta", data, 2025)  # Base HSS only
opponent_hss = load_hss("Boston", data, 2025)
weighted_stat = team_hss - opponent_hss
prediction = model.predict([[weighted_stat]])
```

### After (New Model with Injuries):
```python
team_hss = load_hss("Atlanta", data, 2025)  # Base HSS
opponent_hss = load_hss("Boston", data, 2025)

# NEW: Apply injury adjustments
injury_adjuster = get_injury_adjuster()
team_hss_adjusted, penalty = injury_adjuster.adjust_hss(
    "Atlanta", team_hss, game_date="2025-01-15"
)
opponent_hss_adjusted, opp_penalty = injury_adjuster.adjust_hss(
    "Boston", opponent_hss, game_date="2025-01-15"
)

weighted_stat = team_hss_adjusted - opponent_hss_adjusted
prediction = model.predict([[weighted_stat]])
```

### Penalty Calculation:
- **Out** = Full player score penalty (e.g., Trae Young = 150 pts → -7.5 HSS)
- **Day-to-Day** = 50% penalty (might play)
- **Scaling**: `penalty * 0.05` (5% of player score becomes HSS reduction)

### Example:
```
Atlanta Hawks without Trae Young (150 player_score):
  Base HSS: 145.2
  Injury Penalty: 150 * 0.05 = 7.5
  Adjusted HSS: 145.2 - 7.5 = 137.7
  
  Impact: Reduces win probability by ~5-10% against strong opponents
```

---

## 🔄 Daily Workflow

### Morning (Before Games):
```powershell
# 1. Activate Python
.\venv\Scripts\Activate.ps1

# 2. Update injuries
cd Data_Gathering_&_Cleaning
python FetchInjuryAndExternalNews.py

# 3. Generate predictions
cd ..\Models
python RandomForest.py

# 4. Check frontend
cd ..\frontend
npm run dev
# Visit: http://localhost:3000/predictions
```

### Evening (After Games):
```powershell
# Update actual results
.\venv\Scripts\Activate.ps1
cd Models
python update_prediction_results.py
```

---

## 🧪 Testing Injury Impact

### View Current Injuries:
```powershell
# See all injuries
Get-Content Data_Gathering_&_Cleaning\injuries.csv | Select-Object -First 20

# Count by team
Import-Csv Data_Gathering_&_Cleaning\injuries.csv | Group-Object team | Sort-Object Count -Descending
```

### Test Injury Adjuster:
```python
# In Python interactive shell:
from Models.injury_adjustments import InjuryAdjuster

adjuster = InjuryAdjuster()
penalty = adjuster.get_injury_penalty("Atlanta Hawks", "2025-01-15")
print(f"Atlanta injury penalty: {penalty}")

base_hss = 145.0
adjusted, pen = adjuster.adjust_hss("Atlanta Hawks", base_hss, "2025-01-15")
print(f"Base: {base_hss}, Adjusted: {adjusted}, Penalty: {pen}")
```

---

## 📊 Frontend Features

### Predictions Page (http://localhost:3000/predictions)

**Shows:**
- Team-by-team predictions
- Win/Loss records with HSS
- ESPN comparison metrics
- Confidence buckets (High/Medium/Low)
- Actual results after games complete

**Localization:**
- English: `/en/predictions`
- French: `/fr/predictions`

---

## 🐛 Common Issues

### Python Issues

**"ModuleNotFoundError: No module named 'X'"**
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**"FileNotFoundError: injuries.csv"**
```powershell
cd Data_Gathering_&_Cleaning
python FetchInjuryAndExternalNews.py
```

**No injury adjustments applied:**
- Check `injuries.csv` has data
- Verify team names match (e.g., "Atlanta Hawks" vs "Atlanta")
- Look for console output: "Loaded X injury records"

### Frontend Issues

**Port 3000 in use:**
```powershell
npm run dev -- -p 3001
```

**Stale predictions:**
- Hard refresh: Ctrl+Shift+R
- Re-run `python Models/RandomForest.py`

**prediction_history.json missing:**
```powershell
cd Models
python RandomForest.py
```

---

## 🔍 Verify Injury Integration is Working

### Look for these console outputs when running RandomForest.py:

```
Loaded 108 injury records from C:\...\injuries.csv
Loaded 521 player scores from C:\...\individual_player_scores.csv
```

### Check predictions have different HSS values:

Before (without injuries):
```csv
Team,Opponent,HSS Home,HSS Away,Win%
Atlanta,Boston,145.23000,148.56000,48.32
```

After (with injuries):
```csv
Team,Opponent,HSS Home,HSS Away,Win%
Atlanta,Boston,137.73000,148.56000,42.15
```
*(Note: Atlanta's HSS dropped due to Trae Young injury)*

---

## 📚 Full Documentation

See `SETUP_AND_RUN.md` for comprehensive setup instructions.

---

## 🎯 What Changed - Summary

### New Files:
1. **Models/injury_adjustments.py** - Core injury logic
2. **requirements.txt** - Python dependencies
3. **SETUP_AND_RUN.md** - Detailed setup guide
4. **start-backend.ps1** - Automated backend runner
5. **start-frontend.ps1** - Automated frontend runner

### Modified Files:
1. **Models/RandomForest.py**:
   - Imports `get_injury_adjuster()`
   - Calls `adjust_hss()` for both teams before prediction
   - Uses adjusted HSS values in all calculations

### How to Confirm Integration:
```powershell
# Search for injury adjuster usage
Select-String -Path .\Models\RandomForest.py -Pattern "injury_adjuster"
# Should show multiple matches
```

---

**🏀 Happy Predicting with Injury-Aware Intelligence!**
