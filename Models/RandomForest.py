import os
import csv
from sklearn.ensemble import RandomForestRegressor
from DataStore import DataStore
from datetime import date, datetime

# Global variables to mimic static fields in Java
data_store = None
prediction_writer = None
win_loss_writer = None

def load_training_data(cleaned_data_path):
    """
    Loads training data from CSV files in the provided directory (and sub-directories).
    - WeightedStat is the feature (X)
    - WinPercentage is the target (y)
    Returns (X, y) for training.
    """
    X = []
    y = []

    # Prepare the data_store if it hasn't been initialized
    global data_store
    if data_store is None:
        data_store = DataStore(30)

    team_index = 0
    # Traverse the 'cleaned_data_path' directory
    for stat_folder in os.listdir(cleaned_data_path):
        stat_folder_path = os.path.join(cleaned_data_path, stat_folder)
        if os.path.isdir(stat_folder):
            for team_file in os.listdir(stat_folder_path):
                if team_file.endswith(".csv"):
                    file_path = os.path.join(stat_folder_path, team_file)
                    team = team_file.split(".")[0]
                    # Map the team to an index if we have space
                    if team_index < 30 and team not in data_store.team_index_map:
                        data_store.add_team_to_index_map(team, team_index)
                        team_index += 1

                    # Read the CSV
                    with open(file_path, "r", encoding="utf-8-sig") as f:
                        reader = csv.reader(f)
                        # Skip header
                        next(reader, None)
                        for row in reader:
                            # 0 -> rank, 1 -> weighted stat, 2 -> year, 3 -> win percentage
                            if len(row) < 4:
                                continue
                            weighted_stat = float(row[1].strip())
                            win_percentage = float(row[3].strip())
                            X.append([weighted_stat])
                            y.append(win_percentage)
    return X, y

def predict_outcomes(team_name, schedule_path, historical_data_path, model, current_date):
    """
    Predicts outcomes for each game in 'schedule_path' using the trained Random Forest model.
    Writes results to 'prediction_results.csv' and aggregated W/L to 'win_loss_records.csv'.
    """

    # create file writer objects to write game-by-game predictions, final predicted win-loss records
    global prediction_writer, win_loss_writer, data_store
    if prediction_writer is None:
        prediction_writer = open("../Front/CSVFiles/prediction_results.csv", "w", encoding="utf-8-sig", newline="")
        prediction_writer.write("Date,Team,Opponent,HSS Home,HSS Away,Win%\n")
    if win_loss_writer is None:
        win_loss_writer = open("../Front/CSVFiles/win_loss_records.csv", "w", encoding="utf-8-sig", newline="")
        win_loss_writer.write("Team,Wins,Losses,HSS\n")

    # if we can't find the team's schedule, break the program
    if not os.path.exists(schedule_path):
        print(f"Schedule file not found for {team_name}: {schedule_path}")
        return

    # Read the schedule CSV, convert into Game objects
    games = []
    with open(schedule_path, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        # Skip header if present
        next(reader, None)
        for row in reader:
            # Expecting something like: [date, ???, opponent, location, ...]
            if len(row) < 4:
                continue
            date = row[0].strip()
            opponent = row[2].strip()
            location = row[3].strip()

            # Dates are formatted as Day, Month Date, Year
            date_parts = date.split(",")
            year = 0
            if len(date_parts) > 2:
                try:
                    year = int(date_parts[2].strip())
                except:
                    year = 0
            games.append(Game(date, opponent, location, year))

    # Prepare an Instances-like structure in Python
    # We'll only store WeightedStat as X
    win_count = 0
    loss_count = 0
    hss_sum = 0.0

    for i, game in enumerate(games):
        
        """
        # make sure the game being evaluted has not already happened
        gameDate = datetime.strptime(game.date, '%a, %b %d, %Y').date()
        if gameDate < currentDate:
            
            continue
        """

        team_hss = load_hss(team_name, historical_data_path, game.year)
        hss_sum += team_hss
        opponent_hss = load_hss(game.opponent, historical_data_path, game.year)

        # If home, add a home advantage
        if game.location == "H":
            # Scales with opponent strength. 2.75 is a min boost, or 1.425% of the awayHSS
            home_advantage_boost = max(2.75, opponent_hss * 0.01425)
            team_hss += home_advantage_boost

        weighted_stat = team_hss - opponent_hss
        # Model expects [ [WeightedStat], ... ]
        # TODO: #This is a single float. we'll need to add mor features and information to the model. This is why predictions are not as accurate as they could be.
            
        predicted_win_percentage = model.predict([[weighted_stat]])[0]  # single float

        if predicted_win_percentage > 0.5:
            predicted_winner = team_name
        elif predicted_win_percentage < 0.5:
            predicted_winner = game.opponent
        else:
            # tie-breaker if 0.5
            predicted_winner = team_name if game.location == "H" else game.opponent

        # Add result to data_store
        data_store.add_game_result(f"Game #{i+1}: {team_name} vs {game.opponent}, Winner: {predicted_winner}")

        # Write row to prediction file
        prediction_writer.write(f"{team_name},{game.opponent},{team_hss:.5f},{opponent_hss:.5f},{predicted_win_percentage*100:.5f}\n")

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
        print_outcomes(i+1, team_name, game.opponent, team_hss, opponent_hss, predicted_win_percentage*100, predicted_winner)

    # Finally, write W/L record
    avgHSS = (hss_sum / len(games)) if games else 0.0
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
    current_data_dir = os.path.join("..", "Current_Data")
    historical_data_dir = data_path

    total_stat = 0.0
    stat_count = 0

    # process a CSV file and sum stats
    def process_file(file_path, year_filter=None):
        nonlocal total_stat, stat_count
        with open(file_path, "r", encoding="utf-8-sig") as f:
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
    if os.path.exists(current_data_dir) and os.path.isdir(current_data_dir):
        for folder in os.listdir(current_data_dir):
            folder_path = os.path.join(current_data_dir, folder)
            if os.path.isdir(folder_path):
                team_file = os.path.join(folder_path, f"{team}.csv")
                if os.path.exists(team_file):
                    process_file(team_file, year_filter=year)

    # If no stats found for the exact year, check most recent past year in current data
    if stat_count == 0 and os.path.exists(current_data_dir):
        for folder in os.listdir(current_data_dir):
            folder_path = os.path.join(current_data_dir, folder)
            if os.path.isdir(folder_path):
                team_file = os.path.join(folder_path, f"{team}.csv")
                if os.path.exists(team_file):
                    process_file(team_file)  # Process all years in current data, which wil lkely be last year if the year above has no data

    # 2. Check Historical Data if no stats found in Current Data
    if stat_count == 0 and os.path.exists(historical_data_dir) and os.path.isdir(historical_data_dir):
        for folder in os.listdir(historical_data_dir):
            folder_path = os.path.join(historical_data_dir, folder)
            if os.path.isdir(folder_path):
                team_file = os.path.join(folder_path, f"{team}.csv")
                if os.path.exists(team_file):
                    process_file(team_file, year_filter=year)

    # Compute HSS
    if stat_count > 0:
        hss = total_stat / stat_count
        print(f"HSS for team: {team}, Year: {year} = {hss}")
        return hss
    else:
        print(f"No stats found for team: {team}, Year: {year}")
        return 0.0

def print_outcomes(game_number, team, opponent_team, team_hss, opponent_hss, predicted_win_percentage, predicted_winner):
    """
    Prints outcomes of each game prediction, mimicking the Java 'System.out.printf' style.
    """
    BOLD = "\033[1m"
    RESET = "\033[0m"
    print(f"{BOLD}GAME #{game_number}: {RESET}{team} vs {opponent_team}")
    print(f"HSS {team}: {team_hss:.5f}")
    print(f"HSS {opponent_team}: {opponent_hss:.5f}")
    print(f"Predicted Win Percentage for {team}: {predicted_win_percentage:.5f}%\n")
    print(f"Predicted Winner: {predicted_winner}")

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
    global data_store, prediction_writer, win_loss_writer

    data_store = DataStore(30)
    schedule_path = "../Schedule"
    historical_data_path = "../Cleaned_Data"
    current_date = date.today()

    # 1) Load training data
    X, y = load_training_data(historical_data_path)

    # 2) Train RandomForestRegressor
    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(X, y)

    # 3) Run predictions for every known team
    teamsList = data_store.get_teams_list()
    for team in teamsList:
        team_schedule_file = os.path.join(schedule_path, team, f"{team}.csv")
        predict_outcomes(team, team_schedule_file, historical_data_path, rf, current_date)

    # Close CSV writers if open
    if prediction_writer is not None:
        prediction_writer.flush()
        prediction_writer.close()
    if win_loss_writer is not None:
        win_loss_writer.flush()
        win_loss_writer.close()

    # 4) Read back the 'win_loss_records.csv' and print
    if os.path.exists("../Front/CSVFiles/win_loss_records.csv"):
        with open("../Front/CSVFiles/win_loss_records.csv", "r", encoding="utf-8-sig") as f:
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
    def __init__(self, date, opponent, location, year):
        self.date = date
        self.opponent = opponent
        self.location = location
        self.year = year
        self.result = None

    def set_result(self, result):
        self.result = result

if __name__ == "__main__":
    main()