import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time

def scrape_team_rankings(metric):
    base_url = "https://www.teamrankings.com/nba/"
    
    # Map of metrics
    url_mapping = {
        'abl': 'stat/average-biggest-lead',
        'ast_pp': 'stat/assists-per-game',
        'average_scoring_margin': 'stat/average-scoring-margin',
        'blk_pct': 'stat/blocks-per-game',
        'defensive_efficiency': 'stat/defensive-efficiency',
        'drb_pct': 'stat/defensive-rebounding-pct',
        'efg_pct': 'stat/effective-field-goal-pct',
        'flr_pct': 'stat/floor-percentage',
        'ftr': 'stat/free-throw-rate',
        'opp_flr_pct': 'stat/opponent-floor-percentage',
        'opponent_efg_pct': 'stat/opponent-effective-field-goal-pct',
        'orb_pct': 'stat/offensive-rebounding-pct',
        'pfs_pct': 'stat/personal-fouls-per-game',
        'sht_pct': 'stat/shooting-pct',
        'stls_pdp': 'stat/steal-pct',
        'tov_pct': 'stat/turnover-pct',
        'win_pct': 'stat/win-pct-all-games'
    }
    
    url = base_url + url_mapping[metric]
    
    try:
        # Add headers to avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the stats table - try multiple selectors
        table = soup.find('table', {'class': 'datatable'})
        if not table:
            table = soup.find('table')
        if not table:
            print(f"  ⚠️  No table found for {metric}")
            return None
            
        data = []
        rows = table.find_all('tr')[1:]  # Skip header
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 3:
                continue
            
            try:
                # Extract team name (usually in column 1)
                team = cols[1].text.strip()
                
                # Normalize team names
                team_mapping = {
                    'Okla City': 'Oklahoma City',
                    'LA Clippers': 'LA Clippers',
                    'LA Lakers': 'LA Lakers',
                    'New York': 'New York',
                    'Golden State': 'Golden State',
                    'San Antonio': 'San Antonio',
                    'New Orleans': 'New Orleans'
                }
                team = team_mapping.get(team, team)
                
                # Extract rank
                rank = int(cols[0].text.strip())
                
                # Extract main statistic value (column 2)
                stat_value = cols[2].text.strip().replace('%', '').replace(',', '')
                current = float(stat_value)
                
                # Try to extract additional columns if available
                last_3 = current  # Default to current if not available
                home = current
                away = current
                
                if len(cols) >= 4:
                    try:
                        last_3 = float(cols[3].text.strip().replace('%', '').replace(',', ''))
                    except (ValueError, IndexError):
                        pass
                
                if len(cols) >= 6:
                    try:
                        home = float(cols[5].text.strip().replace('%', '').replace(',', ''))
                    except (ValueError, IndexError):
                        pass
                
                if len(cols) >= 7:
                    try:
                        away = float(cols[6].text.strip().replace('%', '').replace(',', ''))
                    except (ValueError, IndexError):
                        pass
                
                # Calculate weighted statistic
                weighted_stat = (
                    0.60 * current +
                    0.15 * last_3 +
                    0.125 * home +
                    0.125 * away
                )
                
                data.append({
                    'Team': team,
                    'Rank': rank,
                    'Statistic': round(weighted_stat, 3),
                    'Year': datetime.now().year
                })
            except (ValueError, IndexError) as e:
                print(f"  ⚠️  Skipping row in {metric}: {e}")
                continue
        
        if not data:
            print(f"  ⚠️  No data extracted for {metric}")
            return None
        
        return pd.DataFrame(data)
    
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Network error scraping {metric}: {str(e)}")
        return None
    except Exception as e:
        print(f"  ❌ Error scraping {metric}: {str(e)}")
        return None

def create_current_stats():
    metrics = [
        'abl', 'ast_pp', 'average_scoring_margin', 'blk_pct',
        'defensive_efficiency', 'drb_pct', 'efg_pct', 'flr_pct',
        'ftr', 'opp_flr_pct', 'opponent_efg_pct', 'orb_pct',
        'pfs_pct', 'sht_pct', 'stls_pdp', 'tov_pct', 'win_pct'
    ]
    
    base_dir = "./Current_Data"
    os.makedirs(base_dir, exist_ok=True)
    
    print("=" * 70)
    print("Fetching Current NBA Team Statistics")
    print("=" * 70)
    print()
    
    # First, fetch win percentage data
    print("[1/17] Fetching Win Percentage data...")
    win_pct_df = scrape_team_rankings('win_pct')
    if win_pct_df is not None:
        win_pct_dict = win_pct_df.set_index('Team')['Statistic'].to_dict()
        print(f"  ✅ Successfully fetched win% for {len(win_pct_dict)} teams")
    else:
        print("  ⚠️  Failed to fetch Win Percentage data. Continuing without it...")
        win_pct_dict = {}
    
    # Add delay to avoid rate limiting
    time.sleep(2)
    
    # Process each metric
    success_count = 0
    fail_count = 0
    
    for idx, metric in enumerate(metrics, start=2):
        print(f"[{idx}/17] Processing {metric}...")
        metric_dir = os.path.join(base_dir, metric)
        os.makedirs(metric_dir, exist_ok=True)
        
        df = scrape_team_rankings(metric)
        
        if df is not None:
            # Add win percentage column
            df['Win Percentage'] = df['Team'].map(win_pct_dict)
            
            # Save individual team files
            teams_saved = 0
            for team, team_data in df.groupby('Team'):
                team_file = os.path.join(metric_dir, f'{team}.csv')
                team_data[['Rank', 'Statistic', 'Year', 'Win Percentage']].to_csv(
                    team_file, index=False
                )
                teams_saved += 1
            
            print(f"  ✅ Created {teams_saved} team files for {metric}")
            success_count += 1
        else:
            print(f"  ❌ Failed to scrape data for {metric}")
            fail_count += 1
        
        # Rate limiting: wait between requests
        if idx < len(metrics) + 1:
            time.sleep(1.5)
    
    # Summary
    print()
    print("=" * 70)
    print("SCRAPING SUMMARY")
    print("=" * 70)
    print(f"✅ Successful: {success_count}/{len(metrics)} metrics")
    print(f"❌ Failed: {fail_count}/{len(metrics)} metrics")
    if success_count == len(metrics):
        print("🎉 All metrics successfully scraped!")
    elif success_count > 0:
        print("⚠️  Some metrics failed. Check logs above for details.")
    else:
        print("❌ All metrics failed. Check network connection and website structure.")
    print("=" * 70)

if __name__ == "__main__":
    create_current_stats()
