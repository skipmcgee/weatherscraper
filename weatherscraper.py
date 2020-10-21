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
        self.info_error_list = []
        self.warn_error_list = []
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
        error = f"{error}:{datetime.datetime.today()}"
        self.info_error_list.append(error)
        print(error)
        if level == 1 or 'ALERT' or 'alert':
            logging.alert(error)
        elif level == 2 or 'CRITICAL' or 'critical':
            logging.critical(error)
        elif level == 3 or 'ERROR' or 'error':
            logging.error(error)
        elif level == 4 or 'WARN' or 'WARNING' or 'warn' or 'warning':
            logging.warning(error)
        elif level == 5 or 'NOTICE' or 'notice':
            logging.notice(error)
        elif level == 6 or 'INFO' or 'info':
            logging.info(error)
        elif level == 7 or 'DEBUG' or 'debug':
            logging.debug(error)

    # Identifies application completion and records the total number of errors encountered
    def log_message_end(self):
        self.end_time = datetime.datetime.today()
        self.runtime = self.end_time - self.start_time
        end_message = f"Ending: {self.application_name}, 'end_time'={self.end_time}, 'run_time'={self.runtime};"
        print(end_message)
        logging.info(end_message)

    def log_message_errorsum(self):
        errormessage = f"Sum of errors in {self.application_name}, 'total_error_count'={self.errorcount};"
        logging.warning(errormessage)


class cityweather(LogFormatter):
    def __init__(self, current_city='Aqaba', sat_city='Lago Patria'):
        super().__init__()
        self.init_counter = True
        self.sat_city = sat_city
        self.current_city = current_city
        self.button1 = False
        self.button2 = False
        self.log_message_begin()

    def api_call(self, button1=False, button2=False):
        # API Call
        global sat_api_request, cur_api_request, sat_api, cur_api
        self.button1, self.button2 = button1, button2
        api_key = "x"
        if self.init_counter == True:
            sat_api_request = requests.get("https://api.openweathermap.org/data/2.5/weather?q="
                                    + self.sat_city + "&units=imperial&appid=" + api_key)
            cur_api_request = requests.get("https://api.openweathermap.org/data/2.5/weather?q="
                                    + self.current_city + "&units=imperial&appid=" + api_key)
            sat_api = json.loads(sat_api_request.content)
            cur_api = json.loads(cur_api_request.content)
        elif button1 == True:
            cur_api_request = requests.get("https://api.openweathermap.org/data/2.5/weather?q="
                                       + self.current_city + "&units=imperial&appid=" + api_key)
            cur_api = json.loads(cur_api_request.content)
        elif button2 == True:
            sat_api_request = requests.get("https://api.openweathermap.org/data/2.5/weather?q="
                                       + self.sat_city + "&units=imperial&appid=" + api_key)
            sat_api = json.loads(sat_api_request.content)
        else:
            print("Error with api_call() method")
            self.error_count += 1
            self.info_error_list.append(f"{error}:{datetime.datetime.today()}")
            print(error)
            exit(1)

        # Satellite City Temperatures
        a = sat_api['main']
        self.current_temperature1 = a['temp']
        self.humidity1 = a['humidity']
        self.tempmin1 = a['temp_min']
        self.tempmax1 = a['temp_max']

        # Satellite City Icon
        b = sat_api['weather']
        self.icon1 = [dict['icon'] for dict in b]
        self.descrip1 = [dict['description'] for dict in b]
        self.icon_url1 = f"http://openweathermap.org/img/wn/{self.icon1}@2x.png"

        # Satellite City Coordinates
        c = sat_api['coord']
        self.longtitude1 = c['lon']
        self.latitude1 = c['lat']

        # Satellite City Country
        d = sat_api['sys']
        self.country1 = d['country']

        # Satellite City
        self.citi1 = sat_api['name']

        # Current City Temperatures
        z = cur_api['main']
        self.current_temperature2 = z['temp']
        self.humidity2 = z['humidity']
        self.tempmin2 = z['temp_min']
        self.tempmax2 = z['temp_max']

        # Current City Icon
        y = cur_api['weather']
        self.icon2 = [dict['icon'] for dict in y]
        self.descrip2 = [dict['description'] for dict in y]
        self.icon_url2 = f"http://openweathermap.org/img/wn/{self.icon2}@2x.png"

        # Current City Coordinates
        x = cur_api['coord']
        self.longtitude2 = c['lon']
        self.latitude2 = c['lat']

        # Current City Country
        d = cur_api['sys']
        self.country2 = d['country']

        # Current City
        self.citi2 = cur_api['name']

        # Reset counter for future API queries
        self.init_counter = False

    def app_setup(self):
        # Date Variable
        dt = datetime.datetime.now()
        try:
            w,l = 500,580
            root = Tk()
            root.title("DJC2 20.2 'The Looters' Weather App")
            root.geometry(f"{w}x{l}")
            root['background'] = "white"

            # Current City Search
            self.city2_name = StringVar()
            self.city2_name.set(self.current_city)
            city2_entry = Entry(root, textvariable=self.city2_name, width=63)
            city2_entry.grid(row=0, column=0, ipady=10, stick=W+E+N+S)
            self.current_city = city2_entry.get()

            # Sat City Search
            self.city1_name = StringVar()
            self.city1_name.set(self.sat_city)
            city1_entry = Entry(root, textvariable=self.city1_name, width=63)
            city1_entry.grid(row=1, column=0, ipady=10, stick=W+E+N+S)
            self.current_city = city1_entry.get()

            # Update API info
            self.api_call()

            # Country Names and Coordinates
            lable_citi1 = Label(root, width=0, bg='white', font=("bold", 15))
            lable_citi1.place(x=3, y=80)
            lable_citi2 = Label(root, width=0, bg='white', font=("bold", 15))
            lable_citi2.place(x=((w/2)+3), y=80)

            lable_lat1 = Label(root, width=0, bg='white', font=("Helvetica", 15))
            lable_lat1.place(x=3, y=110)
            lable_lat2 = Label(root, width=0, bg='white', font=("Helvetica", 15))
            lable_lat2.place(x=((w/2)+3), y=110)

            lable_lon1 = Label(root, width=0, bg='white', font=("Helvetica", 15))
            lable_lon1.place(x=3, y=140)
            lable_lon2 = Label(root, width=0, bg='white', font=("Helvetica", 15))
            lable_lon2.place(x=((w/2)+3), y=140)

            # TF 51/1 Logo Image
            new = ImageTk.PhotoImage(Image.open('logo.png'))
            panel = Label(root, bg='white', image=new)
            panel.place(x=410, y=230)

            # Dates
            date1 = Label(root, text=dt.strftime('Time: %A, %C %B, %Y'), bg='white', font=("bold", 15))
            date1.place(x=3, y=200)

            # Time
            hour1 = Label(root, text=dt.strftime('%I : %M %p'),
                         bg='white', font=("bold", 15))
            hour1.place(x=3, y=170)

            # Weather Description
            lable_descrip1 = Label(root, text="ERROR", width=0, bg='white', font=("bold", 15))
            lable_descrip1.place(x=3, y=400)
            lable_descrip2 = Label(root, text="ERROR", width=0, bg='white', font=("bold", 15))
            lable_descrip2.place(x=((w/2)+3), y=400)

            # Current Temperature
            lable_temp1 = Label(root, text="ERROR", width=0, bg='white', font=("bold", 15))
            lable_temp1.place(x=3, y=430)
            lable_temp2 = Label(root, text="ERROR", width=0, bg='white', font=("bold", 15))
            lable_temp2.place(x=((w/2)+3), y=430)

            # Humidity
            lable_humidity1 = Label(root, width=0,bg='white', font=("bold", 15))
            lable_humidity1.place(x=3, y=460)
            lable_humidity2 = Label(root, width=0,bg='white', font=("bold", 15))
            lable_humidity2.place(x=((w/2)+3), y=460)

            # Max Temperature
            max_temp1 = Label(root, width=0, bg='white', font=("bold", 15))
            max_temp1.place(x=3, y=490)
            max_temp2 = Label(root, width=0, bg='white', font=("bold", 15))
            max_temp2.place(x=((w/2)+3), y=490)

            # Min Temperature
            min_temp1 = Label(root, width=0, bg='white', font=("bold", 15))
            min_temp1.place(x=3, y=520)
            min_temp2 = Label(root, width=0, bg='white', font=("bold", 15))
            min_temp2.place(x=((w/2)+3), y=520)

            # Note
            note = Label(root, text="All temperatures in degrees Fahrenheit", bg='white', font=("italic", 10))
            note.place(x=120, y=550)

            # Theme for current sun/rain status:
            def get_source(src=self.icon_url1):
                r = requests.get(src)
                if r.status_code == 200:
                    return soup(r.text)
                else:
                    sys.exit( "[~] Invalid Response Received." )

            def filter(html):
                imgs = html.findAll( "img" )
                if imgs:
                    return imgs
                else:
                    sys.exit("[~] No images detected on the page.")

            def requesthandle(src=self.icon_url1):
                try:
                    r = requests.get(src, stream=True)
                    if r.status_code == 200:
                        r.raw.decode_content = True
                        with open(name, "wb") as f:
                            shutil.copyfileobj(r.raw, f)
                        print(f"[*] Downloaded Image: {name}")
                except Exception as error:
                    print(f"[~] Error Occured with {name} : {error}")

            def get_img():
                html = get_source()
                tag = filter(html)
                src = tag.get("img")
                if src:
                    src = src.groups()
                    img = ImageTk.PhotoImage(Image.open(src))
                    panel = Label(root, image=img)
                    panel.place(x=1, y=200)
                else:
                    img = ImageTk.PhotoImage(Image.open('img_notfound.png'))
                    panel = Label(root, image=img)
                    panel.place(x=1, y=200)

            # Theme for the respective time the application is used
            if int((dt.strftime('%H'))) >= 20:
               img = ImageTk.PhotoImage(Image.open('moon.png'))
               panel = Label(root, image=img)
               panel.place(x=210, y=200)
            elif int((dt.strftime('%H'))) <= 7:
               img = ImageTk.PhotoImage(Image.open('moon.png'))
               panel = Label(root, image=img)
               panel.place(x=210, y=200)
            else:
               img = ImageTk.PhotoImage(Image.open('sun.png'))
               panel = Label(root, image=img)
               panel.place(x=210, y=200)

            # Adding the received info into the screen for Current City
            lable_temp1.configure(text=f"Temperature: {self.current_temperature1}")
            lable_humidity1.configure(text=f"Humidity: {self.humidity1}%")
            max_temp1.configure(text="Max Temp Today: " + f"{self.tempmax1}" + '\u00b0')
            min_temp1.configure(text=f"Min Temp Today: {self.tempmin1}\u00b0")
            lable_lon1.configure(text=f"Longitude: {self.longtitude1}")
            lable_lat1.configure(text=f"Latitude: {self.latitude1}")
            lable_citi1.configure(text=f"Current: {self.citi1}, {self.country1}")
            lable_descrip1.configure(text=f"Weather: {self.descrip1}")

            # Adding the received info into the screen for Satellite City
            lable_temp2.configure(text=f"Temperature: {self.current_temperature2}")
            lable_humidity2.configure(text=f"Humidity: {self.humidity2}%")
            max_temp2.configure(text="Max Temp Today: " + f"{self.tempmax2}" + '\u00b0')
            min_temp2.configure(text=f"Min Temp Today: {self.tempmin2}\u00b0")
            lable_lon2.configure(text=f"Longitude: {self.longtitude2}")
            lable_lat2.configure(text=f"Latitude: {self.latitude2}")
            lable_citi2.configure(text=f"STEP Loc: {self.citi2}, {self.country2}")
            lable_descrip2.configure(text=f"Weather: {self.descrip2}")

            # Search Bar and Button
            city_nameButton1 = Button(root, text="Update Current City", command=self.api_call(button1=True))
            city_nameButton1.grid(row=0, column=1, padx=1, stick=W+E+N+S)
            city_nameButton2 = Button(root, text="Update STEP City  ", command=self.api_call(button2=True))
            city_nameButton2.grid(row=1, column=1, padx=1, stick=W+E+N+S)
            #city_nameButton.update()
            #city_nameButton.invoke()
            #city_nameButton.flash()


            # Need to add a looping thread to conduct a 15 min sleep and then call the api for updated information
            # if self.button1 == True or self.button2 ==True:
            #     join()
            #     complete root loop
            #     start sleep thread again
            # else:
            #     call sleep thread again
            root.mainloop()

        except ConnectionError as error:
            self.error_count += 1
            self.info_error_list.append(f"{error}:{datetime.datetime.today()}")
            print(error)
            # 30 second timer for checking for connection problems
            timer.sleep(30)
            self.app_setup()

        except Exception as error:
            self.warn_error_list.append(f"{error}:{datetime.datetime.today()}")
            print(error)
            self.error_count += 1

    def big_timer(self):
        # 15 min timer for updating weather info
        timer.sleep(900)

    def app_exit(self):
        # Final log messages for recording completion and problems
        if self.error_count > 0:
            self.log_message_errorsum()
            self.log_message_end()
            exit(1)
        else:
            self.log_message_end()
            exit(0)


def main():
    # Application initialization
    weatherapp = cityweather(current_city='Aqaba', sat_city='Lago Patria')
    weatherapp.app_setup()
    weatherapp.app_exit()


# Call the main function
if __name__ == "__main__":
    main()
