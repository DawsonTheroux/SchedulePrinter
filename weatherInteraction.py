#!/usr/bin/python
import os
import json
import requests


def getDayTemperature():
    # Returns the Icon for the day as well as the high and low for the day.
    url = "http://dataservice.accuweather.com/forecasts/v1/daily/1day/55487"
    paramsDict = {
            "apikey": "bGysIUQ37LIj8ep1zHBMyqTkoM4ihx79",
            "language": "en-us",
            "metric": "true",
            "details":"false"
            }
    r = requests.get(url, params=paramsDict)
    # print(f"Return of AccuWeather: {r.text}")
    temperatureData = json.loads(r.text)["DailyForecasts"][0]
    dailyHigh = temperatureData["Temperature"]["Maximum"]["Value"]
    dailyLow  = temperatureData["Temperature"]["Minimum"]["Value"]
    description = temperatureData["Day"]["IconPhrase"]
    icon      = temperatureData["Day"]["Icon"]
    return int(dailyHigh), int(dailyLow), description, icon


def main():
    getDayTemperature()


if __name__ == "__main__":
    main()
