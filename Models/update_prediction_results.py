from datetime import date, datetime, timedelta
from typing import Dict, Iterable, Optional, Sequence

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
        formatted_date = game_date.strftime("%m/%d/%Y")
        try:
            scoreboard = scoreboardv2.ScoreboardV2(game_date=formatted_date, league_id="00")
        except Exception as exc:  # pylint: disable=broad-except
            print(f"Unable to fetch scoreboard for {formatted_date}: {exc}")
            continue

        normalized = scoreboard.get_normalized_dict()
        line_scores = normalized.get("LineScore", [])
        game_headers = normalized.get("GameHeader", [])
        lookup = _build_game_lookup(game_headers, line_scores)

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
