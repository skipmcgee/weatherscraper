#!/usr/bin/env python3

############################################################################################################
#
# Created by Skip McGee for DJC2 20.2 AKA "The Looters" on 20201120.
#
# Ever need want to check if the distant end of a satellite connection is masking equipment
# problems as "weather problems"?
#
# This application is designed to display the current weather at your location + the current weather
# at a second location of your choosing (like for hub/spoke satellite sites, etc.). Note that the
# API this application relieson is updated approximately every 15 minutes.
#
# In order to access the API that we use in this application,
# Browse to: https://openweathermap.org/api
# Under the options, subscribe for the "Free Current Weather". Create an API key.
# Add your key to the "api_key" variable below. Run this little application!
# (Note: If not a "Looter", you could consider changing the application name, logo and default locations.)
#
# This application requires a version of Python > 3.6.0.
#
# Other Useful weather URLs:
# hourly_forecast_url = "https://weather.com/weather/hourbyhour/l/bd6e61a96a73fe700823357bc4695a0342074429b43fdbee1202ed754b361eee"
# json_api_url = "https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=40.9369&lon=14.0334&altitude=15"
#
############################################################################################################

import logging
import logging.handlers
from bs4 import BeautifulSoup
import time
from threading import Thread
import threading
import tkinter as tk
from tkinter import *
from tkinter import messagebox
import requests
import json
import datetime
from PIL import ImageTk, Image
import pytz
from pycountry_convert import country_alpha2_to_country_name
from countryinfo import CountryInfo
import shutil
import concurrent.futures
import queue
from types import SimpleNamespace
from enum import Enum

# <script src="https://www.yr.no/place/Italy/Campania/Lago_di_Patria/external_box_hour_by_hour.js"></script><noscript><a href="https://www.yr.no/place/Italy/Campania/Lago_di_Patria/">yr.no: Forecast for Lago di Patria</a></noscript>
# JS / HTML for the above: document.write('\n' + '<iframe src="https://www.yr.no/place/Italy/Campania/Lago_di_Patria/external_box_hour_by_hour.html" width="850" height="430" frameborder="0" style="margin: 10px 0 10px 0" scrolling="no">\n'  + '</iframe>\n');
# json_url = "https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=40.9369&lon=14.0334&altitude=15"

class LogFormatter(logging.Formatter):
    """ Basic system log message generator to identify significant events and errors for troubleshooting """
    def __init__(self, application_name="DJC2 20.2 'The Looters' Weather App"):
        super().__init__()
        self.application_name = application_name
        self.start_time = datetime.datetime.today()
        self.error_list = []
        self.error_count = 0
        handler = logging.handlers.SysLogHandler()
        formatter = logging.Formatter('%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
        handler.setFormatter(formatter)
        pdfscraper_log = logging.getLogger(__name__)
        pdfscraper_log.setLevel(logging.DEBUG)
        pdfscraper_log.addHandler(handler)

    # Start with a log message identifying application initialization
    def log_message_begin(self):
        begin_message = f"Beginning: {self.application_name}, 'start_time'={self.start_time}, 'originating_process'={__name__};"
        print(begin_message)
        logging.info(begin_message)

    # Logs errors at the specified Severity Level
    def message(self, error, level=4):
        error = error
        self.error_count += 1
        current_time = datetime.datetime.now()
        error = {f"{self.application_name}, 'message':{error}", f"'time':{current_time}", f"'severity':{level}"}
        self.error_list.append(error)
        print(error)
        if level == (5 or 'CRITICAL' or 'critical'):
            logging.critical(error)
        elif level == (4 or 'ERROR' or 'error'):
            logging.error(error)
        elif level == (3 or 'WARN' or 'WARNING' or 'warn' or 'warning'):
            logging.warning(error)
        elif level == (2 or 'INFO' or 'info'):
            logging.info(error)
        elif level == (1 or 'DEBUG' or 'debug'):
            logging.debug(error)

    def log_message_errorsum(self):
        errormessage = f"Sum of errors in {self.application_name}, 'total_error_count'={self.error_count};"
        print(errormessage)
        logging.info(errormessage)

    # Identifies application completion and records the total number of errors encountered
    def log_message_end(self):
        self.end_time = datetime.datetime.today()
        self.runtime = self.end_time - self.start_time
        end_message = f"Ending: {self.application_name}, 'end_time'={self.end_time}, 'run_time'={self.runtime};"
        print(end_message)
        self.log_message_errorsum()
        logging.info(end_message)

''' Division between Classes identified for increased visibility when editing '''


class cityweather(LogFormatter):
    def __init__(self, cur_city="Aqaba, JO", sat_city="Lago Patria, IT"):
        """ Get the current weather displayed in two locations through a tkinter display. """
        super().__init__()
        self.button1 = False
        self.button2 = False
        self.log_message_begin()
        self.w = 460
        self.l = 580
        self.cur_city = cur_city
        self.sat_city = sat_city
        self.api_key = ""
        if self.api_key == "":
            error = "No API Key specified, please add your API key and try again"
            self.message(error, level=4)
            self.log_message_end()
            exit(1)


    def app_setup(self):
        ''' tkinter weather application and setup '''
        print("Building the tkinter mainloop....")
        try:
            weatherapp = Tk()
            weatherapp.title("DJC2 20.2 'The Looters' Weather App")
            weatherapp.geometry(f"{self.w}x{self.l}")
            weatherapp['background'] = "white"
            weatherapp.button = False
            weatherapp.init_counter = True

            # TF 51/1 Logo Image
            logo = ImageTk.PhotoImage(Image.open('logo.png'))
            panel = Label(weatherapp, bg='white', image=logo)
            panel.place(x=(self.w/2)-50, y=(self.l/2)-30)

            # Labels for Entry Fields
            textlabel1 = Label(weatherapp, font=("Helvetica", 12), justify="left", bg="light gray", text="Current Location:")
            textlabel2 = Label(weatherapp, font=("Helvetica", 12), justify="left", bg="light gray",text="Distant Location:")
            textlabel1.grid(row=0, column=0, sticky=W+E+N+S)
            textlabel2.grid(row=1, column=0, sticky=W+E+N+S)

            # Current City Search
            city1_name = StringVar()
            city1_entry = Entry(weatherapp, font=("Helvetica", 12), justify="left", bg="white", fg='gray', textvariable=city1_name, width=29)
            city1_entry.grid(row=0, column=1, ipadx=0, ipady=4, sticky=N+W)

            # Sat City Search
            city2_name = StringVar()
            city2_entry = Entry(weatherapp, font=("Helvetica", 12), justify="left", bg="white", fg='gray', textvariable=city2_name, width=29)
            city2_entry.grid(row=1, column=1, ipadx=0, ipady=4, sticky=W+N)

            if weatherapp.init_counter == True:
                city1_entry.insert(0, self.cur_city)
                city2_entry.insert(0, self.sat_city)

            # Day and night images loading and resizing
            weatherapp.night = ImageTk.PhotoImage(Image.open('night.png'))
            weatherapp.day = ImageTk.PhotoImage(Image.open('day.png'))
            ''' Saving the below code in case you need to resize images on the fly in the future
            This does slow the internal mainloop cycle of tkinter so plan to call outside '''
            # weatherapp.night = Image.open('night.png')
            # weatherapp.night = weatherapp.night.resize((70, 52), Image.ANTIALIAS)
            # weatherapp.night = ImageTk.PhotoImage(weatherapp.night)
            # weatherapp.day = Image.open('day.png')
            # weatherapp.day = weatherapp.day.resize((60, 60), Image.ANTIALIAS)
            # weatherapp.day = ImageTk.PhotoImage(weatherapp.day)

            def cur_city_info():
                ''' Function to define or update the current information for the current or 'cur' city location,
                pulling the recent data from the api '''
                self.cur_city = city1_entry.get()
                print(f"Getting weather data for {self.cur_city}....")
                if weatherapp.init_counter == False:
                    weatherapp.button = True
                utc = pytz.timezone('UTC')
                # API Call
                cur_api_request = requests.get("https://api.openweathermap.org/data/2.5/weather?q="
                                                    + city1_entry.get() + "&units=imperial&appid=" + self.api_key)
                if cur_api_request.status_code != 200:
                    messagebox.showwarning("Weather App Warning", f"Current city API HTTP Status code is "
                                                      f"{cur_api_request.status_code}, resetting to defaults. \n"
                                                      f"Check your spelling and try again.")
                    print(f"Satellite city API HTTP Status code is {cur_api_request.status_code}.")
                    raise KeyError
                else:
                    cur_api = json.loads(cur_api_request.content)

                # Current City Temperatures
                z = cur_api['main']
                current_temperature1 = z['temp']
                humidity1 = z['humidity']
                tempmin1 = z['temp_min']
                tempmax1 = z['temp_max']

                # Current City Icon
                y = cur_api['weather']
                icon1 = [dict['icon'] for dict in y]
                icon1 = ''.join(icon1)
                descrip1 = ', '.join([dict['description'] for dict in y]).title()
                if len(descrip1) >= 18:
                    descrip1 = descrip1[0:15]
                icon_url1 = f"http://openweathermap.org/img/wn/{icon1}@2x.png"

                # Current City Coordinates
                x = cur_api['coord']
                longitude1 = x['lon']
                latitude1 = x['lat']

                # Current City
                citi1 = cur_api['name']

                # Current City Country & daylight information
                v = cur_api['sys']
                country1 = v['country']
                cur_sunrise = v['sunrise']
                cur_sunrise = datetime.datetime.fromtimestamp(cur_sunrise)
                self.cur_sunrise = cur_sunrise
                cur_sunset = v['sunset']
                cur_sunset = datetime.datetime.fromtimestamp(cur_sunset)

                ''' Current Timezone via offset and dict search - note that getting the timezone perfectly right 
                doesn't really matter as long as the offset is correct. However, because precision is important, 
                we will get as reasonably close as possible here without correcting for spaces, colloquial countrynames,
                using state capitals or population centers to identify timezones, etc. '''

                cur_timeoffset = cur_api['timezone']
                cur_timeoffset = datetime.timedelta(seconds=cur_timeoffset)
                cur_now = datetime.datetime.now(pytz.utc)
                cur_countryname = country_alpha2_to_country_name(country1)
                cur_capital = CountryInfo(cur_countryname)
                cur_capital = cur_capital.capital()
                if cur_countryname == 'United States':
                    cur_countryname = 'America'
                cur_offset_matches = [tz.zone for tz in map(pytz.timezone, pytz.all_timezones_set) if cur_now.astimezone(tz).utcoffset() == cur_timeoffset]
                if len(cur_offset_matches) > 1:
                    cur_firstchoice, cur_secondchoice = [], []
                    try:
                        print(f'Searching for {citi1}....')
                        cur_firstchoice += [listitem for listitem in cur_offset_matches if citi1 in listitem]
                    except:
                        pass
                    try:
                        print(f'Searching for {country1}....')
                        cur_firstchoice += [listitem for listitem in cur_offset_matches if country1 in listitem]
                    except:
                        pass
                    if len(cur_firstchoice) == 0:
                        try:
                            print(f'Searching for {cur_capital}....')
                            cur_firstchoice += [listitem for listitem in cur_offset_matches if cur_capital in listitem]
                        except:
                            pass
                    try:
                        print(f'Searching for {cur_countryname}....')
                        cur_firstchoice += [listitem for listitem in cur_offset_matches if cur_countryname in listitem]
                    except:
                        pass
                    if len(cur_firstchoice) >= 2:
                        try:
                            print(f'Searching for {citi1}....')
                            cur_secondchoice += [listitem for listitem in cur_firstchoice if citi1 in listitem]
                            if cur_secondchoice != '':
                                cur_firstchoice.insert(0, cur_secondchoice[0])
                            else:
                                print(f"City {city1} not found.")
                            cur_secondchoice += [listitem for listitem in cur_firstchoice if cur_capital in listitem]
                            if cur_secondchoice != '':
                                cur_firstchoice.insert(0, cur_secondchoice[0])
                            else:
                                print(f"Capital city {cur_capital} not found.")
                        except:
                            pass
                    if len(cur_firstchoice) == 0:
                        cur_firstchoice = cur_offset_matches
                    print(f'Available timezones: {cur_firstchoice}.')
                    cur_zone = ''.join(cur_firstchoice[0])
                    print(f'Picked timezone: {cur_zone}.')
                else:
                    cur_zone = ''.join(cur_offset_matches)
                cur_zone = pytz.timezone(cur_zone)
                cur_sunrise = cur_sunrise.astimezone(cur_zone)
                cur_sunset = cur_sunset.astimezone(cur_zone)

                # Current Date
                cur_dt = cur_api['dt']

                # Current Date & Time converted from UNIX timestamp to UTC and then to Local
                cur_dt = datetime.datetime.fromtimestamp(cur_dt)
                cur_utc_dt = cur_dt.astimezone(utc)
                cur_dt = cur_utc_dt.astimezone(cur_zone)
                cur_date = cur_dt.strftime('%d %B, %Y')
                cur_time = cur_dt.strftime('%H:%M (%p)')

                # Update the information labels
                label_temp1.configure(text=f"Temperature: {current_temperature1}" + '\u00b0')
                label_humidity1.configure(text=f"Humidity: {humidity1}%")
                max_temp1.configure(text="Max Temp Today: " + f"{tempmax1}" + '\u00b0')
                min_temp1.configure(text=f"Min Temp Today: {tempmin1}\u00b0")
                label_lon1.configure(text=f"Longitude: {longitude1}" + '\u00b0')
                label_lat1.configure(text=f"Latitude: {latitude1}"+ '\u00b0')
                label_citi1.configure(text=f"{citi1}, {country1}")
                label_descrip1.configure(text=f"Weather: {descrip1}")
                label_time1.configure(text=f"Local Time: {cur_time}")
                label_date1.configure(text=f"{cur_date}")

                # Download and display the current weather icon
                try:
                    print(f"Trying to download icon from: {icon_url1}.")
                    r = requests.get(icon_url1, stream=True)
                    if r.status_code == 200:
                        r.raw.decode_content = True
                        with open(icon1, "wb") as f:
                            shutil.copyfileobj(r.raw, f)
                        print(f"Downloaded image: {icon1}.")
                        weatherapp.cur_image = ImageTk.PhotoImage(Image.open(icon1))
                    else:
                        print(f"Received HTTP status code {r.status_code} while trying to download {icon1}.")
                        weatherapp.cur_image = ImageTk.PhotoImage(Image.open('img_notfound.jpeg'))
                except Exception as error:
                    print(f"Error occured with downloading {icon1}: {error}.")
                    weatherapp.cur_image = ImageTk.PhotoImage(Image.open('img_notfound.jpeg'))

                # Icon Placement
                label_icon1 = Label(weatherapp, bg='white', image=weatherapp.cur_image)
                label_icon1.place(x=50, y=303)

                # Image application
                if cur_dt >= cur_sunrise:
                    if cur_dt <= cur_sunset:
                        print(f"In {self.cur_city} it is currently daytime.")
                        weatherapp.day_night1 = weatherapp.day
                    else:
                        print(f"In {self.cur_city} it is currently nighttime.")
                        weatherapp.day_night1 = weatherapp.night
                else:
                    print(f"In {self.cur_city} it is currently nighttime.")
                    weatherapp.day_night1 = weatherapp.night

                # Theme for the respective time the application is used
                weatherapp.cur_day_night_panel = Label(weatherapp, bg='white', image=weatherapp.day_night1)
                weatherapp.cur_day_night_panel.place(x=5, y=225)


            def sat_city_info():
                ''' Function to define or update the current information for the remote or 'sat' city location,
                pulling the recent data from the api '''
                self.sat_city = city2_entry.get()
                print(f"Getting weather data for {self.sat_city}....")
                if weatherapp.init_counter == False:
                    weatherapp.button = True
                utc = pytz.timezone('UTC')
                # API Call
                sat_api_request = requests.get("https://api.openweathermap.org/data/2.5/weather?q="
                                                + city2_entry.get() + "&units=imperial&appid=" + self.api_key)
                if sat_api_request.status_code != 200:
                    messagebox.showwarning("Weather App Warning", f"Satellite city API HTTP Status code is "
                                                      f"{sat_api_request.status_code}, resetting to defaults. \n"
                                                      f"Check your spelling and try again.")
                    print(f"Satellite city API HTTP Status code is {sat_api_request.status_code}.")
                    raise KeyError
                else:
                    sat_api = json.loads(sat_api_request.content)

                # Satellite City Temperatures
                a = sat_api['main']
                current_temperature2 = a['temp']
                humidity2 = a['humidity']
                tempmin2 = a['temp_min']
                tempmax2 = a['temp_max']

                # Satellite City Icon
                b = sat_api['weather']
                icon2 = [dict['icon'] for dict in b]
                icon2 = ''.join(icon2)
                descrip2 = ', '.join([dict['description'] for dict in b]).title()
                if len(descrip2) >= 18:
                    descrip2 = descrip2[0:15]
                icon_url2 = f"http://openweathermap.org/img/wn/{icon2}@2x.png"

                # Satellite City Coordinates
                c = sat_api['coord']
                longitude2 = c['lon']
                latitude2 = c['lat']

                # Satellite City Country & daylight information
                d = sat_api['sys']
                country2 = d['country']
                sat_sunrise = d['sunrise']
                sat_sunrise = datetime.datetime.fromtimestamp(sat_sunrise)
                self.sat_sunrise = sat_sunrise
                sat_sunset = d['sunset']
                sat_sunset = datetime.datetime.fromtimestamp(sat_sunset)
                self.sat_sunset = sat_sunset

                # Satellite City
                citi2 = sat_api['name']

                # Satellite Timezone via offset and dict search
                sat_timeoffset = sat_api['timezone']
                sat_timeoffset = datetime.timedelta(seconds=sat_timeoffset)
                sat_now = datetime.datetime.now(pytz.utc)
                sat_countryname = country_alpha2_to_country_name(country2)
                sat_capital = CountryInfo(sat_countryname)
                sat_capital = sat_capital.capital()
                if sat_countryname == 'United States':
                    sat_countryname = 'America'
                sat_offset_matches = [tz.zone for tz in map(pytz.timezone, pytz.all_timezones_set) if sat_now.astimezone(tz).utcoffset() == sat_timeoffset]
                if len(sat_offset_matches) > 1:
                    sat_firstchoice, sat_secondchoice = [], []
                    try:
                        print(f'Searching for {citi2}....')
                        sat_firstchoice += [listitem for listitem in sat_offset_matches if citi2 in listitem]
                    except:
                        pass
                    try:
                        print(f'Searching for {country2}....')
                        sat_firstchoice += [listitem for listitem in sat_offset_matches if country2 in listitem]
                    except:
                        pass
                    if len(sat_firstchoice) == 0:
                        try:
                            print(f'Searching for {sat_capital}....')
                            sat_firstchoice += [listitem for listitem in sat_offset_matches if sat_capital in listitem]
                        except:
                            pass
                    try:
                        print(f'Searching for {sat_countryname}....')
                        sat_firstchoice += [listitem for listitem in sat_offset_matches if sat_countryname in listitem]
                    except:
                        pass
                    if len(sat_firstchoice) >= 2:
                        try:
                            print(f'Searching for {citi2}....')
                            sat_secondchoice += [listitem for listitem in sat_firstchoice if citi2 in listitem]
                            if sat_secondchoice != '':
                                sat_firstchoice.insert(0, sat_secondchoice[0])
                            else:
                                print(f"City {city2} not found!")
                            sat_secondchoice += [listitem for listitem in sat_firstchoice if sat_capital in listitem]
                            if sat_secondchoice != '':
                                sat_firstchoice.insert(0, sat_secondchoice[0])
                            else:
                                print(f"Capital city {sat_capital} not found!")
                        except:
                            pass
                    if len(sat_firstchoice) == 0:
                        sat_firstchoice = sat_offset_matches
                    print(f'Available timezones: {sat_firstchoice}.')
                    sat_zone = ''.join(sat_firstchoice[0])
                    print(f'Picked timezone: {sat_zone}.')
                else:
                    sat_zone = ''.join(sat_offset_matches)
                sat_zone = pytz.timezone(sat_zone)
                sat_sunrise = sat_sunrise.astimezone(sat_zone)
                sat_sunset = sat_sunset.astimezone(sat_zone)

                # Satellite Date & Time converted from UNIX timestamp to UTC and then to Local
                sat_dt = sat_api['dt']
                sat_dt = datetime.datetime.fromtimestamp(sat_dt)
                sat_utc_dt = sat_dt.astimezone(utc)
                sat_dt = sat_utc_dt.astimezone(sat_zone)
                sat_dt = sat_dt.astimezone(sat_zone)
                sat_date = sat_dt.strftime('%d %B, %Y')
                sat_time = sat_dt.strftime('%H:%M (%p)')

                # Update the information labels
                label_temp2.configure(text=f"Temperature: {current_temperature2}" + '\u00b0')
                label_humidity2.configure(text=f"Humidity: {humidity2}%")
                max_temp2.configure(text="Max Temp Today: " + f"{tempmax2}" + '\u00b0')
                min_temp2.configure(text=f"Min Temp Today: {tempmin2}\u00b0")
                label_lon2.configure(text=f"Longitude: {longitude2}"+ '\u00b0')
                label_lat2.configure(text=f"Latitude: {latitude2}"+ '\u00b0')
                label_citi2.configure(text=f"{citi2}, {country2}")
                label_descrip2.configure(text=f"Weather: {descrip2}")
                label_time2.configure(text=f"Local Time: {sat_time}")
                label_date2.configure(text=f"{sat_date}")

                # Download and save the appropriate weather icon
                try:
                    print(f"Trying to download icon from: {icon_url2}.")
                    r = requests.get(icon_url2, stream=True)
                    if r.status_code == 200:
                        r.raw.decode_content = True
                        with open(icon2, "wb") as f:
                            shutil.copyfileobj(r.raw, f)
                        print(f"Downloaded image: {icon2}.")
                        weatherapp.sat_image = ImageTk.PhotoImage(Image.open(icon2))
                    else:
                        print(f"Received HTTP status code {r.status_code} while trying to download {icon2}.")
                        weatherapp.sat_image = ImageTk.PhotoImage(Image.open('img_notfound.jpeg'))
                except Exception as error:
                    print(f"Error occured with downloading {icon2}: {error}.")
                    weatherapp.sat_image = ImageTk.PhotoImage(Image.open('img_notfound.jpeg'))

                # Icon Placement
                label_icon2 = Label(weatherapp, bg='white', image=weatherapp.sat_image)
                label_icon2.place(x=((self.w / 2) + 75), y=303)

                # Image application
                if sat_dt >= sat_sunrise:
                    if sat_dt <= sat_sunset:
                        print(f"In {self.sat_city} it is currently daytime.")
                        weatherapp.day_night2 = weatherapp.day
                    else:
                        print(f"In {self.sat_city} it is currently nighttime.")
                        weatherapp.day_night2 = weatherapp.night
                else:
                    print(f"In {self.sat_city} it is currently nighttime.")
                    weatherapp.day_night2 = weatherapp.night

                # Theme for the respective time the application is used
                weatherapp.sat_day_night_panel = Label(weatherapp, bg='white', image=weatherapp.day_night2)
                weatherapp.sat_day_night_panel.place(x=((self.w / 2) + 35), y=225)


            ''' Defining the break between the data/api calls and the rest of the mainloop for ease of reference '''
            # Country Name Labels
            label_citi1 = Label(weatherapp, width=0, bg='white', font=("bold", 14))
            label_citi1.place(x=3, y=80)
            label_citi2 = Label(weatherapp, width=0, bg='white', font=("bold", 14))
            label_citi2.place(x=((self.w/2)+3), y=80)

            # Latitude Labels
            label_lat1 = Label(weatherapp, width=0, bg='white', font=("Helvetica", 14))
            label_lat1.place(x=3, y=110)
            label_lat2 = Label(weatherapp, width=0, bg='white', font=("Helvetica", 14))
            label_lat2.place(x=((self.w/2)+3), y=110)

            # Longitude Labels
            label_lon1 = Label(weatherapp, width=0, bg='white', font=("Helvetica", 14))
            label_lon1.place(x=3, y=140)
            label_lon2 = Label(weatherapp, width=0, bg='white', font=("Helvetica", 14))
            label_lon2.place(x=((self.w/2)+3), y=140)

            # Date Labels
            label_date1 = Label(weatherapp, width=0, bg='white', font=("Helvetica", 14))
            label_date1.place(x=3, y=200)
            label_date2 = Label(weatherapp, width=0, bg='white', font=("Helvetica", 14))
            label_date2.place(x=((self.w/2)+3), y=200)

            # Time Labels
            label_time1 = Label(weatherapp, width=0, bg='white', font=("Helvetica", 14))
            label_time1.place(x=3, y=170)
            label_time2 = Label(weatherapp, width=0, bg='white', font=("Helvetica", 14))
            label_time2.place(x=((self.w/2)+3), y=170)

            # Weather Description Labels
            label_descrip1 = Label(weatherapp, text="ERROR", width=0, bg='white', font=("Helvetica", 14))
            label_descrip1.place(x=3, y=400)
            label_descrip2 = Label(weatherapp, text="ERROR", width=0, bg='white', font=("Helvetica", 14))
            label_descrip2.place(x=((self.w/2)+3), y=400)

            # Current Temperature Labels
            label_temp1 = Label(weatherapp, text="ERROR", width=0, bg='white', font=("Helvetica", 14))
            label_temp1.place(x=3, y=430)
            label_temp2 = Label(weatherapp, text="ERROR", width=0, bg='white', font=("Helvetica", 14))
            label_temp2.place(x=((self.w/2)+3), y=430)

            # Humidity Labels
            label_humidity1 = Label(weatherapp, width=0, bg='white', font=("Helvetica", 14))
            label_humidity1.place(x=3, y=460)
            label_humidity2 = Label(weatherapp, width=0, bg='white', font=("Helvetica", 14))
            label_humidity2.place(x=((self.w/2)+3), y=460)

            # Max Temperature Labels
            max_temp1 = Label(weatherapp, width=0, bg='white', font=("Helvetica", 14))
            max_temp1.place(x=3, y=490)
            max_temp2 = Label(weatherapp, width=0, bg='white', font=("Helvetica", 14))
            max_temp2.place(x=((self.w/2)+3), y=490)

            # Min Temperature Labels
            min_temp1 = Label(weatherapp, width=0, bg='white', font=("Helvetica", 14))
            min_temp1.place(x=3, y=520)
            min_temp2 = Label(weatherapp, width=0, bg='white', font=("Helvetica", 14))
            min_temp2.place(x=((self.w/2)+3), y=520)

            # Note at the bottom of the application label and definition
            note = Label(weatherapp, text="All temperatures in degrees Fahrenheit", bg='white', font=("italic", 10))
            note.place(x=120, y=550)

            # Wrapper to call the api for the first instance / establish the default values for the application
            print("Initial layout built, over to data input functions....")
            if weatherapp.init_counter == True:
                cur_city_info()
                sat_city_info()


            # Search Button
            city_nameButton1 = Button(weatherapp, font=("Helvetica", 12), text="Search", command=cur_city_info)
            city_nameButton1.grid(row=0, column=2, padx=0, pady=0, sticky=W+E+N+S)
            city_nameButton2 = Button(weatherapp, font=("Helvetica", 12), text="Search", command=sat_city_info)
            city_nameButton2.grid(row=1, column=2, padx=0, pady=0, sticky=W+E+N+S)

            weatherapp.init_counter = False
            print("App functioning, waiting for search button to be pressed.")
            weatherapp.mainloop()

        except ConnectionError as error:
            print("Network connection issue prevents the weatherscraper application from running.")
            self.message(error, level=4)
            time.sleep(10)

        except KeyError as error:
            print("The input location not known, please try again in City, CO format.")
            self.message(error, level=4)

        except KeyboardInterrupt as error:
            print("Exiting properly per user request.")
            self.message(error, level=4)
            self.app_exit()

        except Exception as error:
            print(error)
            self.message(error, level=4)
            self.app_exit()


    def app_exit(self):
        # Final log messages for recording completion and problems
        if self.error_count > 0:
            self.log_message_end()
            exit(1)
        else:
            self.log_message_end()
            exit(0)


def main():
    # Application initialization
    weatherapp = cityweather().app_setup()


# Call the main function
if __name__ == "__main__":
    main()

