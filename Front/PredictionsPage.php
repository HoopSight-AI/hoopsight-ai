<?php
include_once 'Content/HTMLhead.php';
include_once 'Content/HTMLheader.php';

require_once 'PredictionsDashboard.php';

$dashboard = new PredictionsDashboard();
echo $dashboard->generateDashboard();

?>
<script>
function showTeamDetails(team) {
    document.querySelectorAll('.team-detail').forEach(function(el){ el.style.display = 'none'; });
    if (!team) return;
    var el = document.getElementById('team-' + team);
    if (el) {
        el.style.display = 'block';
        if (window.renderHoopSightCharts) {
            window.renderHoopSightCharts();
        }
    }
}

// Wire up dropdown on DOM ready
document.addEventListener('DOMContentLoaded', function(){
    var sel = document.getElementById('team-detail-select');
    if (sel) sel.addEventListener('change', function(){ showTeamDetails(this.value); });
});
</script>

<?php include_once 'Content/HTMLfooter.php'; ?>
