import os
import csv
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional

from sklearn.ensemble import RandomForestRegressor

from DataStore import DataStore
from config import (
    CURRENT_SEASON,
    CURRENT_SEASON_START_YEAR,
    CURRENT_DATA_ROOT,
    HISTORICAL_DATA_ROOT,
    PREDICTION_RESULTS_CSV,
    SCHEDULE_ROOT,
    WIN_LOSS_RECORD_CSV,
)
from espn_predictor import EspnPrediction, fetch_espn_prediction
from injury_adjustments import get_injury_adjuster
from prediction_history import PredictionHistoryManager
from team_mappings import get_team_identity

# Global variables to mimic static fields in Java
data_store = None
prediction_writer = None
prediction_csv_writer = None
win_loss_writer = None
prediction_history_manager: Optional[PredictionHistoryManager] = None

def load_training_data(cleaned_data_path):
    """
    Loads training data from CSV files in the provided directory (and sub-directories).
    - WeightedStat is the feature (X)
    - WinPercentage is the target (y)
    Returns (X, y) for training.
    """
    X = []
    y = []

    global data_store
    if data_store is None:
        data_store = DataStore(30)

    team_index = 0

    cleaned_path = Path(cleaned_data_path)
    if not cleaned_path.exists():
        raise ValueError(f"Directory not found: {cleaned_data_path}")

    for stat_folder in cleaned_path.iterdir():
        if stat_folder.is_dir():
            for team_file in stat_folder.glob("*.csv"):
                team = team_file.stem

                if team_index < 30 and team not in data_store.team_index_map:
                    data_store.add_team_to_index_map(team, team_index)
                    team_index += 1

                with team_file.open("r", encoding="utf-8-sig") as handle:
                    reader = csv.reader(handle)
                    next(reader, None)  # Skip header
                    for row in reader:
                        if len(row) >= 4:
                            try:
                                weighted_stat = float(row[1].strip())
                                win_percentage = float(row[3].strip())
                                X.append([weighted_stat])
                                y.append(win_percentage)
                            except (ValueError, IndexError) as exc:
                                print(f"Error processing row in {team_file}: {exc}")
                                continue

    if not X:
        raise ValueError(f"No training data loaded from {cleaned_data_path}")
        
    return X, y


def normalize_game_date(raw_date: str):
    """Return the cleaned display string, ISO date, and season year for a game."""
    cleaned = raw_date.strip().strip('"')
    try:
        parsed = datetime.strptime(cleaned, "%a, %b %d, %Y")
    except ValueError:
        fallback = f"{cleaned}, {CURRENT_SEASON_START_YEAR}"
        parsed = datetime.strptime(fallback, "%a, %b %d, %Y")
    return cleaned, parsed.date().isoformat(), parsed.year

def predict_outcomes(
    team_name,
    schedule_path,
    historical_data_path,
    model,
    current_date,
    history_manager=None,
    target_date: Optional[date] = None,
):
    """
    Predicts outcomes for each game in 'schedule_path' using the trained Random Forest model.
    Writes results to 'prediction_results.csv' and aggregated W/L to 'win_loss_records.csv'.
    """
    if history_manager is None:
        history_manager = prediction_history_manager

    # create file writer objects to write game-by-game predictions, final predicted win-loss records
    global prediction_writer, prediction_csv_writer, win_loss_writer, data_store
    if prediction_writer is None:
        prediction_writer = PREDICTION_RESULTS_CSV.open("w", encoding="utf-8-sig", newline="")
        prediction_csv_writer = csv.writer(prediction_writer)
        prediction_csv_writer.writerow([
            "Team",
            "Date",
            "Tipoff (ET)",
            "Opponent",
            "Location",
            "Team HSS (Adj)",
            "Opponent HSS (Adj)",
            "Team Win %",
            "Opponent Win %",
            "Predicted Winner",
            "Projected Margin (pts)",
            "Confidence Gap %",
            "Team ESPN Win %",
            "Opponent ESPN Win %",
        ])
    if win_loss_writer is None:
        win_loss_writer = WIN_LOSS_RECORD_CSV.open("w", encoding="utf-8-sig", newline="")
        win_loss_writer.write("Team,Wins,Losses,HSS\n")

    # if we can't find the team's schedule, break the program
    schedule_path = Path(schedule_path)
    if not schedule_path.exists():
        print(f"Schedule file not found for {team_name}: {schedule_path}")
        return

    # Read the schedule CSV, convert into Game objects
    games = []
    with schedule_path.open("r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        # Skip header if present
        next(reader, None)
        for row in reader:
            # Expecting something like: [date, ???, opponent, location, ...]
            if len(row) < 4:
                continue
            raw_date = row[0].strip()
            start_time = row[1].strip() if len(row) > 1 else ""
            opponent = row[2].strip()
            location = row[3].strip()

            display_date, iso_date, year = normalize_game_date(raw_date)
            if year == 0:
                year = CURRENT_SEASON_START_YEAR
            games.append(Game(display_date, iso_date, start_time, opponent, location, year))

    # Prepare an Instances-like structure in Python
    # We'll only store WeightedStat as X
    win_count = 0
    loss_count = 0
    hss_sum = 0.0

    # Initialize injury adjuster
    injury_adjuster = get_injury_adjuster()

    predicted_games = 0

    for game in games:
        try:
            game_date = datetime.strptime(game.iso_date, "%Y-%m-%d").date()
        except ValueError:
            continue

        if game_date < current_date:
            continue
        if target_date is not None and game_date != target_date:
            continue

        team_hss = load_hss(team_name, historical_data_path, game.year)
        hss_sum += team_hss
        opponent_hss = load_hss(game.opponent, historical_data_path, game.year)
        predicted_games += 1
        display_index = predicted_games

        # Apply injury adjustments
        team_hss_adjusted, team_injury_penalty = injury_adjuster.adjust_hss(
            team_name, team_hss, game.iso_date
        )
        opponent_hss_adjusted, opp_injury_penalty = injury_adjuster.adjust_hss(
            game.opponent, opponent_hss, game.iso_date
        )

        # If home, add a home advantage to the adjusted HSS
        if game.location == "H":
            # Scales with opponent strength. 2.75 is a min boost, or 1.425% of the awayHSS
            home_advantage_boost = max(2.75, opponent_hss_adjusted * 0.01425)
            team_hss_adjusted += home_advantage_boost

        weighted_stat = team_hss_adjusted - opponent_hss_adjusted
        predicted_win_percentage = model.predict([[weighted_stat]])[0]
        team_win_pct = predicted_win_percentage * 100
        opponent_win_pct = 100 - team_win_pct

        if predicted_win_percentage > 0.5:
            predicted_winner = team_name
        elif predicted_win_percentage < 0.5:
            predicted_winner = game.opponent
        else:
            predicted_winner = team_name if game.location == "H" else game.opponent

        predicted_winner_pct = team_win_pct if predicted_winner == team_name else opponent_win_pct
        confidence_gap_pct = abs(team_win_pct - 50.0)
        expected_margin = round(confidence_gap_pct * 0.4, 2)

        location_code = (game.location or "").upper()
        team_location = location_code if location_code in {"H", "A"} else "N"

        if location_code == "H":
            home_team = team_name
            away_team = game.opponent
            team_is_home = True
        elif location_code == "A":
            home_team = game.opponent
            away_team = team_name
            team_is_home = False
        else:
            ordered = sorted([team_name, game.opponent])
            home_team, away_team = ordered[0], ordered[1]
            team_is_home = team_name == home_team
            location_code = "N"

        if team_is_home:
            home_hss_value = team_hss_adjusted
            away_hss_value = opponent_hss_adjusted
        else:
            home_hss_value = opponent_hss_adjusted
            away_hss_value = team_hss_adjusted

        home_model_pct = team_win_pct if team_is_home else opponent_win_pct
        away_model_pct = 100.0 - home_model_pct

        espn_snapshot: Optional[EspnPrediction] = None
        espn_home_pct: Optional[float] = None
        espn_away_pct: Optional[float] = None
        espn_favorite_full: Optional[str] = None
        espn_favorite_abbr: Optional[str] = None
        espn_confidence_gap: Optional[float] = None

        if location_code in {"H", "A"}:
            try:
                _, home_abbr = get_team_identity(home_team)
                _, away_abbr = get_team_identity(away_team)
            except KeyError:
                pass
            else:
                espn_snapshot = fetch_espn_prediction(game.iso_date, home_abbr, away_abbr)
                if espn_snapshot is not None:
                    espn_home_pct = espn_snapshot.home_pct
                    espn_away_pct = espn_snapshot.away_pct
                    espn_favorite_full = espn_snapshot.favorite_full
                    espn_favorite_abbr = espn_snapshot.favorite_abbr
                    espn_confidence_gap = espn_snapshot.confidence_gap

        should_log = history_manager is not None and team_is_home

        if should_log:
            history_manager.upsert_prediction(
                display_date=game.display_date,
                iso_date=game.iso_date,
                home_team=home_team,
                away_team=away_team,
                location=location_code,
                predicted_winner=predicted_winner,
                predicted_win_pct=predicted_winner_pct,
                home_hss=home_hss_value,
                away_hss=away_hss_value,
                tipoff_et=game.start_time,
                model_home_pct=home_model_pct,
                model_away_pct=away_model_pct,
            )

            if espn_snapshot is not None:
                history_manager.update_espn_prediction(
                    iso_date=game.iso_date,
                    home_team=home_team,
                    away_team=away_team,
                    game_id=espn_snapshot.game_id,
                    source_url=espn_snapshot.source_url,
                    home_pct=espn_home_pct,
                    away_pct=espn_away_pct,
                    favorite_full=espn_favorite_full,
                    favorite_abbr=espn_favorite_abbr,
                    confidence_gap=espn_confidence_gap,
                )

        team_espn_pct = espn_home_pct if team_is_home else espn_away_pct
        opponent_espn_pct = espn_away_pct if team_is_home else espn_home_pct

        # Add result to data_store
        data_store.add_game_result(
            f"Game #{display_index}: {team_name} vs {game.opponent}, Winner: {predicted_winner}, "
            f"HoopSight Win%: {team_win_pct:.2f}/{opponent_win_pct:.2f}, Projected Margin: {expected_margin:.2f}"
        )

        def _fmt_pct(value: Optional[float]) -> str:
            return f"{value:.2f}" if value is not None else "N/A"

        prediction_csv_writer.writerow(
            [
                team_name,
                game.display_date,
                game.start_time,
                game.opponent,
                team_location,
                f"{team_hss_adjusted:.5f}",
                f"{opponent_hss_adjusted:.5f}",
                f"{team_win_pct:.2f}",
                f"{opponent_win_pct:.2f}",
                predicted_winner,
                f"{expected_margin:.2f}",
                f"{confidence_gap_pct:.2f}",
                _fmt_pct(team_espn_pct),
                _fmt_pct(opponent_espn_pct),
            ]
        )

        # Update head-to-head in data_store
        current_team_index = get_team_index(team_name)
        opponent_team_index = get_team_index(game.opponent)
        if predicted_winner == team_name:
            data_store.update_head_to_head(current_team_index, opponent_team_index, 1)
            data_store.update_head_to_head(opponent_team_index, current_team_index, 0)
            win_count += 1
        else:
            data_store.update_head_to_head(current_team_index, opponent_team_index, 0)
            data_store.update_head_to_head(opponent_team_index, current_team_index, 1)
            loss_count += 1

        # Print outcome to console
        print_outcomes(
            display_index,
            team_name,
            game.opponent,
            team_hss,
            opponent_hss,
            team_win_pct,
            opponent_win_pct,
            predicted_winner,
            expected_margin,
        )

    # Finally, write W/L record
    if predicted_games == 0:
        return

    avgHSS = (hss_sum / predicted_games) if predicted_games else 0.0
    win_loss_writer.write(f"{team_name},{win_count},{loss_count},{avgHSS:.5f}\n")

def get_team_index(team_name):
    """
    Retrieves a team's index from the Data_Store.
    """
    return data_store.get_team_index(team_name)

def load_hss(team, data_path, year):
    """
    Loads HoopSight Strength (HSS) for a given team and year:
    1. Checks `../Current_Data` for the exact year or most recent past year.
    2. Falls back to historical data in `data_path` if no current data is found.
    Returns the total WeightedStat (HSS) for the team.
    """
    current_data_dir = Path(CURRENT_DATA_ROOT)
    historical_data_dir = Path(data_path)

    total_stat = 0.0
    stat_count = 0

    # process a CSV file and sum stats
    def process_file(file_path, year_filter=None):
        nonlocal total_stat, stat_count
        with Path(file_path).open("r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            next(reader, None)  # Skip header
            for row in reader:
                # Stat files are formatted as Rank,Statistic,Year,Win Percentage
                if len(row) > 2:
                    try:
                        stat_year = int(row[2].strip())
                        if year_filter is None or stat_year == year_filter:
                            stat_value = float(row[1].strip())
                            total_stat += stat_value
                            stat_count += 1
                    except (ValueError, IndexError):
                        continue

    # 1. Check Current Data for the exact year
    if current_data_dir.exists() and current_data_dir.is_dir():
        for folder in current_data_dir.iterdir():
            if folder.is_dir():
                team_file = folder / f"{team}.csv"
                if team_file.exists():
                    process_file(team_file, year_filter=year)

    # If no stats found for the exact year, check most recent past year in current data
    if stat_count == 0 and current_data_dir.exists():
        for folder in current_data_dir.iterdir():
            if folder.is_dir():
                team_file = folder / f"{team}.csv"
                if team_file.exists():
                    process_file(team_file)

    # 2. Check Historical Data if no stats found in Current Data
    if stat_count == 0 and historical_data_dir.exists() and historical_data_dir.is_dir():
        for folder in historical_data_dir.iterdir():
            if folder.is_dir():
                team_file = folder / f"{team}.csv"
                if team_file.exists():
                    process_file(team_file, year_filter=year)

    # Compute HSS
    if stat_count > 0:
        hss = total_stat / stat_count
        print(f"HSS for team: {team}, Year: {year} = {hss}")
        return hss
    else:
        print(f"No stats found for team: {team}, Year: {year}")
        return 0.0

def print_outcomes(
    game_number,
    team,
    opponent_team,
    team_hss,
    opponent_hss,
    team_win_pct,
    opponent_win_pct,
    predicted_winner,
    expected_margin,
):
    """
    Prints outcomes of each game prediction, mimicking the Java 'System.out.printf' style.
    """
    BOLD = "\033[1m"
    RESET = "\033[0m"
    print(f"{BOLD}GAME #{game_number}: {RESET}{team} vs {opponent_team}")
    print(f"HSS {team}: {team_hss:.5f}")
    print(f"HSS {opponent_team}: {opponent_hss:.5f}")
    print(
        f"HoopSight Win % -> {team}: {team_win_pct:.2f}% | {opponent_team}: {opponent_win_pct:.2f}%"
    )
    print(f"Projected Margin: {expected_margin:.2f} pts")
    print(f"Predicted Winner: {predicted_winner}\n")

def query_wins_and_losses(data_store):
    """
    Queries the user for two teams, then prints their head-to-head record.
    """
    team1 = input("Enter the name of the first team: ").strip()
    team2 = input("Enter the name of the second team: ").strip()

    team_1_index = data_store.get_team_index(team1)
    team_2_index = data_store.get_team_index(team2)

    if team_1_index == -1 or team_2_index == -1:
        print("One or both team names are invalid.")
        return

    wins_against = data_store.get_head_to_head_result(team_1_index, team_2_index)
    losses_against = data_store.get_head_to_head_result(team_2_index, team_1_index)

    print(f"{team1} vs {team2}:")
    print(f"{team1} wins: {wins_against}")
    print(f"{team1} losses: {losses_against}")

def main():
    global data_store, prediction_writer, win_loss_writer, prediction_history_manager

    data_store = DataStore(30)
    schedule_path = SCHEDULE_ROOT
    historical_data_path = HISTORICAL_DATA_ROOT
    current_date = date.today()
    prediction_history_manager = PredictionHistoryManager(CURRENT_SEASON)
    target_date = current_date + timedelta(days=1)
    prediction_history_manager.prune_before_date(target_date.isoformat())

    # 1) Load training data
    X, y = load_training_data(historical_data_path)

    # 2) Train RandomForestRegressor
    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(X, y)

    # 3) Run predictions for every known team
    teams_list = data_store.get_teams_list()
    for team in teams_list:
        team_schedule_file = Path(schedule_path) / team / f"{team}.csv"
        predict_outcomes(
            team,
            team_schedule_file,
            historical_data_path,
            rf,
            current_date,
            prediction_history_manager,
            target_date=target_date,
        )

    # Close CSV writers if open
    if prediction_writer is not None:
        prediction_writer.flush()
        prediction_writer.close()
    if win_loss_writer is not None:
        win_loss_writer.flush()
        win_loss_writer.close()

    prediction_history_manager.save()

    # 4) Read back the 'win_loss_records.csv' and print
    if WIN_LOSS_RECORD_CSV.exists():
        with WIN_LOSS_RECORD_CSV.open("r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            next(reader, None)  # skip header
            for row in reader:
                if len(row) < 4:
                    continue
                team = row[0].strip()
                wins = row[1].strip()
                losses = row[2].strip()
                hss = row[3].strip()
                print(f"{team} had a predicted record of {wins}-{losses} and a HoopSight Strength Score of {hss}")

#Python class to represent game details
class Game:
    def __init__(self, display_date, iso_date, start_time, opponent, location, year):
        self.display_date = display_date
        self.iso_date = iso_date
        self.start_time = start_time
        self.opponent = opponent
        self.location = location.upper() if location else ""
        self.year = year
        self.result = None

    def set_result(self, result):
        self.result = result

if __name__ == "__main__":
    main()
