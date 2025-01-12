from bs4 import BeautifulSoup
import csv
import requests

output_file = '../Standings/standings.csv'

url = 'https://www.teamrankings.com/nba/standings/'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
team_entries = []
content = soup.find('main')
conferences = content.find_all('table')
for conference in conferences: 
    divisions = conference.find_all('tbody')
    for division in divisions:
        team_rows = division.find_all('tr')
        for team in team_rows:
            team_stats = team.find_all('td')
            team_name = team_stats[0].get_text().strip()
            if team_name == 'Okla City':
                team_name = 'Oklahoma City'
            team_record = team_stats[2].get_text().strip()
            wins, losses = team_record.split('-')
            team_entry = [team_name, wins, losses]
            team_entries.append(team_entry)

with open(output_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Team','Wins','Losses'])
    writer.writerows(team_entries)