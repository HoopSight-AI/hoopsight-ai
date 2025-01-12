import csv
import os

input_file = '../nba_schedule_2024-25.csv'
output_file = '../cleaned_schedule.csv'

team_map = {
    'Atlanta Hawks': 'Atlanta',
    'Boston Celtics' : 'Boston', 
    'Brooklyn Nets' : 'Brooklyn',
    'Charlotte Hornets': 'Charlotte',
    'Chicago Bulls': 'Chicago',
    'Cleveland Cavaliers': 'Cleveland',
    'Dallas Mavericks': 'Dallas',
    'Denver Nuggets': 'Denver',
    'Detroit Pistons': 'Detroit',
    'Golden State Warriors': 'Golden State',
    'Houston Rockets': 'Houston',
    'Indiana Pacers': 'Indiana',
    'Los Angeles Clippers': 'LA Clippers',
    'Los Angeles Lakers': 'LA Lakers',
    'Memphis Grizzlies': 'Memphis',
    'Miami Heat': 'Miami',
    'Milwaukee Bucks': 'Milwaukee',
    'Minnesota Timberwolves': 'Minnesota',
    'New Orleans Pelicans': 'New Orleans',
    'New York Knicks': 'New York',
    'Oklahoma City Thunder': 'Oklahoma City',
    'Orlando Magic': 'Orlando',
    'Philadelphia 76ers': 'Philadelphia',
    'Phoenix Suns': 'Phoenix',
    'Portland Trail Blazers': 'Portland',
    'Sacramento Kings': 'Sacramento',
    'San Antonio Spurs': 'San Antonio',
    'Toronto Raptors': 'Toronto',
    'Utah Jazz': 'Utah',
    'Washington Wizards': 'Washington'
}

with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)
    next(reader, None)
    for row in reader:
        row[2] = team_map[row[2]]
        row[3] = team_map[row[3]]
        writer.writerow(row)

os.replace(output_file, input_file)