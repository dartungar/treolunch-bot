import json
import os
import random
import requests
from helpers import get_declinated_minute_word
from datetime import datetime, timedelta


class Weather:
    '''encapsulates weather-related logic. \n
        getting actual weather from API & getting it's custom-defined "score" (./weather.json)'''

    def __init__(self, coordinates, api_key):
        self._api_key = api_key
        self._coordinates = coordinates
        self._last_request_time = None
        self._last_request_weather = None
        with open("weather.json", encoding='utf-8') as file:
            self.weather_data = json.load(file)

    @property
    def current_weather(self):
        '''Get actual weather data, if last request was > 15m ago. Else return current data'''
        if not self._last_request_time or not self._last_request_weather or self._last_request_time < datetime.now() - timedelta(minutes=15):
            self._last_request_time = datetime.now()
            self._last_request_weather = requests.get(
                f'https://api.openweathermap.org/data/2.5/weather?lat={self._coordinates["lat"]}&lon={self._coordinates["lon"]}&units=metric&lang=ru&appid={self._api_key}').json()
        return self._last_request_weather

    def _get_weather_rating(self) -> int:
        '''  get 'goodness' rating of the weather based on its openweathermap code.\n
            'clear' weather is 1, 'heavy thunderstorm' is 0.01, etc.\n
            data is in ./weather.json'''
        rating = [w for w in self.weather_data if w['code']
                  == str(self._last_request_weather['weather'][0]['id'])][0]['rating']
        return rating


# encapculated place-choosing operations
# 'given this weather, what do you recommend?'
class PlaceChooser:
    # load places & weather info, env variables
    def __init__(self) -> None:
        with open("places.json", encoding='utf-8') as file:
            self.places = json.load(file)

    def _choose_place(self, temp: int, weather_rating: int) -> dict:
        '''Get place based on current weather and distance to the place. \n
            The worse weather's rating, the less distance we are 'willing to walk'.\n
            Extreme temperature takes its toll, too.'''
        max_distance = 1500 * weather_rating
        # if it's too warm or too cold, we probably wouldn't want to go too far
        tempdelta = 0
        if temp > 24:
            tempdelta = temp - 24
        elif temp < -3:
            tempdelta = abs(temp - -3)
        tempdelta = abs(tempdelta**2 * 10)
        max_distance -= tempdelta
        if max_distance < 100:
            max_distance = 100
        suitable_places = [
            p for p in self.places if p['distance'] <= max_distance]
        place_obj = random.choice(suitable_places)
        place_name = place_obj['name']
        if place_obj.get('options'):
            option = random.choice(place_obj['options'])
            place_name += f': {option}'

        return {'name': place_name, 'distance': place_obj['distance']}

    def get_random_place(self, weather: dict, weather_rating: int) -> dict:
        '''choose place based on weather data'''
        try:
            place = self._choose_place(
                weather['main']['feels_like'], weather_rating)
            return place
        except Exception as e:
            raise e

    def get_full_info(self, weather: dict, weather_rating: int) -> str:
        '''get info & create full response string'''
        place = self.get_random_place(weather, weather_rating)
        temp = weather['main']['feels_like']
        walking_minutes = round(place['distance'] / 80)
        return f"Сейчас на улице {weather['weather'][0]['description']}.\nТемпература по ощущениям: {temp}С.\nПредлагаю сходить в {place['name']}. \nИдти примерно {walking_minutes} {get_declinated_minute_word(walking_minutes)}."


# for testing
if __name__ == '__main__':
    weather = Weather(
        coordinates={'lat': 55.769505, 'lon': 37.672348}, api_key=os.getenv('API_KEY'))
    bot = PlaceChooser()
    print(bot.get_full_info(weather.current_weather, weather._get_weather_rating()))
