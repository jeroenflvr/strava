#!/usr/bin/python
from __future__ import division
import requests
#from pprint import pprint
import json
import sys,getopt
import time
from calendar import timegm

PER_PAGE = 10  
TOKEN = "afd90cd6d25c4c419cffb415aecaa8cd000737d3"
start_date = ''
end_date = ''

url = "https://www.strava.com/api/v3/athlete/activities"
headers = {
 'accept': "application/json",
 'authorization': "Bearer " + TOKEN,
 'cache-control': "no-cache",
}

def get_strava_data(start_date_epoch,end_date_epoch):
  url = "https://www.strava.com/api/v3/athlete/activities"
  data = '1'
  page = 1 
  while True:
    query_string = {"after":start_date_epoch,"per_page":PER_PAGE,"page":page,"before":end_date_epoch}
    response = requests.request("GET", url, headers=headers, params=query_string)
    data = json.loads(response.text)
    parsed = json.loads(response.content.decode('utf-8'))
    for ride in data:
      yield ride

    if len(data) < PER_PAGE:
      break

    page += 1

def parse_rides(strava_data):
    commutes = 0 
    private_rides = 0
    commute_kilometers = 0
    private_ride_kilometers = 0
    for ride in strava_data:
     if ride['type'] == 'Ride':
      if ride['device_watts']:
       print("datum: " + ride['start_date'] + ", watts avg", ride['average_watts'],"afstand:", 
                ride["distance"]/1000, "watts :",ride['weighted_average_watts'], "speed avg:", 
                '%.2f' %((ride['distance']/ride['moving_time'])*3.6), "moving time: ", ride['moving_time'])

      avg = ride['average_speed'] * 3.6
      if (ride['commute']):
         commute = 'commute'
      else:
         commute = 'private'

      if 'werk' in (ride['name']).encode('utf-8').lower():
         commute = 'commute'

      if commute == 'commute':
         commutes += 1
         commute_kilometers += ride['distance']
      else:
         private_rides += 1
         private_ride_kilometers += ride['distance']


    all_rides = commutes + private_rides
    all_kilometers = commute_kilometers + private_ride_kilometers
  
    print "Date range: ", start_date, "to",end_date
  
    print "total number of activities: ", str(all_rides)
    print "total distance: ", str(round((private_ride_kilometers + commute_kilometers)/1000,2)),'km'
  
    commute_percent = round((commutes / all_rides) * 100,2)
    print "Total distance commutes: ",str(round(commute_kilometers/1000,2)), 'km'
    print "Total distance private rides: ",str(round(private_ride_kilometers/1000,2)),'km'
    print "Number of commutes: " + str(commutes)
    print "Number of private rides: " + str(private_rides)
    print "Percent commutes based on number of activities: ", str(commute_percent),'%'
    print "Percent commutes based on distance: ", str(round(100-(private_ride_kilometers/commute_kilometers)*100,2)),'%'
  
def usage(error):
     print 'Usage: getStrava.py -s <startdate> -e <enddtate>'
     if error:
       print "error:", error
       sys.exit(2)
     sys.exit(0) 

def main(arguments):
  try:
     opts, args = getopt.getopt(arguments,"hs:e:",["start_date=","end_date="])
  except getopt.GetoptError as err:
      usage(err)
  if len(opts) < 2:
      usage(None) 
  for opt, arg in opts:
     if opt in ('-h', '--help'):
        usage()
     elif opt in ("-s", "--start_date"):
        global start_date
        start_date = arg
     elif opt in ("-e", "--end_date"):
        global end_date
        end_date = arg


  utc_time = time.strptime(start_date, "%d/%m/%Y")
  start_epoch_time = timegm(utc_time)


  utc_end_time = time.strptime(end_date, "%d/%m/%Y")
  end_epoch_time = timegm(utc_end_time)
  
  parse_rides(get_strava_data(start_epoch_time, end_epoch_time))

if __name__ == "__main__":
   main(sys.argv[1:])
