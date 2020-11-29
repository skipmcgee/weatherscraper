### Initial Folder PyInstaller Command
pyinstaller --noconfirm --debug=all --onedir --add-data="README.md;." --add-data="LICENSE;." --add-data="day.png;." --add-data="img_notfound.jpeg;." --add-data="logo.png;." --add-data="night.png;." --noupx --name "WeatherApp" --icon=logo.ico --additional-hooks-dir=. --clean --icon="logo.ico" weatherscraper.py

### Updated Folder PyInstaller Command
pyinstaller --noconfirm --debug=all --onedir --windowed --add-data="README.md;." --add-data="LICENSE;." --add-data="day.png;." --add-data="img_notfound.jpeg;." --add-data="logo.png;." --add-data="night.png;." --noupx --name "WeatherApp" --icon=logo.ico --additional-hooks-dir=. --clean --icon="logo.ico" weatherscraper.py

### Initial Single Executable PyInstaller Command
pyinstaller --noconfirm --debug=all --onefile --windowed --add-data="README.md;." --add-data="LICENSE;." --add-data="day.png;." --add-data="img_notfound.jpeg;." --add-data="logo.png;." --add-data="night.png;." --noupx --name "WeatherApp" --icon=logo.ico --additional-hooks-dir=. --clean --icon="logo.ico" weatherscraper.py
##### Requires that afterwards you remove the "[('v', None, 'OPTION')]," from the WeatherApp.spec file, then rebuild with:
pyinstaller -F -d all -w WeatherApp.spec

### Single Executable File PyInstaller Command
pyinstaller --noconfirm --onefile --windowed --add-data="day.png;." --add-data="img_notfound.jpeg;." --add-data="logo.png;." --add-data="night.png;." --name "WeatherApp" --icon="logo.ico" --hidden-import="tk" --hidden-import="tkinter" --additional-hooks-dir=. --clean --icon="logo.ico" weatherscraper.py
##### Requires that afterwards you remove the "[('v', None, 'OPTION')]," from the WeatherApp.spec file, then rebuild with:
pyinstaller -F -d all -w WeatherApp.spec
