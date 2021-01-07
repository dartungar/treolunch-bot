import json
import os
import random
import requests
from helpers import get_declinated_minute_word


class PlaceChooser:
    # load places & weather info, env variables
    def __init__(self) -> None:
        with open("places.json", encoding='utf-8') as file:
            self.places = json.load(file)
        with open("weather.json", encoding='utf-8') as file:
            self.weather = json.load(file)

        try:
            self.api_key = os.getenv('API_KEY')
        except:
            raise EnvironmentError('API_KEY env variable not found!')

    # get weather data for given coordinates from openweathermap API
    # default coords: Treolan office on Dobro5
    def _get_current_weather(self, location={'lat': 55.769505, 'lon': 37.672348}):
        lat, lon = location['lat'], location['lon']
        resp = requests.get(
            f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&lang=ru&appid={self.api_key}')
        if resp.status_code != 200:
            raise Exception(
                f'Request was not successful: code {resp.status_code}')
        return resp.json()

    # get 'goodness' rating of the weather based on its openweathermap code
    # 'clear' weather is 1, 'heavy thunderstorm' is 0.01, etc.
    # see ./weather.json
    def _get_weather_rating(self, code):
        rating = [w for w in self.weather if w['code']
                  == str(code)][0]['rating']
        return rating

    # the better the weather is, the farther places we can/want to go
    # this function simulates that
    def _choose_place(self, temp, weather_rating):
        max_distance = 1500 * weather_rating
        # if it's too warm or too cold, we probably wouldn't want to go too far
        if temp > 26 or temp < -10:
            max_distance /= 2
        suitable_places = [
            p for p in self.places if p['distance'] <= max_distance]
        place_obj = random.choice(suitable_places)
        place_name = place_obj['name']
        if place_obj.get('options'):
            option = random.choice(place_obj['options'])
            place_name += f': {option}'

        return {'name': place_name, 'distance': place_obj['distance']}

    # choose place based on weather data
    def get_random_place(self, weather):
        try:
            place = self._choose_place(
                weather['main']['feels_like'], self._get_weather_rating(weather['weather'][0]['id']))
            return place
        except Exception as e:
            raise e

    # get info & create full response string
    def get_full_info(self):
        weather = self._get_current_weather()
        place = self.get_random_place(weather)
        walking_minutes = round(place['distance'] / 80)
        return f"Сейчас на улице {weather['weather'][0]['description']}. \nТемпература по ощущениям: {weather['main']['feels_like']}С. \nПредлагаю сходить в {place['name']}. \nИдти примерно {walking_minutes} {get_declinated_minute_word(walking_minutes)}."


# for testing
if __name__ == '__main__':
    bot = PlaceChooser()
    print(bot.get_full_info())
