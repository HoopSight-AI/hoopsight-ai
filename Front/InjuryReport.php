<?php
/**
 * InjuryReport Class
 * Manages injury data display and impact calculations
 */
class InjuryReport
{
    private $injuriesFile;
    private $playerScoresFile;
    private $injuries = [];
    private $playerScores = [];

    public function __construct(
        string $injuriesFile = '../Data_Gathering_&_Cleaning/injuries.csv',
        string $playerScoresFile = '../Data_Gathering_&_Cleaning/individual_player_scores.csv'
    ) {
        $this->injuriesFile = $injuriesFile;
        $this->playerScoresFile = $playerScoresFile;
        $this->loadData();
    }

    private function loadData(): void
    {
        // Load injuries
        if (file_exists($this->injuriesFile)) {
            $rows = array_map('str_getcsv', file($this->injuriesFile));
            $header = array_shift($rows);
            foreach ($rows as $row) {
                $this->injuries[] = [
                    'team' => $row[0] ?? '',
                    'player' => $row[1] ?? '',
                    'position' => $row[2] ?? '',
                    'return_date' => $row[3] ?? '',
                    'status' => $row[4] ?? '',
                    'comment' => $row[5] ?? ''
                ];
            }
        }

        // Load player scores
        if (file_exists($this->playerScoresFile)) {
            $rows = array_map('str_getcsv', file($this->playerScoresFile));
            $header = array_shift($rows);
            foreach ($rows as $row) {
                $team = $row[0] ?? '';
                $player = $row[1] ?? '';
                $score = floatval($row[3] ?? 0);
                
                if (!isset($this->playerScores[$team])) {
                    $this->playerScores[$team] = [];
                }
                $this->playerScores[$team][$player] = $score;
            }
        }
    }

    /**
     * Get injuries for a specific team
     */
    public function getTeamInjuries(string $teamName): array
    {
        $teamInjuries = [];
        foreach ($this->injuries as $injury) {
            // Match full name or partial name
            if (stripos($injury['team'], $teamName) !== false || 
                stripos($teamName, $injury['team']) !== false) {
                
                // Add player score if available
                $playerScore = 0;
                foreach ($this->playerScores as $team => $players) {
                    if (stripos($team, $teamName) !== false) {
                        if (isset($players[$injury['player']])) {
                            $playerScore = $players[$injury['player']];
                            break;
                        }
                    }
                }
                
                $injury['player_score'] = $playerScore;
                $injury['impact'] = $this->calculateImpact($injury['status'], $playerScore);
                $teamInjuries[] = $injury;
            }
        }
        return $teamInjuries;
    }

    /**
     * Calculate HSS impact from injury
     */
    private function calculateImpact(string $status, float $playerScore): float
    {
        $penalty = 0;
        
        if ($status === 'Out') {
            $penalty = $playerScore;
        } elseif ($status === 'Day-To-Day') {
            $penalty = $playerScore * 0.5; // 50% penalty for questionable
        }
        
        // Scale penalty (same as Python model: 5%)
        return $penalty * 0.05;
    }

    /**
     * Get total injury impact for a team
     */
    public function getTeamInjuryImpact(string $teamName): float
    {
        $injuries = $this->getTeamInjuries($teamName);
        $totalImpact = 0;
        
        foreach ($injuries as $injury) {
            $totalImpact += $injury['impact'];
        }
        
        return $totalImpact;
    }

    /**
     * Generate HTML for injury report
     */
    public function generateInjuryReport(string $teamName): string
    {
        $injuries = $this->getTeamInjuries($teamName);
        
        if (empty($injuries)) {
            return "<div class='injury-report healthy'>
                        <h3>✓ No Current Injuries</h3>
                        <p>Team is at full strength</p>
                    </div>";
        }

        $totalImpact = $this->getTeamInjuryImpact($teamName);
        
        $html = "<div class='injury-report'>";
        $html .= "<h3>⚕️ Injury Report</h3>";
        $html .= "<p class='injury-impact'>Total HSS Impact: <strong>-" . number_format($totalImpact, 2) . "</strong></p>";
        $html .= "<table class='injury-table'>";
        $html .= "<thead><tr>
                    <th>Player</th>
                    <th>Position</th>
                    <th>Status</th>
                    <th>Player Impact</th>
                    <th>HSS Penalty</th>
                  </tr></thead><tbody>";
        
        foreach ($injuries as $injury) {
            $statusClass = strtolower($injury['status']);
            $statusClass = str_replace('-', '', $statusClass);
            
            $html .= "<tr>";
            $html .= "<td><strong>" . htmlspecialchars($injury['player']) . "</strong></td>";
            $html .= "<td>" . htmlspecialchars($injury['position']) . "</td>";
            $html .= "<td><span class='status-badge status-{$statusClass}'>" . 
                     htmlspecialchars($injury['status']) . "</span></td>";
            $html .= "<td>" . number_format($injury['player_score'], 1) . "</td>";
            $html .= "<td class='penalty'>-" . number_format($injury['impact'], 2) . "</td>";
            $html .= "</tr>";
        }
        
        $html .= "</tbody></table>";
        $html .= "<p class='injury-note'>💡 <em>Out = Full penalty | Day-To-Day = 50% penalty</em></p>";
        $html .= "</div>";
        
        return $html;
    }

    /**
     * Generate injury summary badge for main table
     */
    public function getInjuryBadge(string $teamName): string
    {
        $injuries = $this->getTeamInjuries($teamName);
        $count = count($injuries);
        $impact = $this->getTeamInjuryImpact($teamName);
        
        if ($count === 0) {
            return "<span class='injury-badge healthy' title='No injuries'>✓</span>";
        }
        
        $severity = 'minor';
        if ($impact > 10) {
            $severity = 'severe';
        } elseif ($impact > 5) {
            $severity = 'moderate';
        }
        
        return "<span class='injury-badge {$severity}' title='{$count} injured, -{$impact} HSS'>⚕️ {$count}</span>";
    }
}
