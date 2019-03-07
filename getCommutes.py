from __future__ import division
import requests
from pprint import pprint
import json
import sys,getopt
import time
from calendar import timegm
# -> 1236472051
def main(argv):
  startdate = ''
  enddate = ''
  
  try:
     opts, args = getopt.getopt(argv,"hs:e:",["startdate=","enddate="])
  except getopt.GetoptError:
     print 'getStrava.py -s <startdate> -e <enddtate>'
     sys.exit(2)
  for opt, arg in opts:
     if opt == '-h':
        print 'getStrava.py -s <startdate> -e <enddtate>'
        sys.exit()
     elif opt in ("-s", "--startdate"):
        startdate = arg
     elif opt in ("-e", "--enddate"):
        enddate = arg

  utc_time = time.strptime(startdate, "%d/%m/%Y")
  start_epoch_time = timegm(utc_time)


  utc_end_time = time.strptime(enddate, "%d/%m/%Y")
  end_epoch_time = timegm(utc_end_time)

  url = "https://www.strava.com/api/v3/athlete/activities"
  coms = 0 
  privs = 0
  kmcoms = 0
  kmprivs = 0
  # we're paging, I'll rewrite later with the cool python generators (they're 
  #  awesome).
  for p in range(1,10):
    querystring = {"after":start_epoch_time,"per_page":"100","page":p,"before":end_epoch_time}

    headers = {
     'accept': "application/json",
     'authorization': "Bearer <your token>",
     'cache-control': "no-cache",
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    data = json.loads(response.text)
    parsed = json.loads(response.content.decode('utf-8'))


    for ride in data:
     if ride['type'] == 'Ride': 
      avg = ride['average_speed'] * 3.6
      if (ride['commute']):
         commute = 'commute'
      else:
         commute = 'private'
   
      #  before the commute parameter was available, I used to name my rides, 
      #  containing werk.  Since 2018, they're tagged automatically based on 
      #  start/stop geo data from google.  I'll write a post about it later.
      #  I should move the block below into the condition above, but keeping it
      #  for backward compatibility.
      #if 'werk' in (ride['name']).encode('utf-8').lower():
      #   commute = 'commute'
     
      if commute == 'commute':
         coms += 1
         kmcoms += ride['distance']
      else:
         privs += 1
         kmprivs += ride['distance']


  allrides = coms + privs
  allkms = kmcoms + kmprivs
  
  print "Date range: ", startdate, "to",enddate
  
  print "total number of activities: ", str(allrides)
  print "total distance: ", str(round((kmprivs + kmcoms)/1000,2)),'km'

  pcoms = round((coms / allrides) * 100,2)
  print "Total distance commutes: ",str(round(kmcoms/1000,2)), 'km'
  print "Total distance private rides: ",str(round(kmprivs/1000,2)),'km'
  print "Number of commutes: " + str(coms) 
  print "Number of private rides: " + str(privs)
  print "Percent commutes based on number of activities: ", str(pcoms),'%'
  print "Percent commutes based on distance: ", str(round(100-(kmprivs/kmcoms)*100,2)),'%'


if __name__ == "__main__":
   main(sys.argv[1:])
