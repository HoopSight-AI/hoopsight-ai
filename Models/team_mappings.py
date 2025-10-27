from typing import Dict, Tuple

TEAM_NAME_LOOKUP: Dict[str, Tuple[str, str]] = {
    "Atlanta": ("Atlanta Hawks", "ATL"),
    "Boston": ("Boston Celtics", "BOS"),
    "Brooklyn": ("Brooklyn Nets", "BKN"),
    "Charlotte": ("Charlotte Hornets", "CHA"),
    "Chicago": ("Chicago Bulls", "CHI"),
    "Cleveland": ("Cleveland Cavaliers", "CLE"),
    "Dallas": ("Dallas Mavericks", "DAL"),
    "Denver": ("Denver Nuggets", "DEN"),
    "Detroit": ("Detroit Pistons", "DET"),
    "Golden State": ("Golden State Warriors", "GSW"),
    "Houston": ("Houston Rockets", "HOU"),
    "Indiana": ("Indiana Pacers", "IND"),
    "LA Clippers": ("Los Angeles Clippers", "LAC"),
    "LA Lakers": ("Los Angeles Lakers", "LAL"),
    "Memphis": ("Memphis Grizzlies", "MEM"),
    "Miami": ("Miami Heat", "MIA"),
    "Milwaukee": ("Milwaukee Bucks", "MIL"),
    "Minnesota": ("Minnesota Timberwolves", "MIN"),
    "New Orleans": ("New Orleans Pelicans", "NOP"),
    "New York": ("New York Knicks", "NYK"),
    "Oklahoma City": ("Oklahoma City Thunder", "OKC"),
    "Orlando": ("Orlando Magic", "ORL"),
    "Philadelphia": ("Philadelphia 76ers", "PHI"),
    "Phoenix": ("Phoenix Suns", "PHX"),
    "Portland": ("Portland Trail Blazers", "POR"),
    "Sacramento": ("Sacramento Kings", "SAC"),
    "San Antonio": ("San Antonio Spurs", "SAS"),
    "Toronto": ("Toronto Raptors", "TOR"),
    "Utah": ("Utah Jazz", "UTA"),
    "Washington": ("Washington Wizards", "WAS"),
}

# Allow aliases that may appear in CSVs
TEAM_NAME_LOOKUP["Los Angeles"] = TEAM_NAME_LOOKUP["LA Lakers"]
TEAM_NAME_LOOKUP["Los Angeles Lakers"] = TEAM_NAME_LOOKUP["LA Lakers"]
TEAM_NAME_LOOKUP["Los Angeles Clippers"] = TEAM_NAME_LOOKUP["LA Clippers"]
TEAM_NAME_LOOKUP["Brooklyn Nets"] = TEAM_NAME_LOOKUP["Brooklyn"]
TEAM_NAME_LOOKUP["Golden State Warriors"] = TEAM_NAME_LOOKUP["Golden State"]
TEAM_NAME_LOOKUP["New Orleans Pelicans"] = TEAM_NAME_LOOKUP["New Orleans"]
TEAM_NAME_LOOKUP["Oklahoma City Thunder"] = TEAM_NAME_LOOKUP["Oklahoma City"]
TEAM_NAME_LOOKUP["San Antonio Spurs"] = TEAM_NAME_LOOKUP["San Antonio"]
TEAM_NAME_LOOKUP["Phoenix Suns"] = TEAM_NAME_LOOKUP["Phoenix"]
TEAM_NAME_LOOKUP["Portland Trail Blazers"] = TEAM_NAME_LOOKUP["Portland"]
TEAM_NAME_LOOKUP["Minnesota Timberwolves"] = TEAM_NAME_LOOKUP["Minnesota"]
TEAM_NAME_LOOKUP["Sacramento Kings"] = TEAM_NAME_LOOKUP["Sacramento"]
TEAM_NAME_LOOKUP["Washington Wizards"] = TEAM_NAME_LOOKUP["Washington"]
TEAM_NAME_LOOKUP["Utah Jazz"] = TEAM_NAME_LOOKUP["Utah"]
TEAM_NAME_LOOKUP["Milwaukee Bucks"] = TEAM_NAME_LOOKUP["Milwaukee"]
TEAM_NAME_LOOKUP["Orlando Magic"] = TEAM_NAME_LOOKUP["Orlando"]
TEAM_NAME_LOOKUP["Cleveland Cavaliers"] = TEAM_NAME_LOOKUP["Cleveland"]
TEAM_NAME_LOOKUP["Chicago Bulls"] = TEAM_NAME_LOOKUP["Chicago"]
TEAM_NAME_LOOKUP["Charlotte Hornets"] = TEAM_NAME_LOOKUP["Charlotte"]
TEAM_NAME_LOOKUP["Indiana Pacers"] = TEAM_NAME_LOOKUP["Indiana"]
TEAM_NAME_LOOKUP["Detroit Pistons"] = TEAM_NAME_LOOKUP["Detroit"]
TEAM_NAME_LOOKUP["Denver Nuggets"] = TEAM_NAME_LOOKUP["Denver"]
TEAM_NAME_LOOKUP["Dallas Mavericks"] = TEAM_NAME_LOOKUP["Dallas"]
TEAM_NAME_LOOKUP["Atlanta Hawks"] = TEAM_NAME_LOOKUP["Atlanta"]
TEAM_NAME_LOOKUP["Boston Celtics"] = TEAM_NAME_LOOKUP["Boston"]
TEAM_NAME_LOOKUP["Miami Heat"] = TEAM_NAME_LOOKUP["Miami"]
TEAM_NAME_LOOKUP["Houston Rockets"] = TEAM_NAME_LOOKUP["Houston"]
TEAM_NAME_LOOKUP["Memphis Grizzlies"] = TEAM_NAME_LOOKUP["Memphis"]
TEAM_NAME_LOOKUP["Philadelphia 76ers"] = TEAM_NAME_LOOKUP["Philadelphia"]
TEAM_NAME_LOOKUP["Toronto Raptors"] = TEAM_NAME_LOOKUP["Toronto"]
TEAM_NAME_LOOKUP["New York Knicks"] = TEAM_NAME_LOOKUP["New York"]
TEAM_NAME_LOOKUP["Brooklyn"] = TEAM_NAME_LOOKUP["Brooklyn"]
TEAM_NAME_LOOKUP["LA Lakers"] = TEAM_NAME_LOOKUP["LA Lakers"]
TEAM_NAME_LOOKUP["LA Clippers"] = TEAM_NAME_LOOKUP["LA Clippers"]


def get_team_identity(team_name: str) -> Tuple[str, str]:
    """Return the full name and abbreviation for a given team alias."""
    normalized = team_name.strip()
    if normalized not in TEAM_NAME_LOOKUP:
        raise KeyError(f"Unrecognized team name: {team_name}")
    return TEAM_NAME_LOOKUP[normalized]
