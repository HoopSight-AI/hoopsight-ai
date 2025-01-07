import os
import csv
from sklearn.ensemble import RandomForestRegressor
from DataStore import DataStore
from datetime import date, datetime

# Global variables to mimic static fields in Java
dataStore = None
predictionWriter = None
winLossWriter = None

def loadTrainingData(cleanedDataPath):
    """
    Loads training data from CSV files in the provided directory (and sub-directories).
    - WeightedStat is the feature (X)
    - WinPercentage is the target (y)
    Returns (X, y) for training.
    """
    X = []
    y = []

    # Prepare the dataStore if it hasn't been initialized
    global dataStore
    if dataStore is None:
        dataStore = DataStore(30)

    teamIndex = 0
    # Traverse the 'cleanedDataPath' directory
    for statFolder in os.listdir(cleanedDataPath):
        statFolderPath = os.path.join(cleanedDataPath, statFolder)
        if os.path.isdir(statFolderPath):
            for teamFile in os.listdir(statFolderPath):
                if teamFile.endswith(".csv"):
                    filePath = os.path.join(statFolderPath, teamFile)
                    team = teamFile.split(".")[0]
                    # Map the team to an index if we have space
                    if teamIndex < 30 and team not in dataStore.teamIndexMap:
                        dataStore.addTeamToIndexMap(team, teamIndex)
                        teamIndex += 1

                    # Read the CSV
                    with open(filePath, "r", encoding="utf-8-sig") as f:
                        reader = csv.reader(f)
                        # Skip header
                        next(reader, None)
                        for row in reader:
                            # 0 -> rank, 1 -> WeightedStat, 2 -> year, 3 -> WinPercentage
                            if len(row) < 4:
                                continue
                            weightedStat = float(row[1].strip())
                            winPercentage = float(row[3].strip())
                            X.append([weightedStat])
                            y.append(winPercentage)
    return X, y

def predictOutcomes(teamName, schedulePath, historicalDataPath, model, currentDate):
    """
    Predicts outcomes for each game in 'schedulePath' using the trained RandomForest model.
    Writes results to 'prediction_results.csv' and aggregated W/L to 'win_loss_records.csv'.
    """

    # create fileWriter objects to write game-by-game predictions, final predicted win-loss records
    global predictionWriter, winLossWriter, dataStore
    if predictionWriter is None:
        predictionWriter = open("../Front/CSVFiles/prediction_results.csv", "w", encoding="utf-8-sig", newline="")
        predictionWriter.write("Date,Team,Opponent,HSS Home,HSS Away,Win%\n")
    if winLossWriter is None:
        winLossWriter = open("../Front/CSVFiles/win_loss_records.csv", "w", encoding="utf-8-sig", newline="")
        winLossWriter.write("Team,Wins,Losses,HSS\n")

    # if we can't find the team's schedule, break the program
    if not os.path.exists(schedulePath):
        print(f"Schedule file not found for {teamName}: {schedulePath}")
        return

    # Read the schedule CSV, convert into Game objects
    games = []
    with open(schedulePath, "r", encoding="utf-8-sig") as f:
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
    winCount = 0
    lossCount = 0
    hssSum = 0.0

    for i, game in enumerate(games):
        
        """
        # make sure the game being evaluted has not already happened
        gameDate = datetime.strptime(game.date, '%a, %b %d, %Y').date()
        if gameDate < currentDate:
            
            continue
        """

        teamHSS = loadHSS(teamName, historicalDataPath, game.year)
        hssSum += teamHSS
        opponentHSS = loadHSS(game.opponent, historicalDataPath, game.year)

        # If home, add a home advantage
        if game.location == "H":
            # Scales with opponent strength. 2.75 is a min boost, or 1.425% of the awayHSS
            homeAdvantageBoost = max(2.75, opponentHSS * 0.01425)
            teamHSS += homeAdvantageBoost

        weightedStat = teamHSS - opponentHSS
        # Model expects [ [WeightedStat], ... ]
        # TODO: #This is a single float. we'll need to add mor features and information to the model. This is why preditions arre not as accurate as they could be.
            
        predictedWinPercentage = model.predict([[weightedStat]])[0]  # single float

        if predictedWinPercentage > 0.5:
            predictedWinner = teamName
        elif predictedWinPercentage < 0.5:
            predictedWinner = game.opponent
        else:
            # tie-breaker if 0.5
            predictedWinner = teamName if game.location == "H" else game.opponent

        # Add result to dataStore
        dataStore.addGameResult(f"Game #{i+1}: {teamName} vs {game.opponent}, Winner: {predictedWinner}")

        # Write row to prediction file
        predictionWriter.write(f"{teamName},{game.opponent},{teamHSS:.5f},{opponentHSS:.5f},{predictedWinPercentage*100:.5f}\n")

        # Update head-to-head in dataStore
        currentTeamIndex = getTeamIndex(teamName)
        opponentTeamIndex = getTeamIndex(game.opponent)
        if predictedWinner == teamName:
            dataStore.updateHeadToHead(currentTeamIndex, opponentTeamIndex, 1)
            dataStore.updateHeadToHead(opponentTeamIndex, currentTeamIndex, 0)
            winCount += 1
        else:
            dataStore.updateHeadToHead(currentTeamIndex, opponentTeamIndex, 0)
            dataStore.updateHeadToHead(opponentTeamIndex, currentTeamIndex, 1)
            lossCount += 1

        # Print outcome to console
        printOutcomes(i+1, teamName, game.opponent, teamHSS, opponentHSS, predictedWinPercentage*100, predictedWinner)

    # Finally, write W/L record
    avgHSS = (hssSum / len(games)) if games else 0.0
    winLossWriter.write(f"{teamName},{winCount},{lossCount},{avgHSS:.5f}\n")

def getTeamIndex(teamName):
    """
    Retrieves a team's index from the DataStore.
    """
    return dataStore.getTeamIndex(teamName)

def loadHSS(team, dataPath, year):
    """
    Loads HoopSight Strength (HSS) for a given team and year:
    1. Checks `../Current_Data` for the exact year or most recent past year.
    2. Falls back to historical data in `dataPath` if no current data is found.
    Returns the total WeightedStat (HSS) for the team.
    """
    currentDataDir = os.path.join("..", "Current_Data")
    historicalDataDir = dataPath

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
    if os.path.exists(currentDataDir) and os.path.isdir(currentDataDir):
        for folder in os.listdir(currentDataDir):
            folder_path = os.path.join(currentDataDir, folder)
            if os.path.isdir(folder_path):
                team_file = os.path.join(folder_path, f"{team}.csv")
                if os.path.exists(team_file):
                    process_file(team_file, year_filter=year)

    # If no stats found for the exact year, check most recent past year in current data
    if stat_count == 0 and os.path.exists(currentDataDir):
        for folder in os.listdir(currentDataDir):
            folder_path = os.path.join(currentDataDir, folder)
            if os.path.isdir(folder_path):
                team_file = os.path.join(folder_path, f"{team}.csv")
                if os.path.exists(team_file):
                    process_file(team_file)  # Process all years in current data, which wil lkely be last year if the year above has no data

    # 2. Check Historical Data if no stats found in Current Data
    if stat_count == 0 and os.path.exists(historicalDataDir) and os.path.isdir(historicalDataDir):
        for folder in os.listdir(historicalDataDir):
            folder_path = os.path.join(historicalDataDir, folder)
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

def printOutcomes(gameNumber, team, opponentTeam, teamHSS, opponentHSS, predictedWinPercentage, predictedWinner):
    """
    Prints outcomes of each game prediction, mimicking the Java 'System.out.printf' style.
    """
    BOLD = "\033[1m"
    RESET = "\033[0m"
    print(f"{BOLD}GAME #{gameNumber}: {RESET}{team} vs {opponentTeam}")
    print(f"HSS {team}: {teamHSS:.5f}")
    print(f"HSS {opponentTeam}: {opponentHSS:.5f}")
    print(f"Predicted Win Percentage for {team}: {predictedWinPercentage:.5f}%\n")
    print(f"Predicted Winner: {predictedWinner}")

def queryWinsAndLosses(dataStore):
    """
    Queries the user for two teams, then prints their head-to-head record.
    """
    team1 = input("Enter the name of the first team: ").strip()
    team2 = input("Enter the name of the second team: ").strip()

    team1Index = dataStore.getTeamIndex(team1)
    team2Index = dataStore.getTeamIndex(team2)

    if team1Index == -1 or team2Index == -1:
        print("One or both team names are invalid.")
        return

    winsAgainst = dataStore.getHeadToHeadResult(team1Index, team2Index)
    lossesAgainst = dataStore.getHeadToHeadResult(team2Index, team1Index)

    print(f"{team1} vs {team2}:")
    print(f"{team1} wins: {winsAgainst}")
    print(f"{team1} losses: {lossesAgainst}")

def main():
    global dataStore, predictionWriter, winLossWriter

    dataStore = DataStore(30)
    schedulePath = "../Schedule"
    historicalDataPath = "../Cleaned_Data"
    currentDate = date.today()

    # 1) Load training data
    X, y = loadTrainingData(historicalDataPath)

    # 2) Train RandomForestRegressor
    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(X, y)

    # 3) Run predictions for every known team
    teamsList = dataStore.getTeamsList()
    for team in teamsList:
        teamScheduleFile = os.path.join(schedulePath, team, f"{team}.csv")
        predictOutcomes(team, teamScheduleFile, historicalDataPath, rf, currentDate)

    # Close CSV writers if open
    if predictionWriter is not None:
        predictionWriter.flush()
        predictionWriter.close()
    if winLossWriter is not None:
        winLossWriter.flush()
        winLossWriter.close()

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

    def setResult(self, result):
        self.result = result

if __name__ == "__main__":
    main()