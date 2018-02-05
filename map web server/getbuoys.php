<?php

// credentials stored elsewhere to make it a little harder to hack the system.
require "database_credentials.php";

$con=mysqli_connect($hostname, $my_user, $my_password, $my_db);

// Check connection
if (mysqli_connect_errno()) {
  echo "Failed to connect to MySQL: " . mysqli_connect_error();
}

$result = mysqli_query($con,"SELECT * FROM buoylatlon");

//echo "<table border='1'>
//<tr>
//<th>Buoy</th>
//<th>Name</th>
//<th>Latitude</th>
//<th>Longitude</th>
//</tr>";
//
//while($row = mysqli_fetch_array($result)) {
//  echo "<tr>";
//  echo "<td>" . $row['Buoy_Number'] . "</td>";
//  echo "<td>" . $row['Buoy_Name'] . "</td>";
//  echo "<td>" . $row['Latitude'] . "</td>";
//  echo "<td>" . $row['Longitude'] . "</td>";
//  echo "</tr>";
//}

while($row = mysqli_fetch_array($result)) {
  echo $row['Buoy_Number'] . ",";
  echo $row['Buoy_Name'] . ",";
  echo $row['Latitude'] . ", ";
  echo $row['Longitude'] . ",";
  echo $row['mode'] . ",";
  echo $row['debug'] . ",";
  echo "<br>";
}

//echo "</table>";

mysqli_close($con);
?>