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
counter = 0

def timer(delay):
    rightnow = datetime.datetime.today()
    time.sleep(delay)
    counter += 1
    if counter is 1 or 2:
        newtime = datetime.datetime.today()
        timer(delay)
    if counter >= 2:
        raise TimeoutError
#        thread1 = Thread(target=timer(15), daemon=True)
#        thread1.start()
#        timer(delay=10)

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

def weatherscraper(url):
    error_count = 0
# from https://www.geeksforgeeks.org/create-a-gui-for-weather-forecast-using-openweathermap-api-in-python/
    try:
        root = Tk()
        root.title("Weather App")
        root.geometry("450x550")
        root['background'] = "white"

        # Image
        new = ImageTk.PhotoImage(Image.open('logo.png'))
        panel = Label(root, image=new)
        panel.place(x=350, y=75)

        # Dates
        dt = datetime.datetime.now()
        date = Label(root, text=dt.strftime('%A, %C %B, %Y'), bg='white', font=("bold", 15))
        date.place(x=5, y=160)

        # Time
        hour = Label(root, text=dt.strftime('%I : %M %p'),
                     bg='white', font=("bold", 15))
        hour.place(x=10, y=130)






        # City Search
        city_name = StringVar()
        city_name.set('Lago Patria')
        city_entry = Entry(root, textvariable=city_name, width=63)
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

            # Theme for current sun/rain status:
            if humidity >= 90:
                img = ImageTk.PhotoImage(Image.open('rain.png'))
                panel = Label(root, image=img)
                panel.place(x=1, y=200)
            elif humidity >= 40 and humidity <= 89:
                img = ImageTk.PhotoImage(Image.open('mixed.png'))
                panel = Label(root, image=img)
                panel.place(x=1, y=200)
            elif humidity <= 39:
                img = ImageTk.PhotoImage(Image.open('sunny.png'))
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

            # Coordinates
            x = api['coord']
            longtitude = x['lon']
            latitude = x['lat']

            # Country
            z = api['sys']
            country = z['country']
            citi = api['name']

            # Adding the received info into the screen
            lable_temp.configure(text=f"Temp: {current_temperature}")
            lable_humidity.configure(text=f"Humidity: {humidity}%")
            max_temp.configure(text="Max Temp Today: " + f"{tempmax}" + '\u00b0')
            min_temp.configure(text=f"Min Temp Today: {tempmin}\u00b0")
            lable_lon.configure(text=f"Longitude: {longtitude}")
            lable_lat.configure(text=f"Latitude: {latitude}")
            lable_country.configure(text=f"Country: {country}")
            lable_citi.configure(text=f"City: {citi}")

        # Search Bar and Button
        city_nameButton = Button(root, text="  Search  ", command=city_name)
        city_nameButton.grid(row=1, column=1, padx=4, stick=W+E+N+S)


        # Country  Names and Coordinates

        lable_citi = Label(root, width=0, bg='white', font=("bold", 15))
        lable_citi.place(x=5, y=40)

        lable_country = Label(root, width=0, bg='white', font=("bold", 15))
        lable_country.place(x=135, y=40)

        lable_lat = Label(root, width=0, bg='white', font=("Helvetica", 15))
        lable_lat.place(x=5, y=70)

        lable_lon = Label(root, width=0, bg='white', font=("Helvetica", 15))
        lable_lon.place(x=5, y=100)


        # Current Temperature
        lable_temp = Label(root, text="ERROR", width=0, bg=None, font=("Helvetica", 90), fg='black')
        lable_temp.place(x=5, y=245)

        # Other temperature details
        humi = Label(root, width=0, bg='white', font=("bold", 15))
        humi.place(x=3, y=430)

        lable_humidity = Label(root, width=0,bg='white', font=("bold", 15))
        lable_humidity.place(x=107, y=430)


        maxi = Label(root, width=0, bg='white', font=("bold", 15))
        maxi.place(x=3, y=460)

        max_temp = Label(root, width=0, bg='white', font=("bold", 15))
        max_temp.place(x=128, y=460)


        mini = Label(root, width=0, bg='white', font=("bold", 15))
        mini.place(x=3, y=490)

        min_temp = Label(root, width=0, bg='white', font=("bold", 15))
        min_temp.place(x=128, y=490)

        # Note
        note = Label(root, text="All temperatures in degrees Fahrenheit", bg='white', font=("italic", 10))
        note.place(x=95, y=520)



        root.mainloop()


    except ConnectionError:
        error_count += 1


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
    weatherscraper(url)
    exit()


# Call the main function
if __name__ == "__main__":
    main()


