import os
import sys
import json
import requests
import json
import datetime
import time
import re

from bs4 import BeautifulSoup as bs


apiKey = "1e53f4bceed443fd9ad212613191302"
timeDict = {200 : "0", 500 : "1", 800 : "2", 1100 : "3", 1400 : "4", 1700 : "5", 2000 : "6", 2300 : "7"}
snowfallList = []
snowfallDict = {}

from urllib.parse import urlencode
from urllib.request import Request, urlopen

from flask import Flask, request

app = Flask(__name__)


@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    log('Recieved {}'.format(data))
    if data['text'] == '!squaw':
        msg = forecast()
        send_message(msg)
    if data['text'] == '!snow':
        msg = snowfall()
        send_message(msg)

    return "ok", 200


def send_message(msg):
    url = 'https://api.groupme.com/v3/bots/post'

    data = {
        'bot_id': os.getenv('GROUPME_BOT_ID'),
        'text': msg,
    }
    request = Request(url, urlencode(data).encode())
    json = urlopen(request).read().decode()


def log(msg):
    print(str(msg))
    sys.stdout.flush()

def getSquawResp():
    global apiKey
    url = "http://api.worldweatheronline.com/premium/v1/ski.ashx?key=" \
          + apiKey + "&num_of_days=1&q=Squaw+Valley,ca&format=json&date=today"
    resp = requests.get(url)
    return resp.text
def parseResp():
    jsonResp = getSquawResp()
    jsonParsed = flatten_json(json.loads(jsonResp))

    return jsonParsed

def getCurrentTime():
    curr = time.strftime("%H%M", time.localtime())
    min = 2400
    for i, v in enumerate(timeDict.keys()):
        val = int(curr) - v
        if abs(val) < min:
            min = v
    return min



def forecast():
    count = countdown()
    jsonParsed = parseResp()
    sunrise = jsonParsed['data_weather_0_astronomy_0_sunrise']
    sunset = jsonParsed['data_weather_0_astronomy_0_sunset']
    maxtemp = jsonParsed['data_weather_0_bottom_0_maxtempF']
    mintemp = jsonParsed['data_weather_0_bottom_0_mintempF']
    chanceofsnow = jsonParsed['data_weather_0_chanceofsnow']
    totalsnowfall = jsonParsed['data_weather_0_totalSnowfall_cm']

    s = getCurrentTime()

    toptemp = jsonParsed['data_weather_0_hourly_'+timeDict.get(s)+'_top_0_tempF']
    bottontemp = jsonParsed['data_weather_0_hourly_'+timeDict.get(s)+'_bottom_0_tempF']
    message = "Hello! " + count + "Today at Squaw Valley:\nCurrently, at the top of the mountain it is " + toptemp + " and at the base it is " + bottontemp + "\n\nsunrise: " + sunrise + "\nsunset: " + sunset + "\nmin temp at base: " \
              + mintemp + "\nmax temp at base: " + maxtemp + "\nchance of snow: " + chanceofsnow + "%"\
              + "\nexpected snowfall today: " + str(float(totalsnowfall) * 0.393701) + " inches"
    return message

def flatten_json(nested_json):

    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(nested_json)
    return out

def makeSnowDict():
    snowfallDict['overnight'] = snowfallList[0]
    snowfallDict['24 hours'] = snowfallList[1]
    snowfallDict['7 days'] = snowfallList[2]
    snowfallDict['base'] = snowfallList[3]
    snowfallDict['season total'] = snowfallList[4]

def snowfall():
    global snowfallList
    session = requests.session()
    baseURL = "https://squawalpine.com/skiing-riding/weather-conditions-webcams/snow-weather-reports-lake-tahoe"
    resp = session.get(baseURL)
    soup = bs(resp.text, "html.parser")
    div = soup.find("div", {"class":"elevation-1 content active"})
    p = div.find_all("p",{"class": "value"})

    for i in p:
        if "in</p>" in str(i):
            arr = re.split("<span>|</span>", str(i))
            snowfallList.append(arr[1])
    makeSnowDict()

    msg = "Snow Report: \n" \
          "Overnight: " + snowfallDict['overnight'] + " in \n" \
                                                      "24 Hours: " + snowfallDict['24 hours'] + " in \n" \
                                                                                                "7 Days: " + snowfallDict['7 days'] + " in \n" \
                                                                                                                                      "Base: " + snowfallDict['base'] + " in\n" \
                                                                                                                                                                        "Season Total: " + snowfallDict['season total'] + " in\n"
    return msg

def countdown():
    countdown_days = (datetime.datetime(2019, 3, 16) - datetime.datetime.now()).days
    till_midnight = 24 - datetime.datetime.now().hour + 5
    minutes = 60 - datetime.datetime.now().minute
    if till_midnight >= 24:
        countdown_days += 1
        till_midnight -= 24
    return "You're going to shred the gnar in " + str(countdown_days) + " days, " + str(till_midnight) + " hours, and " + str(minutes) + " minutes!\n\n"

