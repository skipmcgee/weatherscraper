#!/usr/bin/env python3

##################################################################################
#
# Created by Skip McGee for DJC2 20.2 AKA "The Looters" on 20201012
#
#
##################################################################################

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


global error_count, counter

#        thread1 = Thread(target=timer(15), daemon=True)
#        thread1.start()
#        timer(delay=10)

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
#        print(soup)
#    except Exception as error:
#        print(error)
#        error_count += 1
#url = "https://weather.com/weather/hourbyhour/l/bd6e61a96a73fe700823357bc4695a0342074429b43fdbee1202ed754b361eee"

class cityweather():
    def __init__(self):
        self.error_count = 0
        self.counter = 0
    def api_call(self):
        # API Call
        api_key = "894301acda297582e5e34973cbc1f4a9"
        api_request = requests.get("https://api.openweathermap.org/data/2.5/weather?q="
                                       + "Lago Patria" + "&units=imperial&appid=" + api_key)
        if self.counter > 0:
            api_request = requests.get("https://api.openweathermap.org/data/2.5/weather?q="
                                       + self.city_entry.get() + "&units=imperial&appid=" + api_key)
        api = json.loads(api_request.content)
        # Temperatures
        y = api['main']
        self.current_temperature = y['temp']
        self.humidity = y['humidity']
        self.tempmin = y['temp_min']
        self.tempmax = y['temp_max']

        # Icon
        i = api['weather']
        self.icon = [dict['icon'] for dict in i]
        self.description = [dict['description'] for dict in i]
        self.icon_url = f"http://openweathermap.org/img/wn/{self.icon}@2x.png"

        # Coordinates
        x = api['coord']
        self.longtitude = x['lon']
        self.latitude = x['lat']

        # Country
        z = api['sys']
        self.country = z['country']
        self.citi = api['name']
        print("completed")

        # Increase counter
        self.counter += 1
# from https://www.geeksforgeeks.org/create-a-gui-for-weather-forecast-using-openweathermap-api-in-python/

    def app_setup(self):
        # Date Variable
        dt = datetime.datetime.now()
        try:
            root = Tk()
            root.title("Weather App")
            root.geometry("450x550")
            root['background'] = "white"

            # City Search
            city_name = StringVar()
            city_name.set("Lago Patria")
            city_entry = Entry(root, textvariable=city_name, width=63)
            city_entry.grid(row=1, column=0, ipady=10, stick=W+E+N+S)

            # Country  Names and Coordinates
            lable_citi = Label(root, width=0, bg='white', font=("bold", 15))
            lable_citi.place(x=3, y=40)

            lable_country = Label(root, width=0, bg='white', font=("bold", 15))
            lable_country.place(x=200, y=40)

            lable_lat = Label(root, width=0, bg='white', font=("Helvetica", 15))
            lable_lat.place(x=3, y=70)

            lable_lon = Label(root, width=0, bg='white', font=("Helvetica", 15))
            lable_lon.place(x=3, y=100)

            # Image
            new = ImageTk.PhotoImage(Image.open('logo.png'))
            panel = Label(root, image=new)
            panel.place(x=350, y=75)

            # Dates
            date = Label(root, text=dt.strftime('%A, %C %B, %Y'), bg='white', font=("bold", 15))
            date.place(x=5, y=160)

            # Time
            hour = Label(root, text=dt.strftime('%I : %M %p'),
                         bg='white', font=("bold", 15))
            hour.place(x=3, y=130)

            # Current Temperature
            lable_temp = Label(root, text="ERROR", width=0, bg=None, font=("Helvetica", 90), fg='black')
            lable_temp.place(x=3, y=245)

            # Other temperature details
            humi = Label(root, width=0, bg='white', font=("bold", 15))
            humi.place(x=3, y=430)

            lable_humidity = Label(root, width=0,bg='white', font=("bold", 15))
            lable_humidity.place(x=3, y=430)


            maxi = Label(root, width=0, bg='white', font=("bold", 15))
            maxi.place(x=3, y=460)

            max_temp = Label(root, width=0, bg='white', font=("bold", 15))
            max_temp.place(x=3, y=460)


            mini = Label(root, width=0, bg='white', font=("bold", 15))
            mini.place(x=3, y=490)

            min_temp = Label(root, width=0, bg='white', font=("bold", 15))
            min_temp.place(x=3, y=490)

            # Note
            note = Label(root, text="All temperatures in degrees Fahrenheit", bg='white', font=("italic", 10))
            note.place(x=95, y=520)

            # Theme for current sun/rain status:
            def get_source(src=self.icon_url):
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

            def requesthandle(src):
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

            # Adding the received info into the screen
            lable_temp.configure(text=f"Temp: {self.current_temperature}")
            lable_humidity.configure(text=f"Humidity: {self.humidity}%")
            max_temp.configure(text="Max Temp Today: " + f"{self.tempmax}" + '\u00b0')
            min_temp.configure(text=f"Min Temp Today: {self.tempmin}\u00b0")
            lable_lon.configure(text=f"Longitude: {self.longtitude}")
            lable_lat.configure(text=f"Latitude: {self.latitude}")
            lable_country.configure(text=f"Country: {self.country}")
            lable_citi.configure(text=f"City: {self.citi}")

            # Search Bar and Button
            city_nameButton = Button(root, text="  Search  ", command=self.api_call)
            city_nameButton.grid(row=1, column=1, padx=4, stick=W+E+N+S)
            #city_nameButton.update()
            #city_nameButton.invoke()
            #city_nameButton.flash()
            root.mainloop()

        except ConnectionError:
            self.error_count += 1

        except Exception as error:
            print(error)
            self.error_count += 1

def main():
    firstcity = cityweather()
    firstcity.api_call()
    firstcity.app_setup()
    exit()


# Call the main function
if __name__ == "__main__":
    main()


