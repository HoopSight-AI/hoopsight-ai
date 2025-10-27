"""
Injury adjustment utilities for HoopSight AI predictions.

This module loads injuries and player scores to compute team strength adjustments
based on which players are unavailable for upcoming games.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import pandas as pd

from config import PROJECT_ROOT
from team_mappings import TEAM_NAME_LOOKUP


class InjuryAdjuster:
    """Manages injury-based HSS adjustments for teams."""

    def __init__(
        self,
        injuries_csv: Optional[Path] = None,
        player_scores_csv: Optional[Path] = None,
    ):
        """
        Initialize the injury adjuster.

        Args:
            injuries_csv: Path to injuries.csv (default: Data_Gathering_&_Cleaning/injuries.csv)
            player_scores_csv: Path to individual_player_scores.csv
        """
        data_dir = PROJECT_ROOT / "Data_Gathering_&_Cleaning"
        self.injuries_csv = injuries_csv or data_dir / "injuries.csv"
        self.player_scores_csv = player_scores_csv or data_dir / "individual_player_scores.csv"

        # Load data
        self.injuries_df: Optional[pd.DataFrame] = None
        self.player_scores_df: Optional[pd.DataFrame] = None
        self._load_data()

        # Build lookup structures
        self.team_player_scores: Dict[str, Dict[str, float]] = {}
        self._build_player_score_lookup()

    def _load_data(self) -> None:
        """Load injuries and player scores from CSV files."""
        if self.injuries_csv.exists():
            self.injuries_df = pd.read_csv(self.injuries_csv)
            print(f"Loaded {len(self.injuries_df)} injury records from {self.injuries_csv}")
        else:
            print(f"Warning: Injuries file not found at {self.injuries_csv}")
            self.injuries_df = pd.DataFrame(columns=["team", "player", "status", "estimated_return_date"])

        if self.player_scores_csv.exists():
            self.player_scores_df = pd.read_csv(self.player_scores_csv)
            print(f"Loaded {len(self.player_scores_df)} player scores from {self.player_scores_csv}")
        else:
            print(f"Warning: Player scores file not found at {self.player_scores_csv}")
            self.player_scores_df = pd.DataFrame(columns=["team", "player", "player_score"])

    def _build_player_score_lookup(self) -> None:
        """Build a nested dict: team -> player -> score."""
        if self.player_scores_df is None or self.player_scores_df.empty:
            return

        for _, row in self.player_scores_df.iterrows():
            team = str(row["team"]).strip()
            player = str(row["player"]).strip()
            score = float(row["player_score"]) if pd.notna(row["player_score"]) else 0.0

            if team not in self.team_player_scores:
                self.team_player_scores[team] = {}
            self.team_player_scores[team][player] = score

    def _normalize_team_name(self, team_name: str) -> str:
        """
        Normalize team name to match our project's short form.
        
        Args:
            team_name: Team name (could be full or short form)
            
        Returns:
            Normalized short team name (e.g., "Atlanta", "LA Lakers")
        """
        team_name = team_name.strip()
        
        # Direct lookup for canonical short names
        if team_name in TEAM_NAME_LOOKUP:
            full, abbr = TEAM_NAME_LOOKUP[team_name]
            # If the key itself is a short name (< 25 chars, not a full name), use it
            if len(team_name) < 25 and not team_name.endswith(('Hawks', 'Celtics', 'Nets', 'Hornets', 'Bulls',
                                                                  'Cavaliers', 'Mavericks', 'Nuggets', 'Pistons',
                                                                  'Warriors', 'Rockets', 'Pacers', 'Clippers', 'Lakers',
                                                                  'Grizzlies', 'Heat', 'Bucks', 'Timberwolves', 'Pelicans',
                                                                  'Knicks', 'Thunder', 'Magic', '76ers', 'Suns',
                                                                  'Trail Blazers', 'Kings', 'Spurs', 'Raptors', 'Jazz', 'Wizards')):
                return team_name
        
        # Search for full name match and return the short form
        for short, (full, abbr) in TEAM_NAME_LOOKUP.items():
            if team_name == full:
                return short
            if abbr and team_name == abbr:
                return short
        
        # Return as-is if we can't normalize
        return team_name

    def get_injury_penalty(self, team_name: str, game_date: Optional[str] = None) -> float:
        """
        Calculate the HSS penalty for a team based on current injuries.

        The penalty is the sum of player_scores for all injured/questionable players.
        A higher penalty means the team is more weakened by injuries.

        Args:
            team_name: Team name (short form like "Atlanta" or full like "Atlanta Hawks")
            game_date: ISO date string (YYYY-MM-DD) to check if injury is relevant (optional)

        Returns:
            Total HSS penalty (sum of injured player scores)
        """
        if self.injuries_df is None or self.injuries_df.empty:
            return 0.0

        # Normalize team name
        normalized_team = self._normalize_team_name(team_name)

        # Filter injuries for this team
        team_injuries = self.injuries_df[
            self.injuries_df["team"].str.strip() == normalized_team
        ].copy()

        if team_injuries.empty:
            # Try matching against full team names in injuries.csv
            team_injuries = self.injuries_df[
                self.injuries_df["team"].str.contains(normalized_team, case=False, na=False)
            ].copy()

        if team_injuries.empty:
            return 0.0

        total_penalty = 0.0

        for _, injury_row in team_injuries.iterrows():
            player = str(injury_row["player"]).strip()
            status = str(injury_row["status"]).strip()
            
            # Only penalize for "Out" and "Day-To-Day" statuses
            if status not in ["Out", "Day-To-Day"]:
                continue

            # Check if injury is relevant for this game date
            if game_date:
                return_date_str = injury_row.get("estimated_return_date", "")
                if pd.notna(return_date_str) and return_date_str:
                    try:
                        # Parse return date (format: "Jan 15", "Feb 20", etc.)
                        # We'll assume current year or next year based on game_date
                        game_dt = datetime.strptime(game_date, "%Y-%m-%d")
                        
                        # Try to parse the return date with year inference
                        return_str = str(return_date_str).strip()
                        try:
                            # Try with current game year first
                            return_dt = datetime.strptime(f"{return_str} {game_dt.year}", "%b %d %Y")
                        except ValueError:
                            # If that fails, try next year
                            return_dt = datetime.strptime(f"{return_str} {game_dt.year + 1}", "%b %d %Y")
                        
                        # If player is expected back before the game, skip this injury
                        if return_dt < game_dt:
                            continue
                    except (ValueError, TypeError):
                        # If we can't parse the date, assume injury is still relevant
                        pass

            # Get player's score
            player_score = 0.0
            
            # Try to find player score in our lookup
            for team_key in self.team_player_scores:
                if normalized_team in team_key or team_key in normalized_team:
                    if player in self.team_player_scores[team_key]:
                        player_score = self.team_player_scores[team_key][player]
                        break
            
            # If player score is 0, they might not be a significant contributor
            # But we still count them with a small penalty for "Out" status
            if player_score == 0.0 and status == "Out":
                player_score = 5.0  # Small baseline penalty for missing player
            elif status == "Day-To-Day":
                # Day-to-Day players get 50% penalty (they might play)
                player_score *= 0.5

            total_penalty += player_score

        return total_penalty

    def adjust_hss(
        self,
        team_name: str,
        base_hss: float,
        game_date: Optional[str] = None,
        apply_adjustment: bool = True,
    ) -> tuple[float, float]:
        """
        Adjust a team's HSS based on injuries.

        Args:
            team_name: Team name
            base_hss: Base HSS value without injury adjustment
            game_date: ISO date string for the game (optional)
            apply_adjustment: Whether to actually apply the adjustment (for testing)

        Returns:
            Tuple of (adjusted_hss, injury_penalty)
        """
        if not apply_adjustment:
            return base_hss, 0.0

        penalty = self.get_injury_penalty(team_name, game_date)
        
        # Subtract penalty from HSS (injuries weaken the team)
        # We scale the penalty down since HSS values are typically 100-200
        # A major injury (100 player score) should reduce HSS by ~5-10%
        scaled_penalty = penalty * 0.05  # 5% scaling factor
        
        adjusted_hss = base_hss - scaled_penalty
        
        return adjusted_hss, penalty


# Global instance for easy access
_global_adjuster: Optional[InjuryAdjuster] = None


def get_injury_adjuster() -> InjuryAdjuster:
    """Get or create the global InjuryAdjuster instance."""
    global _global_adjuster
    if _global_adjuster is None:
        _global_adjuster = InjuryAdjuster()
    return _global_adjuster
