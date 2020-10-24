#!/usr/bin/env python3

############################################################################################################
#
# Created by Skip McGee for DJC2 20.2 AKA "The Looters" on 20201020.
#
# Ever need want to check if the distant end of a satellite connection is masking equipment
# problems as "weather problems"?
#
# This application is designed to display the current weather at your location + the current weather
# at a second location of your choosing (like for hub/spoke satellite sites, etc.). Leave this application
# running in your COC and it also provides a helpful network checker to can inform you of significant
# network interruptions / issues.
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
from tkinter import *
import requests
import json
import datetime
from PIL import ImageTk, Image
import pytz
from pycountry_convert import country_alpha2_to_country_name

# <script src="https://www.yr.no/place/Italy/Campania/Lago_di_Patria/external_box_hour_by_hour.js"></script><noscript><a href="https://www.yr.no/place/Italy/Campania/Lago_di_Patria/">yr.no: Forecast for Lago di Patria</a></noscript>

# HTML for the above: document.write('\n'
#  + '<iframe src="https://www.yr.no/place/Italy/Campania/Lago_di_Patria/external_box_hour_by_hour.html" width="850" height="430" frameborder="0" style="margin: 10px 0 10px 0" scrolling="no">\n'
#  + '</iframe>\n'
# );
#def infoscraper(url):
#    error_count = 0
#    try:
#        json_url = "https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=40.9369&lon=14.0334&altitude=15"
#        page = requests.get(json_url)
#        soup = BeautifulSoup(page.content, 'html.parser')

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
    def error_message(self, error, level=4):
        error = error
        self.error_count += 1
        current_time = datetime.datetime.now()
        error = {f"'error':{error}", f"'time':{current_time}", f"'severity':{level}"}
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
        logging.warning(errormessage)

    # Identifies application completion and records the total number of errors encountered
    def log_message_end(self):
        self.end_time = datetime.datetime.today()
        self.runtime = self.end_time - self.start_time
        end_message = f"Ending: {self.application_name}, 'end_time'={self.end_time}, 'run_time'={self.runtime};"
        print(end_message)
        print(self.log_message_errorsum)
        logging.info(self.log_message_errorsum)
        logging.info(end_message)

##### Division between Classes identified for increased visibility when editing


class cityweather(LogFormatter):
    def __init__(self, current_city="Aqaba, JO", sat_city="Lago Patria, IT"):
        """ Need to really work on the documentation of this app one day """
        super().__init__()
        self.init_counter = True
        self.button1 = False
        self.button2 = False
        self.log_message_begin()
        self.w = 460
        self.l = 580
        self.current_city = current_city
        self.sat_city = sat_city

    def big_timer(self):
        # 15 min timer for updating weather info
        time.sleep(900)


    def app_setup(self, button1=False, button2=False):
        try:
            weatherapp = Tk()
            weatherapp.title("DJC2 20.2 'The Looters' Weather App")
            weatherapp.geometry(f"{self.w}x{self.l}")
            weatherapp['background'] = "white"

            # TF 51/1 Logo Image
            logo = ImageTk.PhotoImage(Image.open('logo.png'))
            panel = Label(weatherapp, bg='white', image=logo)
            panel.place(x=(self.w/2)-50, y=(self.l/2)-30)

            # Labels for Entry Fields
            textlabel1 = Label(weatherapp, font=("Helvetica", 15), justify="left", bg="light gray", text="Current Location:")
            textlabel2 = Label(weatherapp, font=("Helvetica", 15), justify="left", bg="light gray",text="Distant Location:")
            textlabel1.grid(row=0, column=0, sticky=W+E+N+S)
            textlabel2.grid(row=1, column=0, sticky=W+E+N+S)

            # Current City Search
            city1_name = StringVar()
            city1_entry = Entry(weatherapp, font=("Helvetica", 15), justify="left", bg="white", fg='gray', textvariable=city1_name, width=30)
            city1_entry.grid(row=0, column=1, ipadx=0, ipady=4, sticky=N+W)


            # Sat City Search
            city2_name = StringVar()
            city2_entry = Entry(weatherapp, font=("Helvetica", 15), justify="left", bg="white", fg='gray', textvariable=city2_name, width=30)
            city2_entry.grid(row=1, column=1, ipadx=0, ipady=4, sticky=W+N)

            if self.init_counter == True:
                city1_entry.insert(0, self.current_city)
                city2_entry.insert(0, self.sat_city)

            def city_info():
                utc = pytz.timezone('UTC')
                # API Call
                api_key = "x"
                cur_api_request = requests.get("https://api.openweathermap.org/data/2.5/weather?q="
                                                    + city1_entry.get() + "&units=imperial&appid=" + api_key)
                cur_api = json.loads(cur_api_request.content)
                sat_api_request = requests.get("https://api.openweathermap.org/data/2.5/weather?q="
                                                + city2_entry.get() + "&units=imperial&appid=" + api_key)
                sat_api = json.loads(sat_api_request.content)

                # Current City Temperatures
                z = cur_api['main']
                current_temperature1 = z['temp']
                humidity1 = z['humidity']
                tempmin1 = z['temp_min']
                tempmax1 = z['temp_max']

                # Current City Icon
                y = cur_api['weather']
                icon1 = [dict['icon'] for dict in y]
                descrip1 = ', '.join([dict['description'] for dict in y]).title()
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
                cur_sunrise = utc.localize(cur_sunrise)
                cur_sunset = v['sunset']
                cur_sunset = datetime.datetime.fromtimestamp(cur_sunset)
                cur_sunset = utc.localize(cur_sunset)

                # Current Timezone via offset and dict search
                cur_timeoffset = cur_api['timezone']
                cur_timeoffset = datetime.timedelta(seconds=cur_timeoffset)
                cur_now = datetime.datetime.now(pytz.utc)
                cur_countryname = country_alpha2_to_country_name(country1)
                if cur_countryname == "United States":
                    cur_countryname = 'America'
                cur_offset_matches = [tz.zone for tz in map(pytz.timezone, pytz.all_timezones_set) if cur_now.astimezone(tz).utcoffset() == cur_timeoffset]
                if len(cur_offset_matches) > 1:
                    cur_firstchoice = []
                    try:
                        print(f'searching for {citi1}')
                        cur_firstchoice += [listitem for listitem in cur_offset_matches if citi1 in listitem]
                    except:
                        pass
                    try:
                        print(f'searching for {country1}')
                        cur_firstchoice += [listitem for listitem in cur_offset_matches if country1 in listitem]
                    except:
                        pass
                    try:
                        print(f'searching for {cur_countryname}')
                        cur_firstchoice += [listitem for listitem in cur_offset_matches if cur_countryname in listitem]
                    except:
                        pass
                    if len(cur_firstchoice) == 0:
                        cur_firstchoice = cur_offset_matches
                    print(f'available timezones: {cur_firstchoice}')
                    cur_zone = ''.join(cur_firstchoice[0])
                    print(f'picked timezone: {cur_zone}')
                else:
                    cur_zone = ''.join(cur_offset_matches)
                cur_zone = pytz.timezone(cur_zone)

                # Current Date
                cur_dt = cur_api['dt']

                # Current Date & Time converted from UNIX timestamp to UTC and then to Local
                cur_dt = datetime.datetime.fromtimestamp(cur_dt)
                cur_utc_dt = cur_dt.astimezone(utc)
                cur_dt = cur_utc_dt.astimezone(cur_zone)
                cur_date = cur_dt.strftime('%d %B, %Y')
                cur_time = cur_dt.strftime('%H:%M (%p)')

                # Satellite City Temperatures
                a = sat_api['main']
                current_temperature2 = a['temp']
                humidity2 = a['humidity']
                tempmin2 = a['temp_min']
                tempmax2 = a['temp_max']

                # Satellite City Icon
                b = sat_api['weather']
                icon2 = [dict['icon'] for dict in b]
                descrip2 = ', '.join([dict['description'] for dict in b]).title()
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
                sat_sunrise = utc.localize(sat_sunrise)
                sat_sunset = d['sunset']
                sat_sunset = datetime.datetime.fromtimestamp(sat_sunset)
                sat_sunset = utc.localize(sat_sunset)

                # Satellite City
                citi2 = sat_api['name']

                # Satellite Timezone via offset and dict search
                sat_timeoffset = sat_api['timezone']
                sat_timeoffset = datetime.timedelta(seconds=sat_timeoffset)
                sat_now = datetime.datetime.now(pytz.utc)
                sat_countryname = country_alpha2_to_country_name(country2)
                if sat_countryname == 'United States':
                    sat_countryname = 'America'
                sat_offset_matches = [tz.zone for tz in map(pytz.timezone, pytz.all_timezones_set) if sat_now.astimezone(tz).utcoffset() == sat_timeoffset]
                if len(sat_offset_matches) > 1:
                    sat_firstchoice = []
                    try:
                        print(f'searching for {citi2}')
                        sat_firstchoice += [listitem for listitem in sat_offset_matches if citi2 in listitem]
                    except:
                        pass
                    try:
                        print(f'searching for {country2}')
                        sat_firstchoice += [listitem for listitem in sat_offset_matches if country2 in listitem]
                    except:
                        pass
                    try:
                        print(f'searching for {sat_countryname}')
                        sat_firstchoice += [listitem for listitem in sat_offset_matches if sat_countryname in listitem]
                    except:
                        pass
                    if len(sat_firstchoice) == 0:
                        sat_firstchoice = sat_offset_matches
                    print(f'available timezones: {sat_firstchoice}')
                    sat_zone = ''.join(sat_firstchoice[0])
                    print(f'picked timezone: {sat_zone}')
                else:
                    sat_zone = ''.join(sat_offset_matches)
                sat_zone = pytz.timezone(sat_zone)

                # Satellite Date & Time converted from UNIX timestamp to UTC and then to Local
                sat_dt = sat_api['dt']
                sat_dt = datetime.datetime.fromtimestamp(sat_dt)
                sat_utc_dt = sat_dt.astimezone(utc)
                sat_dt = sat_utc_dt.astimezone(sat_zone)
                sat_dt = sat_dt.astimezone(sat_zone)
                sat_date = sat_dt.strftime('%d %B, %Y')
                sat_time = sat_dt.strftime('%H:%M (%p)')

                # Theme for current sun/rain status:
                icon1_img = icon_url1
                icon2_img = icon_url2

                # def get_source(src=icon_url1):
                #     r = requests.get(src)
                #     if r.status_code == 200:
                #         return soup(r.text)
                #     else:
                #         sys.exit( "[~] Invalid Response Received." )
                #
                # def filter(html):
                #     imgs = html.findAll( "img" )
                #     if imgs:
                #         return imgs
                #     else:
                #         sys.exit("[~] No images detected on the page.")
                #
                # def requesthandle(src=icon_url1):
                #     try:
                #         r = requests.get(src, stream=True)
                #         if r.status_code == 200:
                #             r.raw.decode_content = True
                #             with open(name, "wb") as f:
                #                 shutil.copyfileobj(r.raw, f)
                #             print(f"[*] Downloaded Image: {name}")
                #     except Exception as error:
                #         print(f"[~] Error Occured with {name} : {error}")
                #
                # def get_img():
                #     html = get_source()
                #     tag = filter(html)
                #     src = tag.get("img")
                #     if src:
                #         src = src.groups()
                #         img = ImageTk.PhotoImage(Image.open(src))
                #         panel = Label(weatherapp, image=img)
                #         panel.place(x=1, y=200)
                #     else:
                #         img = ImageTk.PhotoImage(Image.open('img_notfound.png'))
                #         panel = Label(weatherapp, image=img)
                #         panel.place(x=1, y=200)


                # Update the information labels
                label_temp1.configure(text=f"Temperature: {current_temperature1}" + '\u00b0')
                label_humidity1.configure(text=f"Humidity: {humidity1}%")
                max_temp1.configure(text="Max Temp Today: " + f"{tempmax1}" + '\u00b0')
                min_temp1.configure(text=f"Min Temp Today: {tempmin1}\u00b0")
                label_lon1.configure(text=f"Longitude: {longitude1}" + '\u00b0')
                label_lat1.configure(text=f"Latitude: {latitude1}"+ '\u00b0')
                label_citi1.configure(text=f"Current: {citi1}, {country1}")
                label_descrip1.configure(text=f"Weather: {descrip1}")
                label_time1.configure(text=f"Time: {cur_time} L")
                label_date1.configure(text=f"{cur_date}")
                #label_icon1.configure(img={icon1_img})

                label_temp2.configure(text=f"Temperature: {current_temperature2}" + '\u00b0')
                label_humidity2.configure(text=f"Humidity: {humidity2}%")
                max_temp2.configure(text="Max Temp Today: " + f"{tempmax2}" + '\u00b0')
                min_temp2.configure(text=f"Min Temp Today: {tempmin2}\u00b0")
                label_lon2.configure(text=f"Longitude: {longitude2}"+ '\u00b0')
                label_lat2.configure(text=f"Latitude: {latitude2}"+ '\u00b0')
                label_citi2.configure(text=f"Distant: {citi2}, {country2}")
                label_descrip2.configure(text=f"Weather: {descrip2}")
                label_time2.configure(text=f"Time: {sat_time} L")
                label_date2.configure(text=f"{sat_date}")
                #label_icon2.configure(img={icon2_img})

                # Image application
                night = ImageTk.PhotoImage(Image.open('night.png'))
                day = ImageTk.PhotoImage(Image.open('day.png'))
                if cur_utc_dt >= cur_sunrise:
                    if cur_utc_dt <= cur_sunset:
                        print("day")
                        day_night1 = day
                    else:
                        print('night1')
                        day_night1 = night
                else:
                    print('night2')
                    day_night1 = night
                if sat_utc_dt >= sat_sunrise:
                    if sat_utc_dt <= sat_sunset:
                        print('day')
                        day_night2 = day
                    else:
                        print('night1')
                        day_night2 = night
                else:
                    print('night2')
                    day_night2 = night
                cur_day_night_panel.image = day_night1
                sat_day_night_panel.image = day_night2


            # Icon Placement
            label_icon1 = Label(weatherapp, width=0, bg='white', font=("bold", 15))
            label_icon1.place(x=3, y=170)
            label_icon2 = Label(weatherapp, width=0, bg='white', font=("bold", 15))
            label_icon2.place(x=((self.w/2)+3), y=170)

            # Country Names and Coordinates
            label_citi1 = Label(weatherapp, width=0, bg='white', font=("bold", 15))
            label_citi1.place(x=3, y=80)
            label_citi2 = Label(weatherapp, width=0, bg='white', font=("bold", 15))
            label_citi2.place(x=((self.w/2)+3), y=80)

            label_lat1 = Label(weatherapp, width=0, bg='white', font=("Helvetica", 15))
            label_lat1.place(x=3, y=110)
            label_lat2 = Label(weatherapp, width=0, bg='white', font=("Helvetica", 15))
            label_lat2.place(x=((self.w/2)+3), y=110)

            label_lon1 = Label(weatherapp, width=0, bg='white', font=("Helvetica", 15))
            label_lon1.place(x=3, y=140)
            label_lon2 = Label(weatherapp, width=0, bg='white', font=("Helvetica", 15))
            label_lon2.place(x=((self.w/2)+3), y=140)

            # Dates
            label_date1 = Label(weatherapp, width=0, bg='white', font=("Helvetica", 15))
            label_date1.place(x=3, y=200)
            label_date2 = Label(weatherapp, width=0, bg='white', font=("Helvetica", 15))
            label_date2.place(x=((self.w/2)+3), y=200)

            # Time
            label_time1 = Label(weatherapp, width=0, bg='white', font=("Helvetica", 15))
            label_time1.place(x=3, y=170)
            label_time2 = Label(weatherapp, width=0, bg='white', font=("Helvetica", 15))
            label_time2.place(x=((self.w/2)+3), y=170)

            # Weather Description
            label_descrip1 = Label(weatherapp, text="ERROR", width=0, bg='white', font=("Helvetica", 15))
            label_descrip1.place(x=3, y=400)
            label_descrip2 = Label(weatherapp, text="ERROR", width=0, bg='white', font=("Helvetica", 15))
            label_descrip2.place(x=((self.w/2)+3), y=400)

            # Current Temperature
            label_temp1 = Label(weatherapp, text="ERROR", width=0, bg='white', font=("Helvetica", 15))
            label_temp1.place(x=3, y=430)
            label_temp2 = Label(weatherapp, text="ERROR", width=0, bg='white', font=("Helvetica", 15))
            label_temp2.place(x=((self.w/2)+3), y=430)

            # Humidity
            label_humidity1 = Label(weatherapp, width=0, bg='white', font=("Helvetica", 15))
            label_humidity1.place(x=3, y=460)
            label_humidity2 = Label(weatherapp, width=0, bg='white', font=("Helvetica", 15))
            label_humidity2.place(x=((self.w/2)+3), y=460)

            # Max Temperature
            max_temp1 = Label(weatherapp, width=0, bg='white', font=("Helvetica", 15))
            max_temp1.place(x=3, y=490)
            max_temp2 = Label(weatherapp, width=0, bg='white', font=("Helvetica", 15))
            max_temp2.place(x=((self.w/2)+3), y=490)

            # Min Temperature
            min_temp1 = Label(weatherapp, width=0, bg='white', font=("Helvetica", 15))
            min_temp1.place(x=3, y=520)
            min_temp2 = Label(weatherapp, width=0, bg='white', font=("Helvetica", 15))
            min_temp2.place(x=((self.w/2)+3), y=520)

            # Note
            note = Label(weatherapp, text="All temperatures in degrees Fahrenheit", bg='white', font=("italic", 10))
            note.place(x=120, y=550)

            # Search Button
            city_nameButton1 = Button(weatherapp, font=("Helvetica", 15), text="Search", command=city_info)
            city_nameButton1.grid(row=0, column=2, padx=0, pady=0, sticky=W+E+N+S)
            city_nameButton2 = Button(weatherapp, font=("Helvetica", 15), text="Search", command=city_info)
            city_nameButton2.grid(row=1, column=2, padx=0, pady=0, sticky=W+E+N+S)

            # Theme for the respective time the application is used
            cur_day_night_panel = Label(weatherapp,  bg='white')
            cur_day_night_panel.place(x=3, y=240)
            sat_day_night_panel = Label(weatherapp,  bg='white')
            sat_day_night_panel.place(x=((self.w / 2) + 3), y=240)


            # Call for default values on application initialization
            if self.init_counter == True:
                city_info()


            # Set the init-counter to False for future use
            self.init_counter = False




            # Need to add a looping thread to conduct a 15 min sleep and then call the api for updated information
            # if button1 == True or button2 ==True:
            #     join()
            #     complete weatherapp loop
            #     start sleep thread again
            # else:
            #     call sleep thread again

            weatherapp.mainloop()

        except ConnectionError as error:
            error = error
            self.error_message(error, level=4)


        except Exception as error:
            self.error_message(error, level=4)
            self.log_message_end()
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
