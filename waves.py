#!/usr/bin/python3.8

# This script is used to determine when a NW swell will hit Pua'ena Point

import os
import re
import wget
from datetime import datetime
import pytz

# First, check to see if an old data file already exists in the working directory
if os.path.exists('51101.spec'):
    os.remove('51101.spec')

# This regex will split the data file into usable pieces, see "Regex Group Key" below
wave_data_regex = re.compile(r'(\d{4})\s(\d{2})\s(\d{2})\s(\d{2})\s(\d{2})\s+(.*)')
"""     Regex Group Key:
        group(1) = year
        group(2) = month
        group(3) = day
        group(4) = hour
        group(5) = minute
        group(6) = rest of line
"""
# This regex will split the local_time string, in order to 
local_time_regex = re.compile(r'(\d+)-(\d+)-(\d+)\s(\d+):(\d+)')

site_url = 'https://www.ndbc.noaa.gov/data/realtime2/51101.spec'

print('Downloading wave data from NOAA')
wget.download(site_url, out='51101.spec')
print('\nDownload complete')
print('Processing Wave Data')

raw_data = open('51101.spec', 'r')

def convert_datetime_to_hst(datetime_string):
    timezone_HST = pytz.timezone('Pacific/Honolulu')
    # convert from string to datetime object
    utc_datetime = datetime.strptime(datetime_string,'%Y-%m-%d %H:%M:%S')
    # localize datetime object to UTC
    utc_datetime = pytz.utc.localize(utc_datetime)
    # convert datetime object from UTC to Pacific/Honolulu
    time_in_hawaii = utc_datetime.astimezone(timezone_HST)
    # convert datetime object back to string
    time_in_hawaii_string = str(time_in_hawaii)
    # strip -10:00 from the end of the string
    size = len(time_in_hawaii_string)
    time_in_hawaii_string = time_in_hawaii_string[:size - 9]
    return time_in_hawaii_string

#2022-06-18 20:40:00

for i in range(26):
    line = raw_data.readline().strip('\n')
    if '#' in line:
        # Print out the first 2 lines container the table headers
        print(line)
    else:
        # Print out the rest of the wave data with date/time of when it will hit Waimea Bay Buoy
        print(line) 
        mo = wave_data_regex.search(line)
        utc_time_string = ('%s-%s-%s %s:%s:00' % (mo.group(1), mo.group(2), mo.group(3), mo.group(4), mo.group(5)))
        local_time = convert_datetime_to_hst(utc_time_string)
        print(local_time + '  ' + mo.group(6))
        
#os.remove('51101.spec')
"""
distance = 510 # Distance in KM between 51101 buoy and Pua'ena Point
period = float(input('\nEnter swell period: '))

velocity = ((1.56*period)*3600)/1000 # This will give you the speed of the wave in KM / hr
hour_decimal = distance/ velocity

hours = int(hour_decimal) + h
minutes = ((hour_decimal*60) % 60) + m

if minutes >= 60:
    hours += 1
    minutes -=60

if hours >= 24:
    hours -= 24

"""
