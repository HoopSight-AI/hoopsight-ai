import aiohttp
import asyncio
import csv
import logging
import json
from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import leaguedashplayerstats, playerestimatedmetrics
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import pandas as pd
import time
from datetime import datetime


load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


def get_team_name_mapping():
    """Create mapping between team abbreviations and full names."""
    nba_teams = teams.get_teams()
    return {team['abbreviation']: team['full_name'] for team in nba_teams}

def get_player_id_mapping():
    """Create mapping between player names and their IDs."""
    all_players = players.get_players()
    return {player['full_name']: player['id'] for player in all_players}

async def fetch_and_save_injuries():
    """
    Fetch current injuries from ESPN and save to 'injuries.csv'.
    Returns a pandas DataFrame of the injuries.
    """
    url = "https://www.espn.com/nba/injuries"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    soup = BeautifulSoup(await response.text(), 'html.parser')
                    
                    with open('injuries.csv', 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(['team', 'player', 'position', 'estimated_return_date', 'status', 'comment'])
                        
                        injury_sections = soup.find_all('div', class_='ResponsiveTable')
                        for section in injury_sections:
                            team_header = section.find('span', class_='injuries__teamName ml2')
                            team_name = team_header.text.strip() if team_header else "Unknown Team"
                            
                            rows = section.find_all('tr', class_='Table__TR')
                            for row in rows:
                                cols = row.find_all('td')
                                if len(cols) >= 5:
                                    writer.writerow([
                                        team_name,
                                        cols[0].text.strip(),
                                        cols[1].text.strip(),
                                        cols[2].text.strip(),
                                        cols[3].text.strip(),
                                        cols[4].text.strip()
                                    ])
                    
                    logger.info("Injuries data saved to injuries.csv")
                    return pd.read_csv('injuries.csv')
                else:
                    logger.error(f"Error response from ESPN. Status code: {response.status}")
                    return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error fetching injuries: {str(e)}")
        return pd.DataFrame()

def fetch_current_nba_players():
    """Return a list of full names of players labeled as active in the nba_api."""
    active_players = players.get_active_players()
    return [player['full_name'] for player in active_players]

def calculate_base_player_scores():
    """
    Calculate a comprehensive base score for each player using actual NBA stats
    instead of estimated metrics.
    Returns a DataFrame with actual stats and player IDs.
    """
    try:
        time.sleep(12)
        dashboard = leaguedashplayerstats.LeagueDashPlayerStats(
            season='2024-25',
            per_mode_detailed='PerGame',
            measure_type_detailed_defense='Base',
            plus_minus='Y',
            rank='Y',
            pace_adjust='Y'
        )
        base_stats_df = dashboard.get_data_frames()[0]
        
        time.sleep(10)
        offensive_stats = leaguedashplayerstats.LeagueDashPlayerStats(
            season='2024-25',
            per_mode_detailed='PerGame',
            measure_type_detailed_defense='Advanced',
            pace_adjust='Y'
        )
        advanced_stats_df = offensive_stats.get_data_frames()[0]
        
        # Merge the dataframes
        stats_df = base_stats_df.merge(
            advanced_stats_df[['PLAYER_ID', 'OFF_RATING', 'DEF_RATING', 'NET_RATING']],
            on='PLAYER_ID',
            how='left'
        )
        
        # Calculate player score (base score)
        stats_df['base_score'] = (
            stats_df['PTS'] * 2.5 +
            stats_df['FG_PCT'].fillna(0) * 2.6 +
            stats_df['FT_PCT'].fillna(0) * 2.2 +
            stats_df['FG3_PCT'].fillna(0) * 2.5 +
            stats_df['AST'] * 3.5 +
            stats_df['OREB'] * 2.0 +
            stats_df['DREB'] * 1.2 +
            stats_df['STL'] * 3.0 +
            stats_df['BLK'] * 1.6 +
            stats_df['OFF_RATING'].fillna(0) * 2.0 + 
            stats_df['DEF_RATING'].fillna(0) * -0.85 + 
            stats_df['NET_RATING'].fillna(0) * 1.0 +  
            stats_df['PLUS_MINUS'] * 2.2 +

            stats_df['TOV'] * -1.2 +
            stats_df['PF'] * -0.4
        )
        
        return stats_df[['PLAYER_ID', 'PLAYER_NAME', 'TEAM_ABBREVIATION', 'base_score']]
    
    except Exception as e:
        logger.error(f"Error calculating player scores: {str(e)}")
        return pd.DataFrame()

async def fetch_nba_articles():
    """Fetch current NBA news articles."""
    url = "https://nba-stories.onrender.com/articles"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    articles = await response.json()
                    return articles
                else:
                    logger.error(f"Failed to fetch articles, status: {response.status}")
                    return []
    except Exception as e:
        logger.error(f"Error fetching articles: {str(e)}")
        return []

async def analyze_article_with_groq(article_title, current_nba_players):
    """Send article to Groq for analysis."""
    if not GROQ_API_KEY:
        return []
    
    prompt = f"""
    You are given an NBA article title: "{article_title}" 
    and a list of current NBA players: {json.dumps(current_nba_players[:200])}

    1) Identify which players are referenced in the title. 
    2) For each mentioned player, determine the sentiment: 
       - "positive" => determine the appropriate adjustment on a scale of 0 to +25
       - "negative" => determine the appropriate adjustment on a scale of -25 to 0
       - "neutral" => 0 adjustment
       - "suspended" => final score = 0
    3) Return as JSON list with format:
       {{
         "name": string,
         "sentiment": ["positive", "negative", "neutral", "suspended"],
         "adjustment": number,
         "reason": string
       }}
    
    Only respond with valid JSON.
    """
    
    payload = {
        "model": "mixtral-8x7b-32768",
        "messages": [
            {"role": "system", "content": prompt}
        ],
        "temperature": 0.2 # maybe this should be 0.1
    }
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(GROQ_API_URL, headers=headers, json=payload, timeout=30) as response:
                if response.status == 200:
                    result = await response.json()
                    groq_reply = result["choices"][0]["message"]["content"].strip()
                    try:
                        analysis = json.loads(groq_reply)
                        return analysis if isinstance(analysis, list) else []
                    except json.JSONDecodeError:
                        logger.error(f"Invalid JSON from Groq: {groq_reply}")
                        return []
                else:
                    logger.error(f"Groq API error, or possible rate limiting: {await response.text()}")
                    return []
    except Exception as e:
        logger.error(f"Error calling Groq API: {str(e)}")
        return []

async def analyze_articles_for_adjustments(articles, current_nba_players):
    adjustments = {}
    
    for article in articles:
        title = article.get("title", "")
        analysis_list = await analyze_article_with_groq(title, current_nba_players)
        await asyncio.sleep(5)  # Rate limiting
        
        for analysis in analysis_list:
            name = analysis.get("name")
            sentiment = analysis.get("sentiment", "neutral")
            score_adjustment = analysis.get("adjustment", 0)
            reason = analysis.get("reason", "No reason given")
            
            if not name:
                continue
                
            if name not in adjustments:
                adjustments[name] = {
                    "total_adjustment": 0,
                    "reasons": [],
                    "suspended": False
                }
            
            if sentiment.lower() == "suspended":
                adjustments[name]["suspended"] = True
                adjustments[name]["reasons"].append(f"Suspended: {reason}")
            else:
                adjustments[name]["total_adjustment"] += score_adjustment
                sign = "+" if score_adjustment > 0 else ""
                adjustments[name]["reasons"].append(
                    f"{sentiment.capitalize()}: {reason} ({sign}{score_adjustment})"
                )
    
    return adjustments

async def calculate_final_scores():
    """Calculate and save final scores with all adjustments."""
    team_mapping = get_team_name_mapping()
    player_id_mapping = get_player_id_mapping()
    
    injuries_df = await fetch_and_save_injuries()
    base_scores_df = calculate_base_player_scores()
    
    if base_scores_df.empty:
        logger.error("Failed to get base player scores")
        return
    
    articles = await fetch_nba_articles()
    current_nba_players = fetch_current_nba_players()
    articles_adjustments = await analyze_articles_for_adjustments(articles, current_nba_players)
    
    final_scores = []
    team_scores = {}
    team_player_counts = {}
    
    for _, row in base_scores_df.iterrows():
        player_name = row['PLAYER_NAME']
        team_abbrev = row['TEAM_ABBREVIATION']
        player_id = row['PLAYER_ID']
        base_score = float(row['base_score'])
        
        injured_records = injuries_df[injuries_df['player'] == player_name]
        is_injured = len(injured_records) > 0
        injury_reason = ""
        if is_injured and not injured_records.empty:
            first_injury = injured_records.iloc[0]
            injury_reason = f"Status: {first_injury['status']}. {first_injury['comment']}"
        
        player_adjustments = articles_adjustments.get(player_name, {})
        suspended = player_adjustments.get("suspended", False)
        news_adjustment = player_adjustments.get("total_adjustment", 0.0)
        news_reasons = player_adjustments.get("reasons", [])
        
        if is_injured:
            final_score = 0.0
            reason = f"INJURED: {injury_reason}"
        elif suspended:
            final_score = 0.0
            reason = "SUSPENDED: " + " | ".join(news_reasons)
        else:
            final_score = base_score + news_adjustment
            reason = " | ".join(news_reasons) if news_reasons else "No adjustments"
        
        # Add to final scores
        final_scores.append({
            'team': team_mapping.get(team_abbrev, team_abbrev),
            'team_abbrev': team_abbrev,  # For sorting
            'player': player_name,
            'player_id': player_id,
            'player_score': round(final_score, 3), # round to 3 decimal places
            'reason': reason
        })
        
        if team_abbrev not in team_scores:
            team_scores[team_abbrev] = 0.0
            team_player_counts[team_abbrev] = 0
        
        team_scores[team_abbrev] += final_score
        if final_score > 0:
            team_player_counts[team_abbrev] += 1
    
    # Sort by team, then by player score within team
    final_scores.sort(key=lambda x: (x['team_abbrev'], -x['player_score']))
    
    # Save individual player scores to CSV
    with open('individual_player_scores.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['team', 'player', 'player_id', 'player_score', 'reason'])
        writer.writeheader()
        writer.writerows([{k: v for k, v in score.items() if k != 'team_abbrev'} 
                         for score in final_scores])
    
    logger.info("Final player scores saved to individual_player_scores.csv")
    
    # Save team scores to CSV
    sorted_teams_scores = sorted(team_scores.items(), key=lambda x: x[1], reverse=True)
    
    with open('team_player_scores.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['team', 'total_player_score'])
        for team_abbrev, total_score in sorted_teams_scores:
            player_count = team_player_counts[team_abbrev]
            average_score = total_score / player_count if player_count > 0 else 0
            writer.writerow([team_mapping.get(team_abbrev, team_abbrev), round(average_score, 3)])
    
    logger.info("Team player scores saved to team_player_scores.csv")
    
    current_team = None
    for score in final_scores:
        if score['team'] != current_team:
            current_team = score['team']
            print(f"\n{current_team}")
            print("-" * 50)
        print(f"{score['player']}: {score['player_score']} ({score['reason'][:1000]}...)")

async def main():
    await calculate_final_scores()

if __name__ == "__main__":
    asyncio.run(main())