import tkinter as tk
import requests  # Requests for weather from http
from tkinter import messagebox
from PIL import Image, ImageTk  # Processing and displaying images
from ttkbootstrap import ttk
from tkinter.ttk import Style # ttk theme
import matplotlib.pyplot as plt # Plot hourly forecast
from datetime import datetime, timedelta # Convert time into human time
import folium # Create wind flow direction map
import webbrowser # Open map as html in browser
import os
# -------------------------------------------------------------------------------------
# Create a class 
class WeatherAPI:
    def __init__(self, api_key):
        self.api_key = api_key
    # Get weather function (information of current and hourly forecast from OpenWeatherMap API)
    def get_weather(self, city):
        try:
            current_weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_key}"
            hourly_forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={self.api_key}"

            current_weather_res = requests.get(current_weather_url)
            hourly_forecast_res = requests.get(hourly_forecast_url)

            if current_weather_res.status_code == 404 or hourly_forecast_res.status_code == 404:
                messagebox.showerror("Error", "City not found, please enter again.")
                return

            current_weather = current_weather_res.json()
            if current_weather_res.status_code != 200:
                error_message = current_weather_res.json().get('message', 'Unknown error')
                messagebox.showerror("Error", f"Failed to retrieve weather information: {error_message}")
                return

            icon_id = current_weather['weather'][0]['icon']
            temperature = current_weather['main']['temp'] - 273.15
            feels_like = current_weather['main']['feels_like'] - 273.15
            description = current_weather['weather'][0]['description']
            city = current_weather['name']
            country = current_weather['sys']['country']
            wind_speed = current_weather['wind']['speed']
            wind_direction = current_weather['wind']['deg']
            pressure = current_weather['main']['pressure']
            humidity = current_weather['main']['humidity']
            dew_point = temperature - (100 - humidity) / 5
            visibility = current_weather.get('visibility', "N/A")

            # Extract latitude and longitude
            lat = current_weather['coord']['lat']
            lon = current_weather['coord']['lon']

            hourly_forecast = hourly_forecast_res.json()
            hourly_temperatures = [forecast['main']['temp'] - 273.15 for forecast in hourly_forecast['list']]
            timestamps = [forecast['dt'] for forecast in hourly_forecast['list']]

            icon_url = f"https://openweathermap.org/img/wn/{icon_id}@2x.png"
            return (icon_url, temperature, description, city, country, wind_speed, wind_direction, pressure,
                    humidity, dew_point, visibility, feels_like, timestamps, hourly_temperatures, lat, lon)
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Request error: {e}")
            return None
        except KeyError as e:
            messagebox.showerror("Error", f"Key error: {e}")
            return None
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
            return None
    # -------------------------------------------------------------------------------------
    # Function to get the current time for a city using OpenWeatherMap's data
    def get_current_time(self, city):
        try:
            current_weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_key}"

            current_weather_res = requests.get(current_weather_url)

            if current_weather_res.status_code != 200:
                return "Time not available"

            current_weather_data = current_weather_res.json()
            timezone_offset = current_weather_data["timezone"]

            # Calculate the local time based on the UTC time and timezone offset
            utc_time = datetime.utcnow()
            local_time = utc_time + timedelta(seconds=timezone_offset)

            # Format the local time as a string
            self.current_time = local_time.strftime("%I:%M %p")

            return self.current_time
        except Exception as e:
            return "Time not available"
    # -------------------------------------------------------------------------------------
    # Get weather function (information of 5-days forecast from OpenWeatherMap API)
    def get_5_day_weather(self, city):
        try:
            forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={self.api_key}"
            forecast_res = requests.get(forecast_url)

            if forecast_res.status_code == 404:
                tk.messagebox.showerror("Error", "City not found, please enter again.")
                return None

            forecast_data = forecast_res.json()
            daily_forecast = forecast_data.get('list', [])[::8]

            dates = []
            months = []
            icons = []
            temperature_fivedays = []
            weather_behaviors = []

            for forecast in daily_forecast:
                date = datetime.fromtimestamp(forecast['dt']).strftime("%d")
                month = datetime.fromtimestamp(forecast['dt']).strftime("%b")
                icon_id = forecast['weather'][0]['icon']
                temperature = forecast['main']['temp'] - 273.15
                weather_behavior = forecast['weather'][0]['description']

                dates.append(date)
                months.append(month)
                icons.append(icon_id)
                temperature_fivedays.append(temperature)
                weather_behaviors.append(weather_behavior)

            return dates, months, icons, temperature_fivedays, weather_behaviors
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Request error: {e}")
            return None
        except KeyError as e:
            messagebox.showerror("Error", f"Key error: {e}")
            return None
    # -------------------------------------------------------------------------------------
    # Get function convert wind into directions
    def get_wind_direction(self, degrees):
        try:
            if 22.5 <= degrees < 67.5:
                return "NE"
            elif 67.5 <= degrees < 112.5:
                return "E"
            elif 112.5 <= degrees < 157.5:
                return "SE"
            elif 157.5 <= degrees < 202.5:
                return "S"
            elif 202.5 <= degrees < 247.5:
                return "SW"
            elif 247.5 <= degrees < 292.5:
                return "W"
            elif 292.5 <= degrees < 337.5:
                return "NW"
            else:
                return "N"
        except ValueError:
            return "Error: Unable to retrieve wind direction!"
# -------------------------------------------------------------------------------------
# Create a class for WeatherWise app tkinter
class WeatherApp(tk.Tk):
    def __init__(self, api_key):
        super().__init__()
        self.api = WeatherAPI(api_key)
        self.title("Weather Wise")
        self.geometry("600x600")
        self.grid_rowconfigure(0, weight=1)  # Allow row 0 (city entry) to expand
        self.grid_rowconfigure(1, weight=1)  # Row 1 (buttons) can expand
        self.grid_rowconfigure(2, weight=1)  # Center row 2 (location_label)
        self.grid_rowconfigure(3, weight=1)  # Allow row 3 (icon label) to expand
        self.grid_rowconfigure(4, weight=1)  # Center row 4 (current_time_label)
        self.grid_rowconfigure(5, weight=1)  # Center row 5 (temperature_label)
        self.grid_rowconfigure(6, weight=1)  # Center row 6 (description_label)
        self.grid_rowconfigure(7, weight=1)  # Center row 7 (wind_label)
        self.grid_rowconfigure(8, weight=1)  # Center row 8 (pressure_label)
        self.grid_rowconfigure(9, weight=1)  # Center row 9 (humidity_label)
        self.grid_rowconfigure(10, weight=1)  # Center row 10 (dew_point_label)
        self.grid_rowconfigure(11, weight=1)  # Center row 11 (visibility_label)
        self.grid_columnconfigure(0, weight=1)  # Allow column 0 to expand
        self.grid_columnconfigure(1, weight=1)  # Center column 1
        
        # Create a Frame to hold the buttons and center it
        self.frame = tk.Frame(self)
        self.frame.grid(row=1, columnspan=3, pady=0, padx=10, sticky="n")
        # Set ttkbootstrap style
        self.style = ttk.Style()
        self.style.theme_use('classic')
        self.create_widgets()

        # Label widget to show the city/country name
        self.location_label = tk.Label(self.frame, font="Helvetica 25")
        self.location_label.grid(column=1, row=2, pady=20, sticky="nsew", columnspan=2)  

        # Label widget to show the weather icon
        self.icon_label = tk.Label(self.frame)
        self.icon_label.grid(column=1, row=3, pady=10, sticky="nsew", columnspan=2)  

        # Create a label for displaying the current time
        self.current_time_label = tk.Label(self.frame, font="Helvetica 20")
        self.current_time_label.grid(column=1, row=4, pady=10, sticky="nsew", columnspan=2)  

        # Label widget to show temperature
        self.temperature_label = tk.Label(self.frame, font="Helvetica 12")
        self.temperature_label.grid(column=1, row=5, sticky="nsew", columnspan=2)  

        # Label widget to show feelslike temperature
        self.feels_like_label = tk.Label(self.frame, font="Helvetica 12")
        self.feels_like_label.grid(column=1, row=6, sticky="nsew", columnspan=2)  

        # Label widget to show the weather description
        self.description_label = tk.Label(self.frame, font="Helvetica 12")
        self.description_label.grid(column=1, row=7, sticky="nsew", columnspan=2)  

        # Label widget to show wind speed/direction
        self.wind_label = tk.Label(self.frame, font="Helvetica 12")
        self.wind_label.grid(column=1, row=8, sticky="nsew", columnspan=2)  

        # Label widget to show pressure in hPa
        self.pressure_label = tk.Label(self.frame, font="Helvetica 12")
        self.pressure_label.grid(column=1, row=9, sticky="nsew", columnspan=2)  

        # Label widget to show humidity in %
        self.humidity_label = tk.Label(self.frame, font="Helvetica 12")
        self.humidity_label.grid(column=1, row=10, sticky="nsew", columnspan=2)  

        # Label widget to show dew point in °C
        self.dew_point_label = tk.Label(self.frame, font="Helvetica 12")
        self.dew_point_label.grid(column=1, row=11, sticky="nsew", columnspan=2)  

        # Label widget to show the visibility in meters
        self.visibility_label = tk.Label(self.frame, font="Helvetica 12")
        self.visibility_label.grid(column=1, row=12, sticky="nsew", columnspan=2)  

    # Cities list of 371 cities around the wolrd in OpenWeatherMap
    cities_names = ["Abidjan", "Abu Dhabi", "Abuja",'Accra','Addis Ababa','Ahmedabad','Aleppo','Alexandria','Algiers','Almaty','Amman','Amsterdam','Anchorage','Andorra la Vella','Ankara','Antananarivo','Apia','Arnold','Ashgabat','Asmara','Asuncion','Athens','Auckland','Avarua',
                    'Baghdad','Baku','Bamako','Banda Aceh','Bandar Seri Begawan','Bandung','Bangkok','Bangui','Banjul','Barcelona','Barranquilla','Basrah','Basse-Terre','Basseterre','Beijing','Beirut','Bekasi','Belem','Belgrade','Belmopan','Belo Horizonte','Bengaluru','Berlin','Bern','Bishkek','Bissau','Bogota','Brasilia','Bratislava','Brazzaville','Bridgetown','Brisbane','Brussels','Bucharest','Budapest','Buenos Aires','Bujumbura','Bursa','Busan',
                    'Cairo','Cali','California','Caloocan','Camayenne','Canberra','Cape Town','Caracas','Casablanca','Castries','Cayenne','Charlotte Amalie','Chengdu','Chennai','Chicago','Chisinau','Chittagong','Chongqing','Colombo','Conakry','Copenhagen','Cordoba','Curitiba',
                    'Daegu','Daejeon','Dakar','Dallas','Damascus','Dar es Salaam','Delhi','Denver','Dhaka','Dili','Djibouti','Dodoma','Doha','Dongguan','Douala','Douglas','Dubai','Dublin','Durban','Dushanbe','Faisalabad','Fort-de-France','Fortaleza','Freetown','Fukuoka','Funafuti','Gaborone','George Town','Georgetown','Gibraltar','Gitega','Giza','Guadalajara','Guangzhou','Guatemala City','Guayaquil','Gujranwala','Gustavia','Gwangju',
                    'Hamburg','Hanoi','Harare','Havana','Helsinki','Ho Chi Minh City','Hong Kong','Honiara','Honolulu','Houston','Hyderabad','Hyderabad','Ibadan','Incheon','Isfahan','Islamabad','Istanbul','Izmir','Jaipur','Jakarta','Jeddah','Jerusalem','Johannesburg','Juarez','Juba',
                    'Kabul','Kaduna','Kampala','Kano','Kanpur','Kaohsiung','Karachi','Karaj','Kathmandu','Kawasaki','Kharkiv','Khartoum','Khulna','Kigali','Kingsburg','Kingston','Kingstown','Kinshasa','Kobe','Kolkata','Kota Bharu','Kowloon','Kuala Lumpur','Kumasi','Kuwait','Kyiv','Kyoto',
                    'La Paz','Lagos','Lahore','Libreville','Lilongwe','Lima','Lisbon','Ljubljana','Lome','London','Los Angeles','Luanda','Lubumbashi','Lusaka','Luxembourg','Macau','Madrid','Majuro','Makassar','Malabo','Male','Mamoudzou','Managua','Manama','Manaus','Manila','Maputo','Maracaibo','Maracay','Mariehamn','Marigot','Maseru','Mashhad','Mbabane','Mecca','Medan','Medellin','Medina','Melbourne','Mexico City','Miami','Minsk','Mogadishu','Monaco','Monrovia','Montevideo','Montreal','Moroni','Moscow','Mosul','Multan','Mumbai','Muscat',
                    "N'Djamena",'Nagoya','Nairobi','Nanchong','Nanjing','Nassau','Nay Pyi Taw','New York','Niamey','Nicosia','Nouakchott','Noumea','Novosibirsk',"Nuku'alofa",'Nur-Sultan','Nuuk','Oranjestad','Osaka','Oslo','Ottawa','Ouagadougou','Pago Pago','Palembang','Palo Alto','Panama','Papeete','Paramaribo','Paris','Perth','Philadelphia','Phnom Penh','Phoenix','Podgorica','Port Louis','Port Moresby','Port of Spain',
                    'Port-Vila','Port-au-Prince','Porto Alegre','Porto-Novo','Prague','Praia','Pretoria','Pristina','Puebla','Pune','Pyongyang','Quezon City','Quito','Rabat','Rawalpindi','Recife','Reykjavik','Riga','Rio de Janeiro','Riyadh','Road Town','Rome','Roseau',"Saint George's",'Saint Helier',"Saint John's",'Saint Peter Port','Saint Petersburg','Saint-Denis','Saint-Pierre','Saipan','Salvador','San Antonio','San Diego','San Francisco','San Jose','San Juan','San Marino','San Salvador',
                    'Sanaa','Santa Cruz de la Sierra','Santiago','Santo Domingo','Sao Paulo','Sao Tome','Sapporo','Sarajevo','Seattle','Semarang','Seoul','Shanghai','Sharjah','Shenzhen','Singapore','Skopje','Sofia','South Tangerang','Soweto','Stockholm','Sucre','Surabaya','Surat','Suva','Sydney','Tabriz','Taipei','Tallinn','Tangerang','Tarawa','Tashkent','Tbilisi','Tegucigalpa','Tehran',
                    'Tel Aviv','Thimphu','Tianjin','Tijuana','Tirana','Tokyo','Toronto','Torshavn','Tripoli','Tunis','Ulan Bator','Vaduz','Valencia','Valletta','Vancouver','Victoria','Vienna','Vientiane','Vilnius','Warsaw','Washington','Wellington','Willemstad','Windhoek','Wuhan',"Xi'an",'Yamoussoukro','Yangon','Yaounde','Yekaterinburg','Yerevan','Yokohama','Zagreb'
                    ]
    city_list = cities_names
    
    # Create widgets for the app
    def create_widgets(self):
        self.cityString = tk.StringVar()
        self.city_combobox = ttk.Combobox(self, values=self.city_list, font="Helvetica 18", textvariable=self.cityString, style="TCombobox")
        self.city_combobox.grid(columnspan=3, row=0, pady=20)

        # Create a Combobox widget to select the temperature unit
        self.temperature_unit_combobox = ttk.Combobox(self, values=["Celsius (°C)", "Fahrenheit (°F)"], font="Helvetica 12", style="TCombobox")
        self.temperature_unit_combobox.grid(column=1, row=13, padx=10, pady=10, sticky="ne")
        self.temperature_unit_combobox.set("Celsius (°C)")

        # Bind the key release event to dynamically filter the city list
        self.city_combobox.bind("<KeyRelease>", lambda event, city_list=self.city_list: self.set_completion_list(city_list, event))
        # Create a Frame to hold the buttons and center it
        self.frame = tk.Frame(self)
        self.frame.grid(row=1, columnspan=3, pady=0, padx=10, sticky="n")

        # Button widget to search for information
        self.search_button = ttk.Button(self.frame, text="Search", command=self.search, style="warning.TButton")
        self.search_button.grid(row=0, column=0, padx=10)
        
        # Button widget to access the hourly forecast
        self.hourly_forecast_button = ttk.Button(self.frame, text="Hourly Forecast", command=self.hourly_button, style="TButton")
        self.hourly_forecast_button.grid(row=0, column=1, padx=10)

        # Button widget to access 5-days forecast
        self.fiveday_forecast_button = ttk.Button(self.frame, text="5-Day Forecast", command=self.display_5_day_forecast, style="TButton")
        self.fiveday_forecast_button.grid(row=0, column=2, padx=10)

        # Button widget to show wind flow direction map
        self.wind_map_button = ttk.Button(self.frame, text="Wind-FD Map", command=lambda: self.create_wind_map(self.city_combobox.get()), style="TButton")
        self.wind_map_button.grid(row=0, column=3, padx=10)
        
    # Function to set the Combobox completion list
    def set_completion_list(self, entries, event):
        pattern = event.widget.get().lower()
        event.widget["values"] = [e for e in entries if pattern in e.lower()]
    # -------------------------------------------------------------------------------------
    # Global variable to store the icon
    icon = None
    # Search function
    def search(self):
        try:
            selected_city = self.cityString.get()  # Get the selected city from the dropdown
            result = self.api.get_weather(selected_city)
            if result is None:
                return
            # If the city is found, unpack the weather information
            icon_url, temperature, description, city, country, wind_speed, wind_direction, pressure, humidity, dew_point, visibility,feels_like, timestamps, hourly_temperatures, lat, lon = result
            self.location_label.configure(text=f"{city}, {country}")

            # Get the weather icon image and update the icon
            image = Image.open(requests.get(icon_url, stream=True).raw)
            self.icon = ImageTk.PhotoImage(image)
            self.icon_label.configure(image=self.icon) 

            # Get the current time
            current_time = self.api.get_current_time(city)  
            self.current_time_label.configure(text=f"{current_time}")
            
            # Update the temperature and description labels
            self.temperature_label.configure(text=f"Temperature: {temperature:.2f} ")
            self.feels_like_label.configure(text=f"Feels like: {feels_like:.2f} ")
            self.description_label.configure(text=f"Description: {description}")
            
            self.wind_label.configure(text=f"Wind Speed: {wind_speed} m/s {self.api.get_wind_direction(wind_direction)}")
            self.pressure_label.configure(text=f"Pressure: {pressure} hPa")
            self.humidity_label.configure(text=f"Humidity: {humidity}%")
            self.dew_point_label.configure(text=f"Dew Point: {dew_point:.2f} ")
            self.visibility_label.configure(text=f"Visibility: {visibility} meters")
            
            self.update_temperature_display()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            
    # Function to update the temperature display based on the selected unit
    def update_temperature_display(self):
        selected_unit = self.temperature_unit_combobox.get()
        result = self.api.get_weather(self.cityString.get())

        if result is None:
            return

        icon_url, temperature, description, city, country, wind_speed, wind_direction, pressure, humidity, dew_point, visibility, feels_like, timestamps, hourly_temperatures, lat, lon = result

        if selected_unit == "Fahrenheit (°F)":
            # Convert temperature from Celsius to Fahrenheit
            temperature = (temperature * 9/5) + 32
            feels_like = (feels_like * 9/5) + 32
            dew_point = (dew_point * 9/5) + 32

        self.temperature_label.configure(text=f"Temperature: {temperature:.2f}°{selected_unit}")
        self.feels_like_label.configure(text=f"Feels like: {feels_like:.2f}°{selected_unit}")
        self.dew_point_label.configure(text=f"Dew Point: {dew_point:.2f}°{selected_unit} ")
    # -------------------------------------------------------------------------------------
    # Hourly forecast button
    def hourly_button(self):
        selected_city = self.cityString.get()  # Get the selected city from the dropdown
        result = self.api.get_weather(selected_city)
        if result is not None:
            icon_url, temperature, description, city, country, wind_speed, wind_direction, pressure, humidity, dew_point, visibility, feels_like, timestamps, hourly_temperatures, lat, lon = result
            self.update_temperature_and_forecast_display(self.temperature_unit_combobox)  # Pass the combobox as a parameter

    # Graph for hourly forecast
    def show_hourly_forecast(self, city, country, timestamps, hourly_temperatures, selected_unit):
        try:
            # Limit the forecast to show only the next 8 hours
            max_hours_ahead = 8
            timestamps = timestamps[:max_hours_ahead]
            hourly_temperatures = hourly_temperatures[:max_hours_ahead]
            
            # Create a list of labels in AM/PM format for the x-axis
            am_pm_labels = [self.convert_timestamp(timestamp) for timestamp in timestamps]
        
        # Convert temperatures to Fahrenheit if selected_unit is "Fahrenheit (°F)"
            if selected_unit == "Fahrenheit (°F)":
                hourly_temperatures = [(temp * 9/5) + 32 for temp in hourly_temperatures]
                y_value = 'Temperature (°F)'  # Update the y-label
            else:
                y_value = 'Temperature (°C)'  # Default to Celsius
            
            # Create the plot
            plt.figure(figsize=(10, 6))
            plt.plot(timestamps, hourly_temperatures, marker='o', linestyle='-', color='orange')
            plt.title(f'Hourly Temperature Forecast for {city}, {country}')
            plt.xlabel(f'Time 24 hours from now (AM/PM)')
            plt.ylabel(y_value)
            
            # Set the x-axis labels to AM/PM format
            plt.xticks(timestamps, am_pm_labels, rotation=45)
            
            plt.grid(True)
            plt.tight_layout()
            plt.show()
        except ValueError:
            return "Invalid Time for hourly forecast"
        
    # Function to convert timestamps to AM/PM format
    def convert_timestamp(self, timestamp):
        try:
            # Convert the timestamp to a datetime object
            dt = datetime.fromtimestamp(timestamp)
            # Format it as AM/PM time
            am_pm_time = dt.strftime("%I:%M %p")
            return am_pm_time
        except ValueError:
            return "Invalid Time"
        
    # Function to update the temperature display and hourly forecast based on the selected unit
    def update_temperature_and_forecast_display(self, temperature_unit_combobox):
        selected_unit = temperature_unit_combobox.get()
        result = self.api.get_weather(self.city_combobox.get())

        if result is None:
            return

        icon_url, temperature, description, city, country, wind_speed, wind_direction, pressure, humidity, dew_point, visibility, feels_like, timestamps, hourly_temperatures, lat, lon = result

        if selected_unit == "Fahrenheit (°F)":
            # Convert temperature from Celsius to Fahrenheit
            temperature = (temperature * 9/5) + 32
            feels_like = (feels_like * 9/5) + 32

        # Update the hourly forecast display with the selected temperature unit
        self.show_hourly_forecast(city, country, timestamps, hourly_temperatures, selected_unit)
    # -------------------------------------------------------------------------------------
    # Function to display five days forecast
    def display_5_day_forecast(self):
        selected_city = self.cityString.get()
        results = self.api.get_5_day_weather(selected_city)
        if not results:
            return

        dates, months, icons, temperature_fivedays, weather_behaviors = results

        if not dates:
            return

        forecast_panel = tk.Toplevel(self)
        forecast_panel.title("5-Day Forecast")
        forecast_panel.geometry("500x600")

        for i in range(5):
            day_label = tk.Label(forecast_panel, text=f"{dates[i]} {months[i]}", font="Helvetica 12")
            day_label.grid(row=i, column=0, padx=10, pady=5)

            icon_url = f"https://openweathermap.org/img/wn/{icons[i]}@2x.png"
            image = Image.open(requests.get(icon_url, stream=True).raw)
            icon_image = ImageTk.PhotoImage(image)
            icon_label = tk.Label(forecast_panel, image=icon_image)
            icon_label.image = icon_image
            icon_label.grid(row=i, column=1, padx=10, pady=5)

            temperature_unit = self.temperature_unit_combobox.get()
            temperature_value = temperature_fivedays[i] if temperature_unit == 'Celsius (°C)' else (temperature_fivedays[i] * 9/5) + 32
            temperature_unit_label = "°C" if temperature_unit == 'Celsius (°C)' else "°F"

            temperature_label = tk.Label(forecast_panel, text=f"Temp: {temperature_value:.2f}{temperature_unit_label}", font="Helvetica 12")
            temperature_label.grid(row=i, column=2, padx=10, pady=5)

            weather_label = tk.Label(forecast_panel, text=f"Description: {weather_behaviors[i]}", font="Helvetica 12")
            weather_label.grid(row=i, column=3, padx=10, pady=5)
    # Function to handle the 5-Day Forecast button click
    def display_5_days_button(self):
        self.display_5_day_forecast()
        self.update_temperature_5_days()
    
    # Function to update the 5-day forecast display based on the selected unit
    def update_temperature_5_days(self, temperature_unit_combobox, forecast_panel, temperature_fivedays):
        selected_unit = temperature_unit_combobox.get()

        for i in range(5):
            temperature_value = temperature_fivedays[i] if selected_unit == 'Celsius (°C)' else (temperature_fivedays[i] * 9/5) + 32
            temperature_unit_label = "°C" if selected_unit == 'Celsius (°C)' else "°F"

            temperature_label = forecast_panel.children[f"temperature_label_{i}"]
            temperature_label.config(text=f"Temp: {temperature_value:.2f}{temperature_unit_label}")
    # -------------------------------------------------------------------------------------
    # Function to create a wind direction map
    def create_wind_map(self, city):
        try:
            result = self.api.get_weather(city)

            if result is not None:
                lat, lon = result[-2], result[-1]
                wind_direction = result[6]

                # Create a folium map centered around the city
                weather_map = folium.Map(location=[lat, lon], zoom_start=11)

                # Add a marker for the city
                folium.Marker([lat, lon], popup=f"{city}, Wind Direction: {self.api.get_wind_direction(wind_direction)}").add_to(weather_map)

                # Add arrow icons to represent wind direction
                arrow_icons = {
                    'N': 'https://cdn1.iconfinder.com/data/icons/arrow-for-love/512/arrrow-09-23-1024.png',
                    'E': 'https://cdn1.iconfinder.com/data/icons/arrow-for-love/512/arrrow-09-24-1024.png',
                    'S': 'https://cdn1.iconfinder.com/data/icons/arrow-for-love/512/arrrow-09-22-1024.png',
                    'W': 'https://cdn1.iconfinder.com/data/icons/arrow-for-love/512/arrrow-09-21-1024.png',
                    'NE': 'https://cdn1.iconfinder.com/data/icons/arrow-for-love/512/arrrow-09-06-1024.png',
                    'SE': 'https://cdn1.iconfinder.com/data/icons/arrow-for-love/512/arrrow-09-08-1024.png',
                    'SW': 'https://cdn1.iconfinder.com/data/icons/arrow-for-love/512/arrrow-09-05-1024.png',
                    'NW': 'https://cdn1.iconfinder.com/data/icons/arrow-for-love/512/arrrow-09-07-1024.png'
                }

                # Add five arrow markers in a straight line
                for i in range(5):
                    arrow_icon_url = arrow_icons.get(self.api.get_wind_direction(wind_direction), '')
                    if arrow_icon_url:
                        # Create a new CustomIcon for each marker
                        arrow_icon = folium.CustomIcon(icon_image=arrow_icon_url, icon_size=(50, 50))
                        folium.Marker([lat - 0.05 + i * 0.03, lon - 0.05 + i * 0.03], popup="Wind Direction", icon=arrow_icon).add_to(weather_map)

                map_filename = f"{city}_wind_map.html"
                weather_map.save(map_filename)

                # Open the HTML file in a web browser
                webbrowser.open_new_tab(map_filename)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
# -------------------------------------------------------------------------------------
if __name__ == "__main__":
    api_key = "" 
    app = WeatherApp(api_key)
    app.mainloop()
