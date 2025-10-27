import fs from 'fs/promises';
import path from 'path';

import { getTranslations, unstable_setRequestLocale } from 'next-intl/server';

import { cn } from '@/utils/Helpers';

interface PredictionRecord {
  season: string;
  game_date: string;
  display_date: string;
  game_tipoff_et?: string | null;
  home_team: string;
  home_team_full?: string | null;
  home_team_abbr?: string | null;
  away_team: string;
  away_team_full?: string | null;
  away_team_abbr?: string | null;
  location: string;
  predicted_winner: string;
  predicted_winner_full?: string | null;
  predicted_win_pct: number;
  home_hss: number;
  away_hss: number;
  confidence_gap_pct?: number | null;
  confidence_bucket?: string | null;
  expected_margin?: number | null;
  generated_at: string;
  actual_home_score?: number | null;
  actual_away_score?: number | null;
  actual_winner?: string | null;
  completed: boolean;
  correct?: boolean | null;
  actual_margin?: number | null;
  margin_error?: number | null;
  alignment_bucket?: string | null;
  espn_game_id?: string | null;
  espn_source_url?: string | null;
  espn_home_pct?: number | null;
  espn_away_pct?: number | null;
  espn_favorite_full?: string | null;
  espn_favorite_abbr?: string | null;
  espn_confidence_gap?: number | null;
  espn_model_delta_pct?: number | null;
  espn_alignment?: string | null;
  espn_last_checked?: string | null;
}

interface TeamGame {
  id: string;
  isoDate: string;
  displayDate: string;
  tipoff?: string | null;
  opponent: string;
  opponentFull: string;
  opponentAbbr?: string | null;
  isHome: boolean;
  predictedWinner: string;
  predictedWinnerFull?: string | null;
  predictedWinPct: number;
  confidenceBucket?: string | null;
  expectedMargin?: number | null;
  alignmentBucket?: string | null;
  completed: boolean;
  correct?: boolean | null;
  actualWinner?: string | null;
  actualWinnerFull?: string | null;
  actualMargin?: number | null;
  marginError?: number | null;
  espnHomePct?: number | null;
  espnAwayPct?: number | null;
  espnFavorite?: string | null;
  espnAlignment?: string | null;
  espnDelta?: number | null;
  espnSourceUrl?: string | null;
}

interface TeamSummary {
  team: string;
  teamFull: string;
  teamAbbr?: string | null;
  games: TeamGame[];
  completed: number;
  correct: number;
  accuracy: number;
  upcoming: number;
}

async function loadPredictionHistory(): Promise<PredictionRecord[]> {
  const historyPath = path.resolve(process.cwd(), '..', 'Front', 'CSVFiles', 'prediction_history.json');
  try {
    const raw = await fs.readFile(historyPath, 'utf8');
    const parsed: PredictionRecord[] = JSON.parse(raw);
    return parsed.map((entry) => ({
      ...entry,
      predicted_win_pct: Number(entry.predicted_win_pct ?? 0),
      home_hss: Number(entry.home_hss ?? 0),
      away_hss: Number(entry.away_hss ?? 0),
      confidence_gap_pct: entry.confidence_gap_pct != null ? Number(entry.confidence_gap_pct) : null,
      expected_margin: entry.expected_margin != null ? Number(entry.expected_margin) : null,
      actual_home_score: entry.actual_home_score != null ? Number(entry.actual_home_score) : null,
      actual_away_score: entry.actual_away_score != null ? Number(entry.actual_away_score) : null,
      actual_margin: entry.actual_margin != null ? Number(entry.actual_margin) : null,
      margin_error: entry.margin_error != null ? Number(entry.margin_error) : null,
      espn_home_pct: entry.espn_home_pct != null ? Number(entry.espn_home_pct) : null,
      espn_away_pct: entry.espn_away_pct != null ? Number(entry.espn_away_pct) : null,
      espn_confidence_gap: entry.espn_confidence_gap != null ? Number(entry.espn_confidence_gap) : null,
      espn_model_delta_pct: entry.espn_model_delta_pct != null ? Number(entry.espn_model_delta_pct) : null,
      completed: Boolean(entry.completed),
      correct: entry.correct == null ? null : Boolean(entry.correct),
    }));
  } catch (error) {
    console.warn('Prediction history not available:', error);
    return [];
  }
}

function buildTeamSummaries(records: PredictionRecord[]): TeamSummary[] {
  const teamMap = new Map<string, TeamSummary>();

  const ensureTeam = (teamKey: string, teamFull?: string | null, teamAbbr?: string | null) => {
    if (!teamMap.has(teamKey)) {
      teamMap.set(teamKey, {
        team: teamKey,
        teamFull: teamFull ?? teamKey,
        teamAbbr,
        games: [],
        completed: 0,
        correct: 0,
        accuracy: 0,
        upcoming: 0,
      });
    }
    const summary = teamMap.get(teamKey)!;
    if (!summary.teamAbbr && teamAbbr) {
      summary.teamAbbr = teamAbbr;
    }
    if (summary.teamFull === teamKey && teamFull) {
      summary.teamFull = teamFull;
    }
    return summary;
  };

  records.forEach((record) => {
    const baseId = `${record.game_date}-${record.home_team}-${record.away_team}`;
    const predictedWinnerFull = record.predicted_winner_full ?? record.predicted_winner;
    const actualWinnerFull = record.actual_winner ?? undefined;

    const homeSummary = ensureTeam(record.home_team, record.home_team_full, record.home_team_abbr);
    const awaySummary = ensureTeam(record.away_team, record.away_team_full, record.away_team_abbr);

    const pushGame = (
      summary: TeamSummary,
      opponentFull: string,
      opponentShort: string,
      isHome: boolean,
    ) => {
      const game: TeamGame = {
        id: `${baseId}-${summary.team}`,
        isoDate: record.game_date,
        displayDate: record.display_date,
        tipoff: record.game_tipoff_et,
        opponent: opponentShort,
        opponentFull,
        opponentAbbr: isHome ? record.away_team_abbr : record.home_team_abbr,
        isHome,
        predictedWinner: record.predicted_winner,
        predictedWinnerFull,
        predictedWinPct: record.predicted_win_pct,
        confidenceBucket: record.confidence_bucket,
        expectedMargin: record.expected_margin,
        alignmentBucket: record.alignment_bucket,
        completed: record.completed,
        correct: record.correct,
        actualWinner: record.actual_winner ?? undefined,
        actualWinnerFull,
        actualMargin: record.actual_margin ?? undefined,
        marginError: record.margin_error ?? undefined,
        espnHomePct: record.espn_home_pct ?? undefined,
        espnAwayPct: record.espn_away_pct ?? undefined,
        espnFavorite: record.espn_favorite_full ?? undefined,
        espnAlignment: record.espn_alignment ?? undefined,
        espnDelta: record.espn_model_delta_pct ?? undefined,
        espnSourceUrl: record.espn_source_url ?? undefined,
      };
      summary.games.push(game);
      if (!record.completed) {
        summary.upcoming += 1;
        return;
      }
      summary.completed += 1;
      if (record.correct) {
        summary.correct += 1;
      }
      summary.accuracy = summary.completed ? (summary.correct / summary.completed) * 100 : 0;
    };

    pushGame(homeSummary, record.away_team_full ?? record.away_team, record.away_team, true);
    pushGame(awaySummary, record.home_team_full ?? record.home_team, record.home_team, false);
  });

  return Array.from(teamMap.values()).map((summary) => ({
    ...summary,
    games: summary.games.sort((a, b) => (a.isoDate < b.isoDate ? 1 : a.isoDate > b.isoDate ? -1 : 0)),
    accuracy: summary.completed ? Number(summary.accuracy.toFixed(1)) : 0,
  }));
}

function formatConfidence(t: Awaited<ReturnType<typeof getTranslations>>, bucket?: string | null) {
  if (!bucket) return t('PredictionsPage.confidence_low');
  const key = bucket.toLowerCase();
  if (key === 'high') return t('PredictionsPage.confidence_high');
  if (key === 'medium') return t('PredictionsPage.confidence_medium');
  return t('PredictionsPage.confidence_low');
}

function formatAlignment(t: Awaited<ReturnType<typeof getTranslations>>, bucket?: string | null) {
  if (!bucket) return t('PredictionsPage.alignment_not_available');
  const key = bucket.toLowerCase();
  if (key === 'tight') return t('PredictionsPage.alignment_tight');
  if (key === 'moderate') return t('PredictionsPage.alignment_moderate');
  if (key === 'wide') return t('PredictionsPage.alignment_wide');
  return t('PredictionsPage.alignment_not_available');
}

function formatEspnAlignment(t: Awaited<ReturnType<typeof getTranslations>>, alignment?: string | null) {
  if (!alignment) return t('PredictionsPage.espn_alignment_unknown');
  const key = alignment.toLowerCase();
  if (key === 'agree') return t('PredictionsPage.espn_alignment_agree');
  if (key === 'disagree') return t('PredictionsPage.espn_alignment_disagree');
  return t('PredictionsPage.espn_alignment_unknown');
}

export async function generateMetadata(props: { params: { locale: string } }) {
  const t = await getTranslations({
    locale: props.params.locale,
    namespace: 'PredictionsPage',
  });

  return {
    title: t('meta_title'),
    description: t('meta_description'),
  };
}

const PredictionsPage = async (props: { params: { locale: string } }) => {
  unstable_setRequestLocale(props.params.locale);
  const [t, records] = await Promise.all([
    getTranslations('PredictionsPage'),
    loadPredictionHistory(),
  ]);

  const teamSummaries = buildTeamSummaries(records);
  const totalPredictions = records.length;
  const completedPredictions = records.filter((record) => record.completed).length;
  const correctPredictions = records.filter((record) => record.completed && record.correct).length;
  const pendingPredictions = totalPredictions - completedPredictions;
  const overallAccuracy = completedPredictions
    ? Number(((correctPredictions / completedPredictions) * 100).toFixed(1))
    : 0;
  const espnComparisons = records.filter((record) => record.espn_alignment);
  const espnAgreements = espnComparisons.filter((record) => record.espn_alignment?.toLowerCase() === 'agree').length;
  const espnDisagreements = espnComparisons.filter((record) => record.espn_alignment?.toLowerCase() === 'disagree').length;
  const espnAverageDelta = espnComparisons.length
    ? Number(
        (
          espnComparisons.reduce((acc, record) => acc + Math.abs(record.espn_model_delta_pct ?? 0), 0) /
          espnComparisons.length
        ).toFixed(1),
      )
    : null;

  return (
    <section className="space-y-10 px-3 py-10 lg:px-12">
      <header className="space-y-6 text-center">
        <p className="text-sm uppercase tracking-widest text-muted-foreground">
          {t('season_label', { season: records[0]?.season ?? '2025-26' })}
        </p>
        <h1 className="text-4xl font-semibold tracking-tight sm:text-5xl">
          {t('page_title')}
        </h1>
      </header>

  <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <div className="rounded-xl border bg-card p-5 shadow-sm">
          <p className="text-sm text-muted-foreground">{t('overall_accuracy')}</p>
          <p className="mt-2 text-3xl font-semibold">{overallAccuracy.toFixed(1)}%</p>
          <p className="text-xs text-muted-foreground">{t('completed_predictions', { completed: completedPredictions })}</p>
        </div>
        <div className="rounded-xl border bg-card p-5 shadow-sm">
          <p className="text-sm text-muted-foreground">{t('total_predictions')}</p>
          <p className="mt-2 text-3xl font-semibold">{totalPredictions}</p>
          <p className="text-xs text-muted-foreground">{t('pending_predictions', { pending: pendingPredictions })}</p>
        </div>
        <div className="rounded-xl border bg-card p-5 shadow-sm">
          <p className="text-sm text-muted-foreground">{t('correct_predictions')}</p>
          <p className="mt-2 text-3xl font-semibold">{correctPredictions}</p>
          <p className="text-xs text-muted-foreground">{t('completed_predictions', { completed: completedPredictions })}</p>
        </div>
        <div className="rounded-xl border bg-card p-5 shadow-sm">
          <p className="text-sm text-muted-foreground">{t('pending_predictions_label')}</p>
          <p className="mt-2 text-3xl font-semibold">{pendingPredictions}</p>
          <p className="text-xs text-muted-foreground">{t('next_update_hint')}</p>
        </div>
        <div className="rounded-xl border bg-card p-5 shadow-sm">
          <p className="text-sm text-muted-foreground">{t('espn_alignment_summary')}</p>
          <p className="mt-2 text-3xl font-semibold">
            {espnAgreements}/{espnComparisons.length || 0}
          </p>
          <p className="text-xs text-muted-foreground">
            {t('espn_alignment_details', {
              disagreements: espnDisagreements,
              delta: espnAverageDelta == null ? '—' : espnAverageDelta.toFixed(1),
            })}
          </p>
        </div>
      </div>

      {teamSummaries.length === 0 ? (
        <div className="rounded-xl border bg-card p-10 text-center shadow-sm">
          <p className="text-base text-muted-foreground">{t('no_data')}</p>
        </div>
      ) : (
        <div className="space-y-8">
          <div className="space-y-2">
            <h2 className="text-2xl font-semibold tracking-tight">{t('team_breakdown')}</h2>
            <p className="text-sm text-muted-foreground">{t('team_breakdown_helper')}</p>
          </div>
          <div className="grid gap-6 lg:grid-cols-2">
            {teamSummaries.map((summary) => (
              <article key={summary.team} className="rounded-2xl border bg-card p-6 shadow-sm transition hover:shadow-md">
                <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <h3 className="text-xl font-semibold">{summary.teamFull}</h3>
                    <p className="text-xs uppercase tracking-widest text-muted-foreground">
                      {t('accuracy_label', {
                        accuracy: summary.completed ? summary.accuracy.toFixed(1) : '0.0',
                        record: `${summary.correct}-${summary.completed - summary.correct}`,
                      })}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-muted-foreground">{t('upcoming_badge', { count: summary.upcoming })}</p>
                  </div>
                </div>

                <div className="mt-4 space-y-3">
                  {summary.games.slice(0, 6).map((game) => {
                    const statusClass = game.completed
                      ? game.correct
                        ? 'bg-emerald-500/10 ring-1 ring-emerald-500/40'
                        : 'bg-rose-500/10 ring-1 ring-rose-500/50'
                      : 'bg-muted';
                    return (
                      <div
                        key={game.id}
                        className={cn(
                          'flex flex-col justify-between gap-3 rounded-xl px-4 py-3 text-sm transition sm:flex-row sm:items-center',
                          statusClass,
                        )}
                      >
                        <div className="space-y-1">
                          <p className="font-semibold">
                            {game.displayDate} · {game.isHome ? t('home_label') : t('away_label')} vs {game.opponentFull}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {t('predicted_line', {
                              winner: game.predictedWinnerFull ?? game.predictedWinner,
                              pct: game.predictedWinPct.toFixed(1),
                            })}
                          </p>
                        </div>
                        <div className="text-right text-xs text-muted-foreground">
                          {game.completed ? (
                            <div className="space-y-1">
                              <p className="font-medium text-foreground">
                                {game.actualWinnerFull ?? game.actualWinner}
                              </p>
                              <p>
                                {t('final_margin', {
                                  margin: game.actualMargin == null ? '—' : game.actualMargin,
                                })}
                              </p>
                              <p>{t('alignment_line', { value: formatAlignment(t, game.alignmentBucket) })}</p>
                              {game.espnFavorite ? (
                                <>
                                  <p>
                                    {t('espn_line', {
                                      favorite: game.espnFavorite,
                                      homePct: game.espnHomePct == null ? '—' : game.espnHomePct.toFixed(1),
                                      awayPct: game.espnAwayPct == null ? '—' : game.espnAwayPct.toFixed(1),
                                    })}
                                  </p>
                                  <p>
                                    {t('espn_alignment_line', {
                                      value: formatEspnAlignment(t, game.espnAlignment),
                                    })}
                                  </p>
                                  <p>
                                    {t('espn_delta_line', {
                                      delta: game.espnDelta == null ? '—' : game.espnDelta.toFixed(1),
                                    })}
                                  </p>
                                </>
                              ) : (
                                <p>{t('espn_unavailable')}</p>
                              )}
                            </div>
                          ) : (
                            <div className="space-y-1">
                              <p className="font-medium text-foreground">{t('upcoming')}</p>
                              {game.tipoff ? <p>{t('tipoff_line', { time: game.tipoff })}</p> : null}
                              <p>{t('confidence_line', { value: formatConfidence(t, game.confidenceBucket) })}</p>
                              {game.espnFavorite ? (
                                <>
                                  <p>
                                    {t('espn_line', {
                                      favorite: game.espnFavorite,
                                      homePct: game.espnHomePct == null ? '—' : game.espnHomePct.toFixed(1),
                                      awayPct: game.espnAwayPct == null ? '—' : game.espnAwayPct.toFixed(1),
                                    })}
                                  </p>
                                  <p>
                                    {t('espn_alignment_line', {
                                      value: formatEspnAlignment(t, game.espnAlignment),
                                    })}
                                  </p>
                                  {game.espnDelta != null ? (
                                    <p>
                                      {t('espn_delta_line', {
                                        delta: game.espnDelta.toFixed(1),
                                      })}
                                    </p>
                                  ) : null}
                                </>
                              ) : (
                                <p>{t('espn_unavailable')}</p>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </article>
            ))}
          </div>
        </div>
      )}
    </section>
  );
};

export default PredictionsPage;
