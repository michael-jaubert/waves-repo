#!/usr/bin/python3.8

# Use to determine when a NW swell will hit the North Shore of O'ahu

import os
import re
import wget
import datetime
import pytz

# Check if an old data file already exists, delete it, then download new data file and open it

if os.path.exists('51101.spec'):
    os.remove('51101.spec')

site_url = 'https://www.ndbc.noaa.gov/data/realtime2/51101.spec'

print('Downloading wave data from NOAA')
wget.download(site_url, out='51101.spec')
print('\nDownload complete')
print('Processing Wave Data')

raw_data = open('51101_static.spec', 'r')

# This regex will split the data file into usable pieces, see "Regex Group Key" below
wave_data_regex = re.compile(r'(\d{4})\s(\d{2})\s(\d{2})\s(\d{2})\s(\d{2})\s+(\d+\.\d)\s+(\d+\.\d)\s+(\d+\.\d)(.+)')
"""     Regex Group Key:
        group(1) = year
        group(2) = month
        group(3) = day
        group(4) = hour
        group(5) = minute
        group(6) = WVHT (the average height (meters) of the highest one-third of waves)
        group(7) = SwH (swell height, vertical distance (meters) between swell crest and successding trough)
        group(8) = SwP (period, or time it takes successive swell wave crests to pass a fixed point)
        group(9) = Rest of string
"""

# This regex will split the local_time string, in order to 
local_time_regex = re.compile(r'(\d+)-(\d+)-(\d+)\s(\d+):(\d+)')


def convert_to_hst_and_add_travel_time(datetime_string, period_string):
    # convert from string to datetime type, localize it, and convert from UTC to Pacific/Honolulu
    timezone_HST = pytz.timezone('Pacific/Honolulu')
    utc_datetime = datetime.datetime.strptime(datetime_string,'%Y %m %d %H %M %S')
    utc_datetime = pytz.utc.localize(utc_datetime)
    time_in_hawaii = utc_datetime.astimezone(timezone_HST)
    # add wave travel time
    distance = 510.0
    period = float(period_string)
    velocity = ((1.56*period)*3600)/1000 # This will give you the speed of the wave in KM / hr
    hour_decimal = distance / velocity
    travel_time = datetime.timedelta(hours=hour_decimal)
    time_in_hawaii = time_in_hawaii + travel_time
    # convert datetime object back to string, strip seconds and microseconds, then return result
    time_in_hawaii_string = str(time_in_hawaii)
    size = len(time_in_hawaii_string)
    time_in_hawaii_string = time_in_hawaii_string[:size - 16]
    return time_in_hawaii_string

def convert_meters_to_feet(height_in_meters):
    height_in_feet = height_in_meters * 3.28084
    height_in_feet = round(height_in_feet, 1)
    return str(height_in_feet)

for i in range(26):
    line = raw_data.readline().strip('\n')
    if '#' in line:
        # print out the first 2 lines, which contain the table headers
        print(line)
    else:
        # print out the rest of the wave data in HST timezone and in feet (right adjusted)
        print(line)
        mo = wave_data_regex.search(line)
        utc_time_string = ('%s %s %s %s %s 00' % (mo.group(1), mo.group(2), mo.group(3), mo.group(4), mo.group(5)))
        period = mo.group(8)
        local_time = convert_to_hst_and_add_travel_time(utc_time_string, period)
        local_time = local_time.replace('-', ' ')
        WVHT = convert_meters_to_feet(float(mo.group(6))).rjust(5)
        SwH = convert_meters_to_feet(float(mo.group(7))).rjust(5)
        period = period.rjust(5)
        rest_of_string = mo.group(9)
        print(local_time + WVHT + SwH + period + rest_of_string)
        
os.remove('51101.spec')
