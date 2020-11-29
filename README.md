# WeatherApp README
Ever need to check if the distant end of a satellite connection is masking equipment problems as "weather problems"? Ever need to monitor the current weather in two separate locations?
####
This application is designed to display the current weather at your location + the current weather at a second location of your choosing (such as hub/spoke satellite sites, etc.). The two locations can be any where across the globe, simply input the name of the nearest major city. The API data is updated approximately every 15 minutes, so a new search will be accurate to within that time period.
####
## *** This repository is for anyone interested in building their own version of the Looter's WeatherApp for Windows 10 ***
####
If you want to just download and run the current version, please navigate to: [WeatherApp](https://github.com/skipmcgee/WeatherApp/tree/main/download) (includes a hashfile for file integrity validation).
##
# WeatherApp.exe Build Instructions
In order to access the API utilized in this application: 
- Browse to: https://openweathermap.org/api
- Under the options, subscribe for the "Free Current Weather". Create an API key.
- Add your key to the "api_key" variable in the class definition in weatherscraper.py. Run this little application!
- (Note: If you aren't a DJC2 20.2 "Looter", you might want to consider changing the application logo and default locations.)
####
1. Install Python 3.8.6 https://www.python.org/downloads/
2. pip install PyInstaller (version 4.1 used for my build)
3. Edit your Environment Variables for PATH, adding C:\Windows\System32\downlevel and C:\Windows\SysWOW64\downlevel  (note: this isn't strictly neccessary but prevents PyInstaller from throwing a lot of errors)
3. Confirm that you have the modules installed per [pip_list_installed](https://github.com/skipmcgee/weatherscraper/blob/win10exe/pip_list_installed)
4. Run the pyinstaller commands per [Build_Commands](https://github.com/skipmcgee/weatherscraper/blob/win10exe/Build_Commands.md)
5. If all instructions were followed with equal version, etc. check hashes for compatibility [Hashfile](https://github.com/skipmcgee/weatherscraper/blob/win10exe/Hashfile.txt)
6. Execute application from the 'dist' folder
####
### Troubleshooting:
1. Run weatherscraper.py with python to ensure there aren't any issues with the script itself (like a missing api key)
2. Build with folder commands and debug=all first, run the executable and troubleshoot any errors
3. Install and run [DebugView](https://docs.microsoft.com/en-us/sysinternals/downloads/debugview) before you run your application
4. Try single file executable build last
#### The WeatherApp project is designed and built by Skip McGee
