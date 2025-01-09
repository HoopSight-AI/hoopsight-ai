import os
import csv
from collections import deque
import heapq

class DataStore:
    """
    A Python adaptation of the Java DataStore class.
    It maintains:
      - game_results: list of strings describing games
      - team_statistics: list of strings describing stats
      - team_data_map: dict mapping 'team_name' -> list of TeamRecord
      - game_result_queue: queue for game results (like LinkedList in Java)
      - team_ranking: a max-heap by seeding_score (in Java was a reversed PriorityQueue)
      - head_to_head: 2D matrix storing wins/losses among teams
      - team_index_map: maps a team name to an integer index
    """

    def __init__(self, num_teams):
        self.game_results = []
        self.team_statistics = []
        self.team_data_map = {}
        self.game_result_queue = deque()

        # We can replicate a 'max-heap' by storing negative seeding scores in a min-heap
        # we'll store ( -seedingScore, TeamData ) in a list
        self.team_ranking_heap = []

        self.head_to_head = [[0]*num_teams for _ in range(num_teams)]
        self.team_index_map = {}


    def add_team_to_index_map(self, team, index):
        """
        Adds a team to the index map, associating it with an integer index.
        """
        if team not in self.team_index_map:
            self.team_index_map[team] = index

    def get_teams_list(self):
        """
        Returns a list of all teams that have been registered in the index map.
        """
        return list(self.team_index_map.keys())

    def get_team_index(self, team_name):
        """
        Retrieves the numeric index of a team, or -1 if not found.
        """
        return self.team_index_map.get(team_name, -1)


    def add_game_result(self, result):
        """
        Adds a game result string to both a list and a queue structure.
        """
        self.game_results.append(result)
        self.game_result_queue.append(result)

    def add_team_statistic(self, statistic):
        """
        Adds a single statistic for a team (stored in a simple list).
        """
        self.team_statistics.append(statistic)

    def clear(self):
        """
        Clears all stored data.
        """
        self.team_index_map.clear()
        self.game_results.clear()
        self.team_statistics.clear()
        self.team_data_map.clear()
        self.game_result_queue.clear()
        self.team_ranking_heap.clear()
        for row in self.head_to_head:
            for i in range(len(row)):
                row[i] = 0
                
    def add_team_record(self, team_name, record):
        """
        Associates a TeamRecord instance with a given team in the team_data_map.
        """
        if team_name not in self.team_data_map:
            self.team_data_map[team_name] = []
        self.team_data_map[team_name].append(record)

    def update_head_to_head(self, team_index_1, team_index_2, result):
        """
        Updates the head-to-head matrix with 'result' (1 for a win, 0 for a loss, etc.).
        """
        if team_index_1 < 0 or team_index_2 < 0 or team_index_1 >= len(self.head_to_head) or team_index_2 >= len(self.head_to_head):
            print(f"Invalid team indices: {team_index_1}, {team_index_2}")
            return
        self.head_to_head[team_index_1][team_index_2] += result

    def get_head_to_head_result(self, team_index_1, team_index_2):
        """
        Retrieves the number of times team1 (team_index_1) has beaten team2 (team_index_2).
        """
        if (team_index_1 < 0 or team_index_2 < 0 or 
            team_index_1 >= len(self.head_to_head) or 
            team_index_2 >= len(self.head_to_head)):
            return 0
        return self.head_to_head[team_index_1][team_index_2]


    def get_num_teams(self):
        return len(self.head_to_head)

    def display_team_data(self, team_name):
        """
        Prints out the stored records for a specified team.
        """
        records = self.team_data_map.get(team_name, [])
        if records:
            print("Data for team:", team_name)
            for record in records:
                print(record)
        else:
            print("No data found for team:", team_name)

    def display_ranked_teams(self):
        """
        Displays teams in descending order of seeding score (TeamData).
        """
        temp_heap = self.team_ranking_heap.copy()
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
        def __init__(self, team_name, seeding_score, points_scored, wins, losses):
            self.team_name = team_name
            self.seeding_score = seeding_score
            self.points_scored = points_scored
            self.wins = wins
            self.losses = losses

        def __str__(self):
            return (f"Team: {self.team_name}, Seeding Score: {self.seeding_score}, "
                    f"Points: {self.points_scored}, Wins: {self.wins}, Losses: {self.losses}")

        def get_seeding_score(self):
            return self.seeding_score

    def add_team_data(self, team_data):
        """
        We push negative seeding_score for a min-heap to replicate that ordering.
        """
        heapq.heappush(self.team_ranking_heap, (-team_data.get_seeding_score(), team_data))

def main():
    data_store = DataStore(30)  # space for 30 teams
    try:
        data_folder_path = "../Cleaned_Data"
        if not os.path.exists(data_folder_path) or not os.path.isdir(data_folder_path):
            print("Directory not found:", data_folder_path)
            return

        # Loop over each category folder
        for category_name in os.listdir(data_folder_path):
            category_folder = os.path.join(data_folder_path, category_name)
            if os.path.isdir(category_folder):
                print("Category:", category_name)
                
                # Loop over each team's CSV file
                for team_file in os.listdir(category_folder):
                    if team_file.endswith(".csv"):
                        file_path = os.path.join(category_folder, team_file)
                        team_name = team_file.replace(".csv", "")
                        
                        with open(file_path, "r", encoding="utf-8-sig") as f:
                            reader = csv.reader(f)
                            next(reader, None)
                            for row in reader:
                                if len(row) < 3:
                                    continue
                                rank = int(row[0].strip())
                                statistic = float(row[1].strip())
                                year = int(row[2].strip())
                                record = DataStore.TeamRecord(rank, statistic, year)
                                data_store.add_team_record(team_name, record)

        # Test display for a specific team
        data_store.display_team_data("Phoenix")  # example
    except Exception as e:
        print("An error occurred:", e)

if __name__ == "__main__":
    main()
