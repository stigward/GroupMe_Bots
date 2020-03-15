import os
import sys
import json
import requests
import json
import datetime
import time
import re

from bs4 import BeautifulSoup as bs



from urllib.parse import urlencode
from urllib.request import Request, urlopen

from flask import Flask, request

app = Flask(__name__)


@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    if data['text'] == '!snow':
        send_message(constructReports())
        send_message(getComments())
    if data['text'] == '!map':
        send_message(getMap())
    return "ok", 200


def send_message(msg):
    url = 'https://api.groupme.com/v3/bots/post'

    data = {
        'bot_id': os.getenv('GROUPME_BOT_ID'),
        'text': msg,
    }
    request = Request(url, urlencode(data).encode())
    json = urlopen(request).read().decode()

def getSnowReport():
    url = "https://www.onthesnow.com/wyoming/jackson-hole/skireport.html"
    session = requests.session()
    resp = session.get(url)
    soup = bs(resp.text, "html.parser")
    jhole_report= soup.find("li", { "class":"today"})
    today_snow = jhole_report.find("div", {"class":"bluePill"})
    parsed_snow = re.split("[\"<>']", str(today_snow))
    today_fall = str(parsed_snow[4])
    msg = ""
    if(int(today_fall) > 12):
        msg = "Some fresh face shots coming your way. Looks like it snowed " + today_fall + " inches today!"
    elif(int(today_fall == 0)):
        msg = "No snow today sadly. Check back tomorrow"
    else:
        msg = "Decent snowfall last night. The hole got " + today_fall + " inches today!"

    return msg 

def getComments():
    url = "https://www.onthesnow.com/wyoming/jackson-hole/skireport.html"
    session = requests.session()
    resp = session.get(url)
    soup = bs(resp.text, "html.parser")
    jhole_report= soup.find("div", { "class":"snow_report_comment_wrapper"})
    parsed_snow = re.split("</div>|<br>|</br>|\n|\r|>", str(jhole_report))
    msg = "Comments from Jackson: "
    for i in range(1, len(parsed_snow)):
        if(parsed_snow[i] != ""):
            msg += (parsed_snow[i])
    return (msg)
def getWeather():
    url = "https://www.onthesnow.com/wyoming/jackson-hole/skireport.html"
    session = requests.session()
    resp = session.get(url)
    soup = bs(resp.text, "html.parser")
    jhole_report= soup.find_all("div", { "class":"temp below"})
    temps = []
    for i in jhole_report:
        parsed_snow = re.split("[\"<>']", str(i))
        temps.append(parsed_snow[4])
    return temps    

def constructReports():
    snow = getSnowReport()
    weather = getWeather()
    msg = snow + "\n"
    temps = "Summit Temp: " + weather[0] + "\nBase Temp: " + weather[1]
    msg += temps
    return(msg)

def getMap():
    return "https://www.jacksonhole.com/images/maps/2056-WinterTrailMap.FINAL2019.201.jpg"
