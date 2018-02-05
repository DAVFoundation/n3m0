<html>
<body>

buoy number: <?php echo $_POST["b_no"]; ?><br>
lat received: <?php echo $_POST["lat"]; ?><br>
lon received: <?php echo $_POST["lon"]; ?><br>
mode received: <?php echo $_POST["mode"]; ?><br>
debug received: <?php echo $_POST["debug"]; ?><br>



<?php
echo "<br>starting db<br>";
// credentials stored elsewhere to make it a little harder to hack the system.
require "database_credentials.php";

$con=mysqli_connect($hostname, $my_user, $my_password, $my_db);
// Check connection
if (mysqli_connect_errno()) {
  echo "Failed to connect to MySQL: " . mysqli_connect_error();
}


$sql_str = "UPDATE buoylatlon SET Latitude=" . $_POST["lat"] . ",Longitude=" . $_POST["lon"] . ",mode='" . $_POST["mode"] . "',debug='" . $_POST["debug"] . "' WHERE Buoy_Number=" . $_POST["b_no"];
//$sql_str = "UPDATE buoylatlon SET Latitude=37.989, Longitude=-122.05 WHERE Buoy_Number=1";
$result = mysqli_query($con,$sql_str);
//$result = mysqli_query($con,"UPDATE buoylatlon SET Latitude=" . $_POST["lat"] . ",Longitude=" . $_POST["lon"] . " WHERE Buoy_Number=1");
mysqli_close($con);

echo $sql_str;

echo "done sending<br>";
?>

</body>
</html>
