#!/usr/bin/python3.8

# This script is used to determine when a NW swell will hit Pua'ena Point

import os
import re
import wget
import datetime
import pytz

# First, check to see if an old data file already exists in the working directory
#if os.path.exists('51101.spec'):
#    os.remove('51101.spec')

# This regex will split the data file into usable pieces, see "Regex Group Key" below
wave_data_regex = re.compile(r'(\d{4})\s(\d{2})\s(\d{2})\s(\d{2})\s(\d{2})\s+(\d+\.\d)\s+(\d+\.\d)\s+(\d+\.\d)\s+\d+\.\d\s+\d+\.\d\s+(\S+)\s+(\S+)\s+\S+\s+\d+\.\d+\s+(\d+)')
"""     Regex Group Key:
        group(1) = year
        group(2) = month
        group(3) = day
        group(4) = hour
        group(5) = minute
        group(6) = WVHT (the average height (meters) of the highest one-third of waves)
        group(7) = SwH (swell height, vertical distance (meters) between swell crest and successding trough)
        group(8) = SwP (period, or time it takes successive swell wave crests to pass a fixed point)
        group(9) = SwD (The direction (NWSE) from which the swell waves at the swell wave period (SWPD) are coming)
        group(10) = MWD (The direction (in degrees) from which the waves at the dominant period (DPD) are coming) 
"""
# This regex will split the local_time string, in order to 
local_time_regex = re.compile(r'(\d+)-(\d+)-(\d+)\s(\d+):(\d+)')

site_url = 'https://www.ndbc.noaa.gov/data/realtime2/51101.spec'

print('Downloading wave data from NOAA')
#wget.download(site_url, out='51101.spec')
print('\nDownload complete')
print('Processing Wave Data')

raw_data = open('51101.spec', 'r')

def convert_to_hst_and_add_travel_time(datetime_string, period_string):
    timezone_HST = pytz.timezone('Pacific/Honolulu')
    # convert from string to datetime object
    utc_datetime = datetime.datetime.strptime(datetime_string,'%Y %m %d %H %M %S')
    # localize datetime object to UTC
    utc_datetime = pytz.utc.localize(utc_datetime)
    # convert datetime object from UTC to Pacific/Honolulu
    time_in_hawaii = utc_datetime.astimezone(timezone_HST)
    # add travel time
    distance = 510.0
    period = float(period_string)
    velocity = ((1.56*period)*3600)/1000 # This will give you the speed of the wave in KM / hr
    hour_decimal = distance / velocity
    travel_time = datetime.timedelta(hours=hour_decimal)
    time_in_hawaii = time_in_hawaii + travel_time
    # convert datetime object back to string
    time_in_hawaii_string = str(time_in_hawaii)
    # strip -10:00 from the end of the string
    size = len(time_in_hawaii_string)
    time_in_hawaii_string = time_in_hawaii_string[:size - 16]
    return time_in_hawaii_string

#2022-06-18 20:40:00

for i in range(26):
    line = raw_data.readline().strip('\n')
    if '#' in line:
        # Print out the first 2 lines container the table headers
        print(line)
    else:
        # Print out the rest of the wave data with date/time of when it will hit Waimea Bay Buoy
        mo = wave_data_regex.search(line)
        utc_time_string = ('%s %s %s %s %s 00' % (mo.group(1), mo.group(2), mo.group(3), mo.group(4), mo.group(5)))
        period = mo.group(8)
        local_time = convert_to_hst_and_add_travel_time(utc_time_string, period)
        local_time = local_time.replace('-', ' ')
        print(local_time)
        
#os.remove('51101.spec')
