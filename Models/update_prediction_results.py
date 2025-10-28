from datetime import date, datetime, timedelta
from typing import Dict, Iterable, Optional, Sequence

import requests
from nba_api.stats.endpoints import scoreboardv2

from config import CURRENT_SEASON
from prediction_history import PredictionHistoryManager


def _build_game_lookup(
    game_headers: Sequence[Dict[str, object]],
    line_scores: Iterable[Dict[str, object]],
) -> Dict[str, Dict[str, object]]:
    lookup: Dict[str, Dict[str, object]] = {}
    for header in game_headers:
        game_id = header["GAME_ID"]
        lookup[game_id] = {
            "status": header.get("GAME_STATUS_TEXT", ""),
            "home_team_id": header.get("HOME_TEAM_ID"),
            "away_team_id": header.get("VISITOR_TEAM_ID"),
            "home": None,
            "away": None,
        }

    for row in line_scores:
        game_id = row["GAME_ID"]
        entry = lookup.setdefault(
            game_id,
            {
                "status": row.get("GAME_STATUS_TEXT", ""),
                "home_team_id": None,
                "away_team_id": None,
                "home": None,
                "away": None,
            },
        )

        team_abbr = row.get("TEAM_ABBREVIATION")
        pts = row.get("PTS")
        pts_value: Optional[int]
        if isinstance(pts, str):
            try:
                pts_value = int(float(pts))
            except ValueError:
                pts_value = None
        elif isinstance(pts, (int, float)):
            pts_value = int(pts)
        else:
            pts_value = None

        team_entry = {
            "abbr": team_abbr,
            "pts": pts_value,
            "team_id": row.get("TEAM_ID"),
        }

        if entry.get("home_team_id") == row.get("TEAM_ID"):
            entry["home"] = team_entry
        elif entry.get("away_team_id") == row.get("TEAM_ID"):
            entry["away"] = team_entry
        else:
            location_hint = (row.get("HOME_AWAY") or row.get("TEAM_LOCATION_TYPE") or "").lower()
            if location_hint in {"home", "h"}:
                entry["home"] = team_entry
            elif location_hint in {"away", "visitor", "v"}:
                entry["away"] = team_entry
            elif entry["home"] is None:
                entry["home"] = team_entry
            else:
                entry["away"] = team_entry

    return lookup


def _safe_parse_int(value: object) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        try:
            return int(float(stripped))
        except ValueError:
            return None
    return None


def _fetch_espn_scoreboard(game_date: date) -> Optional[Dict[str, Dict[str, object]]]:
    """Fetch scoreboard data from ESPN's public scoreboard API."""

    params = {"dates": game_date.strftime("%Y%m%d")}
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; HoopSightBot/1.0)",
        "Accept": "application/json",
        "Referer": "https://www.espn.com/",
    }

    try:
        response = requests.get(
            "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard",
            params=params,
            headers=headers,
            timeout=15,
        )
        response.raise_for_status()
        payload = response.json()
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Unable to fetch ESPN scoreboard for {params['dates']}: {exc}")
        return None

    events = payload.get("events", [])
    if not events:
        return {}

    lookup: Dict[str, Dict[str, object]] = {}
    for event in events:
        competitions = event.get("competitions") or []
        if not competitions:
            continue
        competition = competitions[0]
        game_id = competition.get("id") or event.get("id") or f"espn-{len(lookup)}"

        status = competition.get("status", {}).get("type", {})
        status_text = (
            status.get("shortDetail")
            or status.get("detail")
            or status.get("description")
            or status.get("name", "")
        )

        home_entry = None
        away_entry = None
        for competitor in competition.get("competitors", []):
            team_info = competitor.get("team") or {}
            entry = {
                "abbr": team_info.get("abbreviation"),
                "pts": _safe_parse_int(competitor.get("score")),
                "team_id": _safe_parse_int(team_info.get("id")),
            }
            home_away = (competitor.get("homeAway") or "").lower()
            if home_away == "home":
                home_entry = entry
            elif home_away == "away":
                away_entry = entry

        lookup[game_id] = {
            "status": status_text,
            "home_team_id": home_entry.get("team_id") if home_entry else None,
            "away_team_id": away_entry.get("team_id") if away_entry else None,
            "home": home_entry,
            "away": away_entry,
        }

    return lookup


def _fetch_cdn_scoreboard(game_date: date) -> Optional[Dict[str, Dict[str, object]]]:
    """Fetch scoreboard data from the public NBA CDN."""

    ymd = game_date.strftime("%Y%m%d")
    url = f"https://cdn.nba.com/static/json/liveData/scoreboard/scoreboard_{ymd}.json"
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; HoopSightBot/1.0)",
        "Accept": "application/json",
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        payload = response.json()
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Unable to fetch CDN scoreboard for {ymd}: {exc}")
        return None

    games = payload.get("scoreboard", {}).get("games", [])
    if not games:
        return {}

    lookup: Dict[str, Dict[str, object]] = {}
    for game in games:
        game_id = game.get("gameId")
        if not game_id:
            continue

        home = game.get("homeTeam", {})
        away = game.get("awayTeam", {})

        home_team_id = _safe_parse_int(home.get("teamId"))
        away_team_id = _safe_parse_int(away.get("teamId"))

        lookup[game_id] = {
            "status": game.get("gameStatusText", ""),
            "home_team_id": home_team_id,
            "away_team_id": away_team_id,
            "home": {
                "abbr": home.get("teamTricode") or home.get("triCode"),
                "pts": _safe_parse_int(home.get("score")),
                "team_id": home_team_id,
            },
            "away": {
                "abbr": away.get("teamTricode") or away.get("triCode"),
                "pts": _safe_parse_int(away.get("score")),
                "team_id": away_team_id,
            },
        }

    return lookup


def _fetch_scoreboard_lookup(game_date: date) -> Dict[str, Dict[str, object]]:
    """Fetch scoreboard data with fallback mechanisms."""

    espn_lookup = _fetch_espn_scoreboard(game_date)
    if espn_lookup is not None:
        if espn_lookup:
            return espn_lookup

    cdn_lookup = _fetch_cdn_scoreboard(game_date)
    if cdn_lookup is not None:
        if cdn_lookup:
            return cdn_lookup

    formatted_date = game_date.strftime("%m/%d/%Y")
    try:
        scoreboard = scoreboardv2.ScoreboardV2(game_date=formatted_date, league_id="00")
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Unable to fetch NBA Stats scoreboard for {formatted_date}: {exc}")
        return {}

    normalized = scoreboard.get_normalized_dict()
    line_scores = normalized.get("LineScore", [])
    game_headers = normalized.get("GameHeader", [])
    return _build_game_lookup(game_headers, line_scores)


def _ensure_date_string(value: str) -> str:
    if "/" in value:
        # Already mm/dd/yyyy
        return value
    if "-" in value:
        dt = datetime.strptime(value, "%Y-%m-%d")
        return dt.strftime("%m/%d/%Y")
    raise ValueError(f"Unsupported date format: {value}")


def update_recent_results(days_back: int = 5, days_forward: int = 1) -> None:
    manager = PredictionHistoryManager(CURRENT_SEASON)
    today = date.today()
    pending = manager.pending_games()

    if not pending:
        print("No pending predictions found.")
        return

    targets = {}
    for record in pending:
        record_date = datetime.strptime(record.game_date, "%Y-%m-%d").date()
        if record_date < today - timedelta(days=days_back):
            continue
        if record_date > today + timedelta(days=days_forward):
            continue
        targets.setdefault(record_date, []).append(record)

    for game_date, records in sorted(targets.items()):
        lookup = _fetch_scoreboard_lookup(game_date)
        if not lookup:
            continue

        for record in records:
            match = None
            for game in lookup.values():
                home = game.get("home")
                away = game.get("away")
                if not home or not away:
                    continue
                record_home_abbr = (record.home_team_abbr or record.home_team).upper()
                record_away_abbr = (record.away_team_abbr or record.away_team).upper()
                home_abbr = (home.get("abbr") or "").upper()
                away_abbr = (away.get("abbr") or "").upper()
                if home_abbr == record_home_abbr and away_abbr == record_away_abbr:
                    match = game
                    break
            if not match:
                continue

            home_info = match.get("home")
            away_info = match.get("away")
            if not home_info or not away_info:
                continue

            home_pts = home_info.get("pts")
            away_pts = away_info.get("pts")
            status = match.get("status", "").lower()

            if home_pts is None or away_pts is None or "final" not in status:
                continue

            manager.upsert_actual_results(
                iso_date=record.game_date,
                home_team=record.home_team,
                away_team=record.away_team,
                home_score=home_pts,
                away_score=away_pts,
            )

    manager.save()


if __name__ == "__main__":
    update_recent_results()
