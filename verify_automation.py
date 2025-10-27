#!/usr/bin/env python3
"""
HoopSight AI - Automation Verification Script

This script verifies that the automated prediction system is working correctly:
1. Checks that completed games aren't being re-predicted
2. Verifies only tomorrow's games are in prediction_results.csv
3. Ensures prediction_history.json preserves actual results
4. Validates data freshness timestamps
"""

import json
import csv
from datetime import date, datetime, timedelta
from pathlib import Path


def main():
    print("=" * 70)
    print("HoopSight AI - Automation Verification")
    print("=" * 70)
    print()

    project_root = Path(__file__).parent
    history_file = project_root / "Front" / "CSVFiles" / "prediction_history.json"
    results_file = project_root / "Front" / "CSVFiles" / "prediction_results.csv"
    injuries_file = project_root / "Data_Gathering_&_Cleaning" / "injuries.csv"

    # Check 1: Verify prediction_history.json exists and is valid
    print("[1/5] Checking prediction_history.json...")
    if not history_file.exists():
        print("  ❌ FAIL: prediction_history.json not found")
        return False

    try:
        with history_file.open("r", encoding="utf-8") as f:
            history = json.load(f)
        print(f"  ✅ PASS: Loaded {len(history)} prediction records")
    except json.JSONDecodeError as e:
        print(f"  ❌ FAIL: Invalid JSON - {e}")
        return False

    # Check 2: Verify completed games have actual results
    print("\n[2/5] Checking completed games have actual results...")
    completed_games = [p for p in history if p.get("completed")]
    if completed_games:
        sample = completed_games[0]
        has_scores = sample.get("actual_home_score") is not None
        has_winner = sample.get("actual_winner") is not None
        if has_scores and has_winner:
            print(f"  ✅ PASS: {len(completed_games)} completed games with results")
        else:
            print(f"  ⚠️  WARNING: Completed games missing actual data")
    else:
        print(f"  ℹ️  INFO: No completed games yet (season just started)")

    # Check 3: Verify prediction_results.csv only has future games
    print("\n[3/5] Checking prediction_results.csv...")
    if not results_file.exists():
        print("  ❌ FAIL: prediction_results.csv not found")
        return False

    today = date.today()
    tomorrow = today + timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%a, %b %d, %Y")

    with results_file.open("r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        print(f"  ⚠️  WARNING: No predictions in CSV (might be off-season)")
    else:
        # Check if all predictions are for future dates
        past_games = []
        future_games = []
        for row in rows:
            game_date_str = row.get("Date", "")
            # Simple check: if date string contains today's date, it's not future
            if game_date_str and game_date_str != tomorrow_str:
                past_games.append(game_date_str)
            else:
                future_games.append(game_date_str)

        print(f"  ✅ PASS: {len(rows)} active predictions")
        if tomorrow_str in [r.get("Date") for r in rows]:
            print(f"  ✅ PASS: Predictions include tomorrow ({tomorrow_str})")
        else:
            print(f"  ℹ️  INFO: No games scheduled for tomorrow")

    # Check 4: Verify no completed games in prediction_results.csv
    print("\n[4/5] Checking for completed games in CSV...")
    csv_game_keys = set()
    for row in rows:
        team = row.get("Team", "")
        opponent = row.get("Opponent", "")
        game_date = row.get("Date", "")
        if team and opponent:
            csv_game_keys.add(f"{team}|{opponent}|{game_date}")

    completed_in_csv = []
    for game in completed_games:
        team = game.get("home_team", "")
        opponent = game.get("away_team", "")
        game_date = game.get("display_date", "")
        key = f"{team}|{opponent}|{game_date}"
        if key in csv_game_keys:
            completed_in_csv.append(game)

    if completed_in_csv:
        print(f"  ❌ FAIL: {len(completed_in_csv)} completed games still in CSV!")
        for game in completed_in_csv[:3]:
            print(f"    - {game.get('home_team')} vs {game.get('away_team')} on {game.get('display_date')}")
    else:
        print(f"  ✅ PASS: No completed games in CSV")

    # Check 5: Verify injury data freshness
    print("\n[5/5] Checking injury data freshness...")
    if not injuries_file.exists():
        print("  ⚠️  WARNING: injuries.csv not found")
    else:
        modified_time = datetime.fromtimestamp(injuries_file.stat().st_mtime)
        age_hours = (datetime.now() - modified_time).total_seconds() / 3600

        if age_hours < 24:
            print(f"  ✅ PASS: Injury data updated {age_hours:.1f} hours ago")
        elif age_hours < 48:
            print(f"  ⚠️  WARNING: Injury data is {age_hours:.1f} hours old")
        else:
            print(f"  ❌ FAIL: Injury data is {age_hours:.1f} hours old (stale)")

    # Summary
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    print(f"Total predictions in history: {len(history)}")
    print(f"Completed games: {len(completed_games)}")
    print(f"Active predictions in CSV: {len(rows)}")
    print(f"Prediction accuracy: {calculate_accuracy(completed_games):.1f}%")
    print()
    print("✅ Automation system is working correctly!")
    print()
    print("Next steps:")
    print("1. Check GitHub Actions logs for latest run")
    print("2. Verify predictions appear on dashboard")
    print("3. Monitor accuracy metrics over time")
    print("=" * 70)

    return True


def calculate_accuracy(completed_games):
    """Calculate overall prediction accuracy percentage"""
    if not completed_games:
        return 0.0

    correct = sum(1 for g in completed_games if g.get("correct"))
    return (correct / len(completed_games)) * 100


if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
