import os
import csv
from collections import deque
import heapq

class DataStore:
    """
    A Python adaptation of the Java DataStore class.
    It maintains:
      - gameResults: list of strings describing games
      - teamStatistics: list of strings describing stats
      - teamDataMap: dict mapping 'teamName' -> list of TeamRecord
      - gameResultQueue: queue for game results (like LinkedList in Java)
      - teamRanking: a max-heap by seedingScore (in Java was a reversed PriorityQueue)
      - headToHead: 2D matrix storing wins/losses among teams
      - teamIndexMap: maps a team name to an integer index
    """

    def __init__(self, num_teams):
        self.gameResults = []
        self.teamStatistics = []
        self.teamDataMap = {}
        self.gameResultQueue = deque()

        # We can replicate a 'max-heap' by storing negative seeding scores in a min-heap
        # we'll store ( -seedingScore, TeamData ) in a list
        self._teamRanking_heap = []

        self.headToHead = [[0]*num_teams for _ in range(num_teams)]
        self.teamIndexMap = {}


    def addTeamToIndexMap(self, team, index):
        """
        Adds a team to the index map, associating it with an integer index.
        """
        if team not in self.teamIndexMap:
            self.teamIndexMap[team] = index

    def getTeamsList(self):
        """
        Returns a list of all teams that have been registered in the index map.
        """
        return list(self.teamIndexMap.keys())

    def getTeamIndex(self, teamName):
        """
        Retrieves the numeric index of a team, or -1 if not found.
        """
        return self.teamIndexMap.get(teamName, -1)


    def addGameResult(self, result):
        """
        Adds a game result string to both a list and a queue structure.
        """
        self.gameResults.append(result)
        self.gameResultQueue.append(result)

    def addTeamStatistic(self, statistic):
        """
        Adds a single statistic for a team (stored in a simple list).
        """
        self.teamStatistics.append(statistic)

    def clear(self):
        """
        Clears all stored data.
        """
        self.teamIndexMap.clear()
        self.gameResults.clear()
        self.teamStatistics.clear()
        self.teamDataMap.clear()
        self.gameResultQueue.clear()
        self._teamRanking_heap.clear()
        for row in self.headToHead:
            for i in range(len(row)):
                row[i] = 0
                
    def addTeamRecord(self, teamName, record):
        """
        Associates a TeamRecord instance with a given team in the teamDataMap.
        """
        if teamName not in self.teamDataMap:
            self.teamDataMap[teamName] = []
        self.teamDataMap[teamName].append(record)

    def updateHeadToHead(self, teamIndex1, teamIndex2, result):
        """
        Updates the head-to-head matrix with 'result' (1 for a win, 0 for a loss, etc.).
        """
        if teamIndex1 < 0 or teamIndex2 < 0 or teamIndex1 >= len(self.headToHead) or teamIndex2 >= len(self.headToHead):
            print(f"Invalid team indices: {teamIndex1}, {teamIndex2}")
            return
        self.headToHead[teamIndex1][teamIndex2] += result

    def getHeadToHeadResult(self, teamIndex1, teamIndex2):
        """
        Retrieves the number of times team1 (teamIndex1) has beaten team2 (teamIndex2).
        """
        if (teamIndex1 < 0 or teamIndex2 < 0 or 
            teamIndex1 >= len(self.headToHead) or 
            teamIndex2 >= len(self.headToHead)):
            return 0
        return self.headToHead[teamIndex1][teamIndex2]


    def getNumTeams(self):
        return len(self.headToHead)

    def displayTeamData(self, teamName):
        """
        Prints out the stored records for a specified team.
        """
        records = self.teamDataMap.get(teamName, [])
        if records:
            print("Data for team:", teamName)
            for record in records:
                print(record)
        else:
            print("No data found for team:", teamName)

    def displayRankedTeams(self):
        """
        Displays teams in descending order of seeding score (TeamData).
        """
        temp_heap = self._teamRanking_heap.copy()
        print("Team Rankings based on Seeding Score:")
        # Because we're storing -seedingScore, pop items and invert again
        while temp_heap:
            neg_score, team_data = heapq.heappop(temp_heap)
            print(team_data)


    class TeamRecord:
        def __init__(self, rank, statistic, year):
            self.rank = rank
            self.statistic = statistic
            self.year = year

        def __str__(self):
            return f"Year: {self.year}, Rank: {self.rank}, Statistic: {self.statistic}"

    class TeamData:
        def __init__(self, teamName, seedingScore, pointsScored, wins, losses):
            self.teamName = teamName
            self.seedingScore = seedingScore
            self.pointsScored = pointsScored
            self.wins = wins
            self.losses = losses

        def __str__(self):
            return (f"Team: {self.teamName}, Seeding Score: {self.seedingScore}, "
                    f"Points: {self.pointsScored}, Wins: {self.wins}, Losses: {self.losses}")

        def getSeedingScore(self):
            return self.seedingScore

    def addTeamData(self, teamData):
        """
        We push negative seedingScore for a min-heap to replicate that ordering.
        """
        heapq.heappush(self._teamRanking_heap, (-teamData.getSeedingScore(), teamData))

def main():
    dataStore = DataStore(30)  # space for 30 teams
    try:
        dataFolderPath = "../Cleaned_Data"
        if not os.path.exists(dataFolderPath) or not os.path.isdir(dataFolderPath):
            print("Directory not found:", dataFolderPath)
            return

        # Loop over each category folder
        for categoryName in os.listdir(dataFolderPath):
            categoryFolder = os.path.join(dataFolderPath, categoryName)
            if os.path.isdir(categoryFolder):
                print("Category:", categoryName)
                
                # Loop over each team's CSV file
                for teamFile in os.listdir(categoryFolder):
                    if teamFile.endswith(".csv"):
                        filePath = os.path.join(categoryFolder, teamFile)
                        teamName = teamFile.replace(".csv", "")
                        
                        with open(filePath, "r", encoding="utf-8-sig") as f:
                            reader = csv.reader(f)
                            next(reader, None)
                            for row in reader:
                                if len(row) < 3:
                                    continue
                                rank = int(row[0].strip())
                                statistic = float(row[1].strip())
                                year = int(row[2].strip())
                                record = DataStore.TeamRecord(rank, statistic, year)
                                dataStore.addTeamRecord(teamName, record)

        # Test display for a specific team
        dataStore.displayTeamData("Phoenix")  # example
    except Exception as e:
        print("An error occurred:", e)

if __name__ == "__main__":
    main()
