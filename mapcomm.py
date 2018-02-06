# test code for using web map
# no autonomous vehicle required
# Mike Holden 2018

print ("Here we go!")

import time
import math
import requests

# class to hold info for courses, states, etc.
class LoiterStuff:
     ## current location
     lat = 38.06807841429639	
     lon = -122.23280310630798
     mode='none'
     message = 'no msg'
     
     loitering = False
     time_to_quit = False
     
     ## picture data
     getpix = False
     plat=0
     plon=0
     pmode='none'
     pmsg = 'no message'
          
     def update_n3m0_location(self):
         ## update the boat location
         r=requests.post('http://sailbot.holdentechnology.com/postlatlon.php',data={'b_no':1,'lat':myLoiter.lat,'lon':myLoiter.lon,'mode':myLoiter.mode,'debug':myLoiter.message})
         #print(r.text)

     def get_pic_requests(self):
         ## get data
         r2 = requests.get('http://sailbot.holdentechnology.com/getbuoys.php')          
         thedata=r2.text.split(',')
         myLoiter.plat=float(thedata[8])
         myLoiter.plon=float(thedata[9])
         myLoiter.pmode = thedata[10]
         myLoiter.pmsg = thedata[11]

myLoiter = LoiterStuff()

lasttime = time.time()

# Loop, interrupts are running things now.
while not myLoiter.time_to_quit:
     time.sleep(4)
     #print myLoiter.get_distance_meters(myLoiter.point1,vehicle.location.global_relative_frame)
     # getting parameters is a little buggy
     #print "Param: %s" % vehicle.parameters['WP_RADIUS']
     myLoiter.message = "hello there world"
     myLoiter.mode = "test mode"
     print( time.time())
     dtime=time.time()-lasttime
     
     # update web server with boat location
     myLoiter.update_n3m0_location()

     # check for new command
     myLoiter.get_pic_requests()
     
     # look for new command
     if myLoiter.pmode.find('REQUESTED')>=0:
         print('picture requested')
         getpix=True
         r=requests.post('http://sailbot.holdentechnology.com/postlatlon.php',data={'b_no':2,'lat':myLoiter.plat,'lon':myLoiter.plon,'mode':'Request Received','debug':'Going for picture'})

     

print("Completed")

