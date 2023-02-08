#!/usr/bin/env python
import os
import requests
import json
import datetime
import printer



REFRESH_TOKEN = "1//0dcPCJi9-Lgt9CgYIARAAGA0SNgF-L9IrcWqBtXkal5fNnZOrO1htqzVaKHXjI7vs_rKurhUY8QqBbkms-obJa87_w5vtaPk6kA"
CALENDAR_ID = "dawsontheroux@gmail.com"

def refreshToken():
    f = open("client_secret.json")
    secretJson = json.load(f)["installed"]
    paramDict = {
        "client_id": secretJson["client_id"],
        "client_secret": secretJson["client_secret"],
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN
    }
    
    refreshURL = "https://oauth2.googleapis.com/token"

    r = requests.post(refreshURL, params=paramDict)
    if "error" in r.text:
        raise "Failed to refresh the token"

    return r.text


def sendGetRequest(url, paramDict, token):
    headers = {}
    headers["Authorization"] = f"Bearer {token}"
    r = requests.get(url, params=paramDict, headers = headers)
    #print(f"\n\nThe Request URL was: {r.url}\n\n\\")        
    return r


def getDateTimeTomorrow(day=None):
    """ Gets the date and time in the format googleAPI likes it 
        for the start and end of the day.
    """

    currentTime = datetime.datetime.now()
    currentHour = currentTime.hour
    currentMin = currentTime.minute

    # The minumum today at 12:00AM, which is today minus the current hours and minutes in the day.
    min = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours = -currentHour, minutes = -currentMin)
    # The max is today at 11:59PM, which is min + 1 day -1 minute.
    max = min + datetime.timedelta(days=1, minutes = -1)

    return min.isoformat(), max.isoformat()


def getListOfEvents():
    refreshDict = json.loads(refreshToken())
    accessToken = refreshDict["access_token"]
    #print(f"Printing the refresh dict: {refreshDict}")
    paramsDict = {}
    eventsList = []
    
    min, max = getDateTimeTomorrow()

    # The parameters to be used for the initial GET requests for the events list.
    paramsDict["timeMin"] = min
    paramsDict["timeMax"] = max
    paramsDict["orderBy"] = "startTime"
    paramsDict["singleEvents"] = "True"

    # Send a request to get all the list of events in a day.
    url = f"https://www.googleapis.com/calendar/v3/calendars/{CALENDAR_ID}/events"
    eventsRequest = sendGetRequest(url, paramsDict, accessToken)

    # Send a GET request for every event because we want the start and end TIMES.
    eventsResultsDict = json.loads(eventsRequest.text)
    for event in eventsResultsDict["items"]:
        eventId = event["id"]
        paramsDict = {}
        paramsDict["timeZone"] = "ET"
        url = f"https://www.googleapis.com/calendar/v3/calendars/{CALENDAR_ID}/events/{eventId}"
        eventRequest = sendGetRequest(url, paramsDict, accessToken)
        eventsList.append(json.loads(eventRequest.text))

    return eventsList

def createPrinterFile():
    eventsList = getListOfEvents()
    #print(f"\n\nThe events list is: \n {eventsList}")
    printer.createDocument(eventsList)

def main():
    createPrinterFile()
    printer.printDocument()

if __name__ == "__main__":
    main()
    
