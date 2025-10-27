"""Utilities for fetching ESPN matchup predictor data for NBA games."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, Optional

import requests
from bs4 import BeautifulSoup

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " \
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
SCOREBOARD_URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"

_SCOREBOARD_CACHE: Dict[str, Dict[str, object]] = {}

_ABBR_CANONICAL: Dict[str, str] = {
    "ATL": "ATL",
    "BOS": "BOS",
    "BKN": "BKN",
    "CHA": "CHA",
    "CHI": "CHI",
    "CLE": "CLE",
    "DAL": "DAL",
    "DEN": "DEN",
    "DET": "DET",
    "GS": "GSW",
    "GSW": "GSW",
    "HOU": "HOU",
    "IND": "IND",
    "LAC": "LAC",
    "LAL": "LAL",
    "MEM": "MEM",
    "MIA": "MIA",
    "MIL": "MIL",
    "MIN": "MIN",
    "NO": "NOP",
    "NOP": "NOP",
    "NY": "NYK",
    "NYK": "NYK",
    "OKC": "OKC",
    "ORL": "ORL",
    "PHI": "PHI",
    "PHX": "PHX",
    "POR": "POR",
    "SAC": "SAC",
    "SA": "SAS",
    "SAS": "SAS",
    "TOR": "TOR",
    "UTA": "UTA",
    "UTAH": "UTA",
    "WAS": "WAS",
    "WSH": "WAS",
}


def _canonical_abbr(abbr: Optional[str]) -> Optional[str]:
    if abbr is None:
        return None
    upper = abbr.upper()
    return _ABBR_CANONICAL.get(upper, upper)


@dataclass
class EspnPrediction:
    game_id: Optional[str]
    source_url: Optional[str]
    home_pct: Optional[float]
    away_pct: Optional[float]
    favorite_full: Optional[str]
    favorite_abbr: Optional[str]
    confidence_gap: Optional[float]


def _normalize_pct(value: Optional[object]) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        if value.endswith("%"):
            value = value[:-1]
        try:
            value = float(value)
        except ValueError:
            return None
    if isinstance(value, (int, float)):
        numeric = float(value)
        if numeric <= 1:
            numeric *= 100
        return round(numeric, 3)
    return None


def _extract_from_predictor(entry: Optional[Dict[str, object]]) -> Optional[float]:
    if not isinstance(entry, dict):
        return None
    for key in (
        "teamChance",
        "chance",
        "probability",
        "prob",
        "value",
        "gameProjection",
        "winPercentage",
        "teamProbability",
    ):
        if key in entry:
            pct = _normalize_pct(entry[key])
            if pct is not None:
                return pct
    if "displayValue" in entry:
        return _normalize_pct(entry["displayValue"])
    return None


def _extract_probabilities_from_event(event: Dict[str, object]) -> Dict[str, Optional[float]]:
    competitions = event.get("competitions", [])
    if not competitions:
        return {"home": None, "away": None}
    comp = competitions[0]

    predictor = comp.get("predictor") or event.get("predictor")
    if isinstance(predictor, dict):
        home_pct = _extract_from_predictor(predictor.get("homeTeam"))
        away_pct = _extract_from_predictor(predictor.get("awayTeam"))
        if home_pct is not None or away_pct is not None:
            return {"home": home_pct, "away": away_pct}

    probabilities = comp.get("probabilities") or event.get("probabilities")
    if isinstance(probabilities, list):
        for item in probabilities:
            if not isinstance(item, dict):
                continue
            home_pct = _extract_from_predictor(item.get("homeTeam"))
            away_pct = _extract_from_predictor(item.get("awayTeam"))
            if home_pct is not None or away_pct is not None:
                return {"home": home_pct, "away": away_pct}

    return {"home": None, "away": None}


def _scrape_gamecast_prediction(url: str) -> Dict[str, Optional[float]]:
    try:
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=15)
        response.raise_for_status()
    except requests.RequestException:
        return {"home": None, "away": None}

    soup = BeautifulSoup(response.text, "html.parser")
    values = soup.select(".matchupPredictor__teamValue")
    if not values:
        return {"home": None, "away": None}

    home_pct = None
    away_pct = None
    for node in values:
        text_value = node.get_text(strip=True)
        pct = _normalize_pct(text_value)
        if pct is None:
            continue
        class_names = node.get("class", [])
        if any("teamValue--a" in cls for cls in class_names):
            home_pct = pct
        elif any("teamValue--b" in cls for cls in class_names):
            away_pct = pct

    if home_pct is None or away_pct is None:
        extracted = [_normalize_pct(node.get_text(strip=True)) for node in values[:2]]
        if len(extracted) >= 2 and extracted[0] is not None and extracted[1] is not None:
            # ESPN appears to render away team (B) before home team (A)
            away_pct = extracted[0]
            home_pct = extracted[1]

    return {"home": home_pct, "away": away_pct}


def fetch_espn_prediction(iso_date: str, home_abbr: str, away_abbr: str) -> EspnPrediction:
    datestr = iso_date.replace("-", "")
    params = {"dates": datestr}
    target_home_abbr = _canonical_abbr(home_abbr)
    target_away_abbr = _canonical_abbr(away_abbr)
    if target_home_abbr is None or target_away_abbr is None:
        return EspnPrediction(None, None, None, None, None, None, None)
    try:
        if datestr in _SCOREBOARD_CACHE:
            scoreboard = _SCOREBOARD_CACHE[datestr]
        else:
            response = requests.get(
                SCOREBOARD_URL,
                params=params,
                headers={"User-Agent": USER_AGENT},
                timeout=15,
            )
            response.raise_for_status()
            scoreboard = response.json()
            _SCOREBOARD_CACHE[datestr] = scoreboard
    except (requests.RequestException, json.JSONDecodeError):
        return EspnPrediction(None, None, None, None, None, None, None)

    events = scoreboard.get("events", [])
    for event in events:
        competitions = event.get("competitions", [])
        if not competitions:
            continue
        comp = competitions[0]
        competitors = comp.get("competitors", [])
        home_comp = next((c for c in competitors if c.get("homeAway") == "home"), None)
        away_comp = next((c for c in competitors if c.get("homeAway") == "away"), None)
        if not home_comp or not away_comp:
            continue

        event_home_abbr = _canonical_abbr(home_comp.get("team", {}).get("abbreviation"))
        event_away_abbr = _canonical_abbr(away_comp.get("team", {}).get("abbreviation"))
        if event_home_abbr != target_home_abbr or event_away_abbr != target_away_abbr:
            continue

        game_id = event.get("id")
        source_url = None
        for link in event.get("links", []):
            if not isinstance(link, dict):
                continue
            rel = link.get("rel", [])
            if "gamecast" in rel:
                source_url = link.get("href")
                break
        if not source_url and game_id:
            source_url = f"https://www.espn.com/nba/game/_/gameId/{game_id}"

        predictor = _extract_probabilities_from_event(event)
        if predictor["home"] is None or predictor["away"] is None:
            predictor = _scrape_gamecast_prediction(source_url) if source_url else {"home": None, "away": None}

        home_pct = predictor.get("home")
        away_pct = predictor.get("away")

        favorite_full = None
        favorite_abbr = None
        confidence_gap = None
        if home_pct is not None and away_pct is not None:
            if home_pct >= away_pct:
                favorite_full = home_comp.get("team", {}).get("displayName")
                favorite_abbr = event_home_abbr
                confidence_gap = round(abs(home_pct - 50.0), 3)
            else:
                favorite_full = away_comp.get("team", {}).get("displayName")
                favorite_abbr = event_away_abbr
                confidence_gap = round(abs(away_pct - 50.0), 3)

        return EspnPrediction(game_id, source_url, home_pct, away_pct, favorite_full, favorite_abbr, confidence_gap)

    return EspnPrediction(None, None, None, None, None, None, None)
