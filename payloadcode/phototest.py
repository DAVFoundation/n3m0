print "Here we go!"

# Import DroneKit-Python
from dronekit import connect, VehicleMode, LocationGlobalRelative, LocationGlobal
from pymavlink import mavutil # Needed for command message definitions
from picamera import PiCamera
import time
import math
import requests

# Connect to the Vehicle.
print("\nConnecting to vehicle")
#vehicle = connect(/dev/ttyACM0, wait_ready=True) # pixhawk usb
#vehicle = connect("/dev/ttyUSB0", wait_ready='armed', baud=57600) # telemetry usb
#vehicle = connect("/dev/ttyUSB0", baud=57600) # telemetry usb
vehicle = connect("/dev/ttyS0", baud=57600) # telemetry usb

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
class PhotoStuff:
     ## Photo point (where to take photo)
     point1 = LocationGlobalRelative(38.0, -122.0, 0)

     ## current location
     lat = 38.06807841429639	
     lon = -122.23280310630798
     mode='none'
     message = 'no msg'
     
     Photoing = False
     time_to_quit = False
     
     ## picture data
     getpix = False
     plat=0
     plon=0
     pmode='none'
     pmsg = 'no message'
     camera = PiCamera()
     
     def update_n3m0_location(self):
         ## update the boat location
         r=requests.post('http://sailbot.holdentechnology.com/postlatlon.php',data={'b_no':1,'lat':myPhoto.lat,'lon':myPhoto.lon,'mode':myPhoto.mode,'debug':myPhoto.message})
         #print(r.text)

     def get_pic_requests(self):
         ## get data
         r2 = requests.get('http://sailbot.holdentechnology.com/getbuoys.php')          
         thedata=r2.text.split(',')
         myPhoto.plat=float(thedata[8])
         myPhoto.plon=float(thedata[9])
         myPhoto.pmode = thedata[10]
         myPhoto.pmsg = thedata[11]
         if (str(myPhoto.pmode).find("REQUESTED") >= 0): # new request, acknowledge.
              r=requests.post('http://sailbot.holdentechnology.com/postlatlon.php',data={
                   'b_no':2,'lat':myPhoto.plat,'lon':myPhoto.plon,'mode':"n3m0 Received",'debug':"need mode change"})
     def take_photo(self, w,h, filename):
          print('taking photo')
          print filename
          
          self.camera.resolution = (w, h)
          #self.camera.resolution = (1920, 1080)
          #self.camera.resolution = (640, 480)
          self.camera.start_preview()
          #time.sleep(2)

          self.camera.capture(filename)

          self.camera.stop_preview()
          print('photo taken')

     def post_photo(self,filename, newname):
          print ('posting photo')
          url = 'http://sailbot.holdentechnology.com/upload.php'
          #url = 'http://httpbin.org/post'
          data={'submit':'Submit','name':'fileToUpload','id':'fileToUpload'}
          files = {'fileToUpload': (newname, open(filename, 'rb'))}

          rr = requests.post(url, data=data, files=files)
          print rr.text

          print('photo posted')

     def deliver_photo(self,filename):
          myPhoto.pmode = "Finished"
          #myPhoto.pmsg = "<a href=\"uploads/"+filename+"\"><img src=\"uploads/" + filename + "\" height=50 ></a>"
          myPhoto.pmsg = "uploads/" + filename
          r=requests.post('http://sailbot.holdentechnology.com/postlatlon.php',data={'b_no':2,'lat':myPhoto.plat,'lon':myPhoto.plon,'mode':myPhoto.pmode,'debug':myPhoto.pmsg})
          print "should be guided now",myPhoto.get_distance_meters(myPhoto.point1,vehicle.location.global_relative_frame)
          print myPhoto.pmsg
          myPhoto.time_to_quit=True
          

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


myPhoto = PhotoStuff()


# Callback when location has changed. 'value' is the updated value
# Mode changing done here.
# myPhoto.Photoing is True when we are heading for a picture point

# also saves current location into myPhoto variables.
def location_callback(self, attr_name, value):
     #print "Location: ", value
     
     ## store data
     myPhoto.lat = vehicle.location.global_relative_frame.lat
     myPhoto.lon = vehicle.location.global_relative_frame.lon
     myPhoto.mode = str(vehicle.mode.name)

     ## check for reaching picture waypoint
     dist = myPhoto.get_distance_meters(myPhoto.point1,vehicle.location.global_relative_frame)

     
     # if reached photo point: take photo, return to auto mode.
     if (dist <= 3.0) and (myPhoto.Photoing):
     #if  (myPhoto.Photoing):
          print "Picture!", dist
          # take photo
          myPhoto.take_photo(1920, 1080,'/home/pi/Desktop/cap.jpg')

          # exit guided mode
          myPhoto.Photoing = False

          # post photo
          fname='n3m0_' + time.strftime("%Y%m%d-%H%M%S") + '.jpg'
          myPhoto.post_photo('/home/pi/Desktop/cap.jpg',fname)
          myPhoto.deliver_photo(fname)

     # continuously check to see if we need to change modes
     # if guided flag set but not guided mode: do guided mode.
     if myPhoto.Photoing:
          myPhoto.mode = str(dist)
          if (str(vehicle.mode.name).find("GUIDED") < 0): # not guided
               myPhoto.point1.lat = myPhoto.plat
               myPhoto.point1.lon = myPhoto.plon
               vehicle.mode = VehicleMode("GUIDED")
               vehicle.simple_goto(myPhoto.point1)
               print "guided mode again: ", str(vehicle.mode.name)
        
     else: #  guided flag not set
          if (str(vehicle.mode.name).find("GUIDED") >= 0): # guided, return to auto mode.
               vehicle.mode = VehicleMode("AUTO")
               print "End guided mode ", str(vehicle.mode.name)

     
#Callback to monitor mode changes. 'value' is the updated value
# If mode changes to "steering" start autonomous action (picture)
# any other mode change cancels autonomous function through this code
def mode_callback(self, attr_name, value):
     print "Mode: ", value
     if str(value).find("STEERING") >=0:
          myPhoto.Photoing = True
          myPhoto.pmode = "UNDERWAY"
          myPhoto.pmsg = "n3m0 received request"
          r=requests.post('http://sailbot.holdentechnology.com/postlatlon.php',data={'b_no':2,'lat':myPhoto.plat,'lon':myPhoto.plon,'mode':myPhoto.pmode,'debug':myPhoto.pmsg})
          print "should be guided now",myPhoto.get_distance_meters(myPhoto.point1,vehicle.location.global_relative_frame)
     else:
          if str(value).find("GUIDED") < 0: #not changed to guided mode
               myPhoto.Photoing = False #let us go back to manual or RTL etc
               print("new mode set, Photoing off")
 

# Add a callback `location_callback` for the `global_frame` attribute.
vehicle.add_attribute_listener('location.global_frame', location_callback)
vehicle.add_attribute_listener('mode', mode_callback)

# Loop, interrupts are running things now.
while not myPhoto.time_to_quit:
     time.sleep(4)
     print myPhoto.get_distance_meters(myPhoto.point1,vehicle.location.global_relative_frame)
     # getting parameters is a little buggy
     #print "Param: %s" % vehicle.parameters['WP_RADIUS']
     
     myPhoto.message = "Working <br>" + myPhoto.message
     myPhoto.mode = str(vehicle.mode.name) + "<br>" + myPhoto.mode
     myPhoto.update_n3m0_location()
     myPhoto.message = " "
     myPhoto.mode = " "

     myPhoto.take_photo(640,480,'/home/pi/Desktop/testcap.jpg')
     myPhoto.post_photo('/home/pi/Desktop/testcap.jpg','tphoto.jpg')
     #fname='Tn3m0_' + time.strftime("%Y%m%d-%H%M%S") + '.jpg'
     #myPhoto.post_photo('/home/pi/Desktop/testcap.jpg',fname)
     #myPhoto.time_to_quit=True
     
     myPhoto.get_pic_requests()

          
# Remove observer - specifying the attribute and previously registered callback function
vehicle.remove_message_listener('location.global_frame', location_callback)
vehicle.remove_message_listener('mode', mode_callback)


# Close vehicle object before exiting script
vehicle.close()

print("Completed")

