# n3m0
🚤 Autonomous boat payload computer 
This project lets the autonomous boat n3m0 be controlled by a python script running on an onboard raspberry pi payload computer.

The directory "map web server" has files for a web server that displays n3m0's position on a map,
and also allows the user to request a service at a location by clicking on that location.
The locations of the request and the boat are stored in a mysql database.  
There are files here that allow the contents of the database to be updated, please play nice.

The directory "payloadcode" is the python script that runs on the boat.  
The raspberry pi's hardware serial port is wired to the telemetry port of an ardupilot (APM) autopilot.
In this case the APM is running the rover firmware but this might work with other vehicles.

This project is very much a work-in-progress, don't expect it all to work perfectly or stop changing until this note is updated.