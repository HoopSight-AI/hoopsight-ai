import aiohttp
import asyncio
import csv
import logging
from bs4 import BeautifulSoup

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fetch_injury_data():
    """Fetch and store NBA injury data from ESPN in CSV format"""
    url = "https://www.espn.com/nba/injuries"
    csv_path = "injuries.csv"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                logger.debug(f"Request sent to {url}, Status Code: {response.status}")
                
                if response.status == 200:
                    soup = BeautifulSoup(await response.text(), 'html.parser')
                    
                    # check injuries.csv to see results
                    with open(csv_path, 'w', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(['team', 'player', 'position', 'estimated_return_date', 'status', 'comment'])
                        
                        # Find all team injury sections
                        injury_sections = soup.find_all('div', class_='ResponsiveTable')  # Do not edit this
                        
                        for section in injury_sections:
                            # teams
                            team_header = section.find('span', class_='injuries__teamName ml2')
                            team_name = team_header.text.strip() if team_header else "Unknown Team"
                            
                            # players
                            rows = section.find_all('tr', class_='Table__TR')
                            for row in rows:
                                cols = row.find_all('td')
                                if len(cols) >= 5:  # 5 total columns exist
                                    player = cols[0].text.strip()
                                    position = cols[1].text.strip()
                                    estimated_return_date = cols[2].text.strip()
                                    status = cols[3].text.strip()
                                    comment = cols[4].text.strip()
                                    
                                    # Write data to injuries.csv
                                    writer.writerow([team_name, player, position, estimated_return_date, status, comment])
                    
                    logger.info(f"Injury data successfully written to {csv_path}")
                else:
                    logger.error(f"Failed to fetch data. Status code: {response.status}") #if 200 success, but not 200 fail
    except Exception as e:
        
        logger.error(f"Error occurred: {str(e)}")

# Run the script
if __name__ == "__main__":
    asyncio.run(fetch_injury_data())

#TODO: add external news scraping
#TODO: use groq api to analyze the injury and external news data, and factor in the appropriate player score addition/deduction.