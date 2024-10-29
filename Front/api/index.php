<?php
// api/index.php
$request_uri = $_SERVER['REQUEST_URI'];

// Include the necessary files from Front directory
include_once dirname(__FILE__) . "/../Front/Content/HTMLhead.php";
include_once dirname(__FILE__) . "/../Front/Content/HTMLheader.php";

echo "<span>Hello. Welcome to the development version of the HoopSight AI websight!</span>";
?>
<ul>
    <h3>TODO:</h3>
    <li>Get a basic outline of what the interface should look like</li>
    <li>Website map</li>
    <li>Decide on a color scheme</li>
</ul>
<?php 
include_once dirname(__FILE__) . "/../Front/Content/HTMLfooter.php"; 
?>
