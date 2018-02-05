print "Here we go!"

# Import DroneKit-Python
from dronekit import connect, VehicleMode, LocationGlobalRelative, LocationGlobal
from pymavlink import mavutil # Needed for command message definitions
import time
import math
import requests

# Connect to the Vehicle.
print("\nConnecting to vehicle")
#vehicle = connect(/dev/ttyACM0, wait_ready=True) # pixhawk usb
#vehicle = connect("/dev/ttyUSB0", wait_ready='armed', baud=57600) # telemetry usb
#vehicle = connect("/dev/ttyUSB0", baud=57600) # telemetry usb
vehicle = connect("/dev/ttyS0", baud=57600) # telemetry usb

### begin web server
##class WebPages(object):
##     @cherrypy.expose
##     def index(self):
##          thetext = "location: " + str(vehicle.location.lat)
##          return thetext
##
##cherrypy.quickstart(WebPages())

# Using the ``wait_ready(True)`` waits on :py:attr:`parameters`, :py:attr:`gps_0`,
# :py:attr:`armed`, :py:attr:`mode`, and :py:attr:`attitude`. In practice this usually
# means that all supported attributes will be populated.

# 'parameters'
#vehicle.wait_ready('gps_0','armed','mode','attitude')
vehicle.wait_ready('gps_0')

# Get some vehicle attributes (state)
print "Get some vehicle attribute values:"
print " GPS: %s" % vehicle.gps_0
print " Battery: %s" % vehicle.battery
print " Last Heartbeat: %s" % vehicle.last_heartbeat
print " Is Armable?: %s" % vehicle.is_armable
print " System status: %s" % vehicle.system_status.state
print " Mode: %s" % vehicle.mode.name    # settable

# class to hold info for courses, states, etc.
class LoiterStuff:
     point1 = LocationGlobalRelative(37.99657, -122.0902786, 20)
     loitering = False
     time_to_quit = False
     
     def get_location_meters(self,original_location, dNorth, dEast):
         """
         Returns a LocationGlobal object containing the latitude/longitude `dNorth` and `dEast` metres from the 
         specified `original_location`. The returned LocationGlobal has the same `alt` value
         as `original_location`.

         The function is useful when you want to move the vehicle around specifying locations relative to 
         the current vehicle position.

         The algorithm is relatively accurate over small distances (10m within 1km) except close to the poles.

         For more information see:
         http://gis.stackexchange.com/questions/2951/algorithm-for-offsetting-a-latitude-longitude-by-some-amount-of-meters
         """
         earth_radius = 6378137.0 #Radius of "spherical" earth
         #Coordinate offsets in radians
         dLat = dNorth/earth_radius
         dLon = dEast/(earth_radius*math.cos(math.pi*original_location.lat/180))

         #New position in decimal degrees
         newlat = original_location.lat + (dLat * 180/math.pi)
         newlon = original_location.lon + (dLon * 180/math.pi)
         print("llatlon" )
         if type(original_location) is LocationGlobal:
             targetlocation=LocationGlobal(newlat, newlon,original_location.alt)
         elif type(original_location) is LocationGlobalRelative:
             targetlocation=LocationGlobalRelative(newlat, newlon,original_location.alt)
         else:
             raise Exception("Invalid Location object passed")
             
         return targetlocation;


     def get_distance_meters(self, aLocation1, aLocation2):
         """
         Returns the ground distance in metres between two LocationGlobal objects.

         This method is an approximation, and will not be accurate over large distances and close to the 
         earth's poles. It comes from the ArduPilot test code: 
         https://github.com/diydrones/ardupilot/blob/master/Tools/autotest/common.py
         """
         dlat = aLocation2.lat - aLocation1.lat
         dlong = aLocation2.lon - aLocation1.lon
         return math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5


     def get_bearing(self, aLocation1, aLocation2):
         """
         Returns the bearing between the two LocationGlobal objects passed as parameters.

         This method is an approximation, and may not be accurate over large distances and close to the 
         earth's poles. It comes from the ArduPilot test code: 
         https://github.com/diydrones/ardupilot/blob/master/Tools/autotest/common.py
         """	
         off_x = aLocation2.lon - aLocation1.lon
         off_y = aLocation2.lat - aLocation1.lat
         bearing = 90.00 + math.atan2(-off_y, off_x) * 57.2957795
         if bearing < 0:
             bearing += 360.00
         return bearing;


myLoiter = LoiterStuff()


#Callback to print the location in global frames. 'value' is the updated value
def location_callback(self, attr_name, value):
     #print "Location: ", value
     dist = myLoiter.get_distance_meters(myLoiter.point1,vehicle.location.global_relative_frame)
     if (dist > 3) and (myLoiter.loitering):
          print "moved: ", dist
          if (str(vehicle.mode.name).find("GUIDED") < 0): #not guided
               vehicle.mode = VehicleMode("GUIDED")
               vehicle.simple_goto(myLoiter.point1)
               print "guided mode again: ", str(vehicle.mode.name)
##     else:
##          if (dist <=3):
##               print "done guiding"
##               vehicle.mode = VehicleMode("HOLD")
##	xmlhttp.open("POST","postlatlon.php",true);
##	xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
##	var postdata = "lat=" + geodata.coords.latitude + "&lon=" + geodata.coords.longitude;
##	xmlhttp.send(postdata);

     
#Callback to monitor mode changes. 'value' is the updated value
def mode_callback(self, attr_name, value):
     print "Mode: ", value
     if str(value).find("STEERING") >=0:
          vehicle.mode = VehicleMode("GUIDED")
          print("Loitering mode entered")
##          msg = vehicle.message_factory.statustext_encode(6,"hello world")
##          vehicle.send_mavlink(msg)          
          #myLoiter.point1 = vehicle.location.global_relative_frame
          myLoiter.point1 = myLoiter.get_location_meters(vehicle.location.global_relative_frame,0,5)
          vehicle.simple_goto(myLoiter.point1)
          myLoiter.loitering = True
          print "should be guided now",myLoiter.get_distance_meters(myLoiter.point1,vehicle.location.global_relative_frame)
     else:
          if str(value).find("GUIDED") < 0: #not changed to guided mode
               myLoiter.loitering = False #let us go back to manual or RTL etc
               print("new mode set, loitering off")
 

# Add a callback `location_callback` for the `global_frame` attribute.
vehicle.add_attribute_listener('location.global_frame', location_callback)
vehicle.add_attribute_listener('mode', mode_callback)

# Loop, interrupts are running things now.
while not myLoiter.time_to_quit:
     time.sleep(4)
     print myLoiter.get_distance_meters(myLoiter.point1,vehicle.location.global_relative_frame)
     # getting parameters is a little buggy
     #print "Param: %s" % vehicle.parameters['WP_RADIUS']
     debugstr = "hello there world"
     modestr = str(vehicle.mode.name)
     r=requests.post('http://sailbot.holdentechnology.com/postlatlon.php',data={'lat':vehicle.location.global_relative_frame.lat,'lon':vehicle.location.global_relative_frame.lon,'mode':modestr,'debug':debugstr})
     #print(r.text)

          
# Remove observer - specifying the attribute and previously registered callback function
vehicle.remove_message_listener('location.global_frame', location_callback)
vehicle.remove_message_listener('mode', mode_callback)


# Close vehicle object before exiting script
vehicle.close()

print("Completed")

