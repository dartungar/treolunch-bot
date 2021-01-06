import csv
import json

weather_data = []

with open("./weather.csv") as data:
    reader = csv.reader(data, delimiter=",")
    for row in reader:
        weather_row = {"code": row[0], "weight": 1,
                       "name": row[1], "description": row[2]}
        weather_data.append(weather_row)

with open("./weather.json", "w") as data:
    data.write(json.dumps(weather_data))
