# imports
import os
import requests
from bs4 import BeautifulSoup
import datetime
import pandas as pd

# functions for link searching and data scraping
def generate_yearly_urls(base_url, start_year, end_year):
    urls = []
    for year in range(start_year, end_year + 1):
        date_str = f"{year}-06-30"
        urls.append((f"{base_url}?date={date_str}", year))
    return urls

def scrape_data_for_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table')
    data = []
    if table:
        for row in table.find_all('tr')[1:]:
            cols = row.find_all('td')
            # convert percentage to decimal and remove plus sign from scoring margin
            row_data = [col.text.strip().replace('+', '') if '%' not in col.text else float(col.text.strip('%')) / 100 for col in cols[:3]]
            data.append(row_data)
    return data

# statistical categories
stats_categories = {
    "win_pct": "https://www.teamrankings.com/nba/stat/win-pct-all-games",
    "efg_pct": "https://www.teamrankings.com/nba/stat/effective-field-goal-pct",
    "defensive_efficiency": "https://www.teamrankings.com/nba/stat/defensive-efficiency",
    "opponent_efg_pct": "https://www.teamrankings.com/nba/stat/opponent-effective-field-goal-pct",
    "average_scoring_margin": "https://www.teamrankings.com/nba/stat/average-scoring-margin",
}

current_year = datetime.datetime.now().year

# root directory in kaggle for appropriate file storage
root = '/kaggle/working/'

for category, base_url in stats_categories.items():
    # create directory
    category_dir = os.path.join(root, category)
    os.makedirs(category_dir, exist_ok=True)
    urls_with_years = generate_yearly_urls(base_url, 2004, current_year)
    for url, year in urls_with_years:
        data = scrape_data_for_url(url)
        df = pd.DataFrame(data, columns=['Rank', 'Team', 'Statistic'])
        # standardization 
        filename = os.path.join(category_dir, f'{category}_{year}.csv')
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")
