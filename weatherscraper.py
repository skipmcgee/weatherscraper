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


global error_count

def timer(delay):
    rightnow = datetime.datetime.today()
    time.sleep(delay)


def infoscraper(url):
    error_count = 0
    try:
#        thread1 = Thread(target=timer(15), daemon=True)
#        thread1.start()
#        timer(delay=10)

        json_url = "https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=40.9369&lon=14.0334&altitude=15"
        page = requests.get(json_url)
        soup = BeautifulSoup(page.content, 'html.parser')
        print(soup)
    except Exception as error:
        print(error)
        error_count += 1

def weatherscraper(url):
    error_count = 0
# from https://www.geeksforgeeks.org/create-a-gui-for-weather-forecast-using-openweathermap-api-in-python/
    try:
        root = Tk()
        root.title("Weather App")
        root.geometry("450x525")
        root['background'] = "white"

        # Image
        new = ImageTk.PhotoImage(Image.open('logo.png'))
        panel = Label(root, image=new)
        panel.place(x=350, y=75)


        # Dates
        dt = datetime.datetime.now()
        date = Label(root, text=dt.strftime('%A--'), bg='white', font=("bold", 15))
        date.place(x=5, y=130)
        month = Label(root, text=dt.strftime('%m %B'), bg='white', font=("bold", 15))
        month.place(x=100, y=130)

        # Time
        hour = Label(root, text=dt.strftime('%I : %M %p'),
                     bg='white', font=("bold", 15))
        hour.place(x=10, y=160)

        # Theme for the respective time the application is used
        if int((dt.strftime('%I'))) >= 8 & int((dt.strftime('%I'))) <= 5:
            img = ImageTk.PhotoImage(Image.open('moon.png'))
            panel = Label(root, image=img)
            panel.place(x=210, y=200)
        else:
            img = ImageTk.PhotoImage(Image.open('sun.png'))
            panel = Label(root, image=img)
            panel.place(x=210, y=200)


        # City Search
        city_name = StringVar()
        city_entry = Entry(root, textvariable=city_name, width=42)
        city_entry.grid(row=1, column=0, ipady=10, stick=W+E+N+S)


        def city_name():

            # API Call
            api_key = "x"
            api_request = requests.get("https://api.openweathermap.org/data/2.5/weather?q="
                                       + city_entry.get() + "&units=imperial&appid=" + api_key)
            api = json.loads(api_request.content)

            # Temperatures
            y = api['main']
            current_temperature = y['temp']
            humidity = y['humidity']
            tempmin = y['temp_min']
            tempmax = y['temp_max']

            # Coordinates
            x = api['coord']
            longtitude = x['lon']
            latitude = x['lat']

            # Country
            z = api['sys']
            country = z['country']
            citi = api['name']

            # Adding the received info into the screen
            lable_temp.configure(text=current_temperature)
            lable_humidity.configure(text=humidity)
            max_temp.configure(text=tempmax)
            min_temp.configure(text=tempmin)
            lable_lon.configure(text=longtitude)
            lable_lat.configure(text=latitude)
            lable_country.configure(text=country)
            lable_citi.configure(text=citi)


        # Search Bar and Button
        city_nameButton = Button(root, text="Search", command=city_name)
        city_nameButton.grid(row=1, column=1, padx=4, stick=W+E+N+S)


        # Country  Names and Coordinates
        lable_citi = Label(root, text="...", width=0,
                           bg='white', font=("bold", 15))
        lable_citi.place(x=10, y=63)

        lable_country = Label(root, text="...", width=0,
                              bg='white', font=("bold", 15))
        lable_country.place(x=135, y=63)

        lable_lon = Label(root, text="...", width=0,
                          bg='white', font=("Helvetica", 15))
        lable_lon.place(x=25, y=95)
        lable_lat = Label(root, text="...", width=0,
                          bg='white', font=("Helvetica", 15))
        lable_lat.place(x=95, y=95)

        # Current Temperature

        lable_temp = Label(root, text="...", width=0, bg='white',
                           font=("Helvetica", 110), fg='black')
        lable_temp.place(x=18, y=220)

        # Other temperature details

        humi = Label(root, text="Humidity: ", width=0,
                     bg='white', font=("bold", 15))
        humi.place(x=3, y=400)

        lable_humidity = Label(root, text="...", width=0,
                               bg='white', font=("bold", 15))
        lable_humidity.place(x=107, y=400)


        maxi = Label(root, text="Max. Temp: ", width=0,
                     bg='white', font=("bold", 15))
        maxi.place(x=3, y=430)

        max_temp = Label(root, text="...", width=0,
                         bg='white', font=("bold", 15))
        max_temp.place(x=128, y=430)


        mini = Label(root, text="Min. Temp: ", width=0,
                     bg='white', font=("bold", 15))
        mini.place(x=3, y=460)

        min_temp = Label(root, text="...", width=0,
                         bg='white', font=("bold", 15))
        min_temp.place(x=128, y=460)


        # Note
        note = Label(root, text="All temperatures in degrees Fahrenheit",
                     bg='white', font=("italic", 10))
        note.place(x=95, y=495)


        root.mainloop()


    except Exception as error:
        print(error)
        error_count += 1


# <script src="https://www.yr.no/place/Italy/Campania/Lago_di_Patria/external_box_hour_by_hour.js"></script><noscript><a href="https://www.yr.no/place/Italy/Campania/Lago_di_Patria/">yr.no: Forecast for Lago di Patria</a></noscript>

# HTML for the above: document.write('\n'
#  + '<iframe src="https://www.yr.no/place/Italy/Campania/Lago_di_Patria/external_box_hour_by_hour.html" width="850" height="430" frameborder="0" style="margin: 10px 0 10px 0" scrolling="no">\n'
#  + '</iframe>\n'
# );



def main():
    url = "https://weather.com/weather/hourbyhour/l/bd6e61a96a73fe700823357bc4695a0342074429b43fdbee1202ed754b361eee"
    infoscraper(url)
    weatherscraper(url)
    exit()


# Call the main function
if __name__ == "__main__":
    main()
