import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from config import MODEL_VERSION, PREDICTION_HISTORY_JSON
from team_mappings import get_team_identity

ISO_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


def _now_iso() -> str:
    return datetime.now().astimezone().strftime(ISO_FORMAT)


@dataclass
class PredictionRecord:
    season: str
    game_date: str  # ISO date (YYYY-MM-DD)
    display_date: str
    home_team: str
    away_team: str
    location: str
    predicted_winner: str
    predicted_win_pct: float
    home_hss: float
    away_hss: float
    generated_at: str
    model_home_pct: Optional[float] = None
    model_away_pct: Optional[float] = None
    model_version: str = MODEL_VERSION
    game_tipoff_et: Optional[str] = None
    expected_margin: Optional[float] = None
    confidence_gap_pct: Optional[float] = None
    confidence_bucket: Optional[str] = None
    home_team_full: Optional[str] = None
    home_team_abbr: Optional[str] = None
    away_team_full: Optional[str] = None
    away_team_abbr: Optional[str] = None
    predicted_winner_full: Optional[str] = None
    predicted_winner_abbr: Optional[str] = None
    actual_home_score: Optional[int] = None
    actual_away_score: Optional[int] = None
    actual_winner: Optional[str] = None
    completed: bool = False
    correct: Optional[bool] = None
    actual_margin: Optional[int] = None
    margin_error: Optional[float] = None
    alignment_bucket: Optional[str] = None
    espn_game_id: Optional[str] = None
    espn_source_url: Optional[str] = None
    espn_home_pct: Optional[float] = None
    espn_away_pct: Optional[float] = None
    espn_favorite_full: Optional[str] = None
    espn_favorite_abbr: Optional[str] = None
    espn_confidence_gap: Optional[float] = None
    espn_model_delta_pct: Optional[float] = None
    espn_alignment: Optional[str] = None
    espn_last_checked: Optional[str] = None
    last_updated: str = field(default_factory=_now_iso)

    def key(self) -> Tuple[str, str, str, str]:
        return (self.season, self.game_date, self.home_team, self.away_team)

    def to_dict(self) -> Dict[str, object]:
        return {
            "season": self.season,
            "game_date": self.game_date,
            "display_date": self.display_date,
            "game_tipoff_et": self.game_tipoff_et,
            "home_team": self.home_team,
            "home_team_full": self.home_team_full,
            "home_team_abbr": self.home_team_abbr,
            "away_team": self.away_team,
            "away_team_full": self.away_team_full,
            "away_team_abbr": self.away_team_abbr,
            "location": self.location,
            "predicted_winner": self.predicted_winner,
            "predicted_winner_full": self.predicted_winner_full,
            "predicted_winner_abbr": self.predicted_winner_abbr,
            "predicted_win_pct": self.predicted_win_pct,
            "home_hss": self.home_hss,
            "away_hss": self.away_hss,
            "model_home_pct": self.model_home_pct,
            "model_away_pct": self.model_away_pct,
            "confidence_gap_pct": self.confidence_gap_pct,
            "confidence_bucket": self.confidence_bucket,
            "expected_margin": self.expected_margin,
            "generated_at": self.generated_at,
            "model_version": self.model_version,
            "actual_home_score": self.actual_home_score,
            "actual_away_score": self.actual_away_score,
            "actual_winner": self.actual_winner,
            "completed": self.completed,
            "correct": self.correct,
            "actual_margin": self.actual_margin,
            "margin_error": self.margin_error,
            "alignment_bucket": self.alignment_bucket,
            "espn_game_id": self.espn_game_id,
            "espn_source_url": self.espn_source_url,
            "espn_home_pct": self.espn_home_pct,
            "espn_away_pct": self.espn_away_pct,
            "espn_favorite_full": self.espn_favorite_full,
            "espn_favorite_abbr": self.espn_favorite_abbr,
            "espn_confidence_gap": self.espn_confidence_gap,
            "espn_model_delta_pct": self.espn_model_delta_pct,
            "espn_alignment": self.espn_alignment,
            "espn_last_checked": self.espn_last_checked,
            "last_updated": self.last_updated,
        }

    def update_from_dict(self, payload: Dict[str, object]) -> None:
        for key, value in payload.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.last_updated = _now_iso()


class PredictionHistoryManager:
    def __init__(self, season: str, storage_path: Path = PREDICTION_HISTORY_JSON):
        self.season = season
        self.storage_path = storage_path
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._records: Dict[Tuple[str, str, str, str], PredictionRecord] = {}
        self._load()

    def _load(self) -> None:
        if not self.storage_path.exists():
            return
        try:
            with self.storage_path.open("r", encoding="utf-8") as fp:
                payload = json.load(fp)
        except json.JSONDecodeError:
            return
        for row in payload:
            record = PredictionRecord(**row)
            self._records[record.key()] = record

    def prune_before_date(self, cutoff_iso: str) -> None:
        keys_to_remove = [key for key, record in self._records.items() if record.game_date < cutoff_iso]
        for key in keys_to_remove:
            self._records.pop(key, None)

    def _confidence_bucket(self, gap_pct: float) -> str:
        if gap_pct >= 20:
            return "High"
        if gap_pct >= 10:
            return "Medium"
        return "Low"

    def upsert_prediction(
        self,
        *,
        display_date: str,
        iso_date: str,
        home_team: str,
        away_team: str,
        location: str,
        predicted_winner: str,
        predicted_win_pct: float,
        home_hss: float,
        away_hss: float,
        tipoff_et: Optional[str] = None,
        model_home_pct: Optional[float] = None,
        model_away_pct: Optional[float] = None,
    ) -> None:
        try:
            home_full, home_abbr = get_team_identity(home_team)
            away_full, away_abbr = get_team_identity(away_team)
            winner_full, winner_abbr = get_team_identity(predicted_winner)
        except KeyError as exc:
            print(f"Skipping prediction history entry: {exc}")
            return

        if model_home_pct is not None and model_away_pct is not None:
            confidence_gap_pct = abs(model_home_pct - model_away_pct) / 2.0
        else:
            confidence_gap_pct = abs(predicted_win_pct - 50.0)
        expected_margin = round(confidence_gap_pct * 0.4, 2)
        bucket = self._confidence_bucket(confidence_gap_pct)
        generated_at = _now_iso()

        record = PredictionRecord(
            season=self.season,
            game_date=iso_date,
            display_date=display_date,
            game_tipoff_et=tipoff_et,
            home_team=home_team,
            away_team=away_team,
            location=location,
            predicted_winner=predicted_winner,
            predicted_win_pct=round(predicted_win_pct, 3),
            home_hss=round(home_hss, 5),
            away_hss=round(away_hss, 5),
            model_home_pct=round(model_home_pct, 3) if model_home_pct is not None else None,
            model_away_pct=round(model_away_pct, 3) if model_away_pct is not None else None,
            generated_at=generated_at,
            expected_margin=expected_margin,
            confidence_gap_pct=round(confidence_gap_pct, 3),
            confidence_bucket=bucket,
            home_team_full=home_full,
            home_team_abbr=home_abbr,
            away_team_full=away_full,
            away_team_abbr=away_abbr,
            predicted_winner_full=winner_full,
            predicted_winner_abbr=winner_abbr,
        )

        key = record.key()
        existing = self._records.get(key)
        if existing:
            # If game is already completed, do NOT overwrite the prediction
            # This preserves the original prediction that was made before the game
            if existing.completed:
                print(f"  ⚠️  Skipping prediction update for completed game: {home_team} vs {away_team} on {iso_date}")
                return
            
            # Preserve existing actual results but refresh prediction snapshot
            record.actual_home_score = existing.actual_home_score
            record.actual_away_score = existing.actual_away_score
            record.actual_winner = existing.actual_winner
            record.completed = existing.completed
            record.correct = existing.correct
            record.actual_margin = existing.actual_margin
            record.margin_error = existing.margin_error
            record.alignment_bucket = existing.alignment_bucket
            record.last_updated = existing.last_updated
            if existing.model_home_pct is not None and record.model_home_pct is None:
                record.model_home_pct = existing.model_home_pct
            if existing.model_away_pct is not None and record.model_away_pct is None:
                record.model_away_pct = existing.model_away_pct
        self._records[key] = record

    def upsert_actual_results(
        self,
        *,
        iso_date: str,
        home_team: str,
        away_team: str,
        home_score: int,
        away_score: int,
    ) -> None:
        key = (self.season, iso_date, home_team, away_team)
        record = self._records.get(key)
        if not record:
            return

        actual_margin = abs(home_score - away_score)
        predicted_favorite = record.predicted_winner
        actual_winner = home_team if home_score > away_score else away_team
        margin_error = None
        if record.expected_margin is not None:
            margin_error = round(abs(record.expected_margin - actual_margin), 2)
        alignment = None
        if margin_error is not None:
            if margin_error <= 3:
                alignment = "Tight"
            elif margin_error <= 7:
                alignment = "Moderate"
            else:
                alignment = "Wide"

        updated_fields = {
            "actual_home_score": home_score,
            "actual_away_score": away_score,
            "actual_winner": actual_winner,
            "completed": True,
            "correct": actual_winner == predicted_favorite,
            "actual_margin": actual_margin,
            "margin_error": margin_error,
            "alignment_bucket": alignment,
        }
        record.update_from_dict(updated_fields)

    def to_list(self) -> List[Dict[str, object]]:
        payload = [record.to_dict() for record in self._records.values()]
        payload.sort(key=lambda item: (item["game_date"], item["game_tipoff_et"] or ""))
        return payload

    def pending_games(self) -> List[PredictionRecord]:
        return [record for record in self._records.values() if not record.completed]

    def update_espn_prediction(
        self,
        *,
        iso_date: str,
        home_team: str,
        away_team: str,
        game_id: Optional[str],
        source_url: Optional[str],
        home_pct: Optional[float],
        away_pct: Optional[float],
        favorite_full: Optional[str],
        favorite_abbr: Optional[str],
        confidence_gap: Optional[float],
    ) -> None:
        key = (self.season, iso_date, home_team, away_team)
        record = self._records.get(key)
        if not record:
            return

        espn_pct_for_model = None
        model_reference_pct = None
        if record.predicted_winner == home_team:
            espn_pct_for_model = home_pct
            model_reference_pct = record.model_home_pct if record.model_home_pct is not None else record.predicted_win_pct
        elif record.predicted_winner == away_team:
            espn_pct_for_model = away_pct
            model_reference_pct = record.model_away_pct if record.model_away_pct is not None else record.predicted_win_pct

        model_delta = None
        if espn_pct_for_model is not None and model_reference_pct is not None:
            model_delta = round(model_reference_pct - espn_pct_for_model, 3)

        alignment = None
        if favorite_abbr is not None and record.predicted_winner_abbr is not None:
            alignment = "Agree" if favorite_abbr == record.predicted_winner_abbr else "Disagree"

        payload = {
            "espn_game_id": game_id,
            "espn_source_url": source_url,
            "espn_home_pct": home_pct,
            "espn_away_pct": away_pct,
            "espn_favorite_full": favorite_full,
            "espn_favorite_abbr": favorite_abbr,
            "espn_confidence_gap": confidence_gap,
            "espn_model_delta_pct": model_delta,
            "espn_alignment": alignment,
            "espn_last_checked": _now_iso(),
        }
        record.update_from_dict(payload)

    def save(self) -> None:
        with self.storage_path.open("w", encoding="utf-8") as fp:
            json.dump(self.to_list(), fp, ensure_ascii=False, indent=2)