# -*- coding: utf-8 -*-
import json
import urllib2
import utility
from Foundation import *
import os
import time
import datetime

class notifyWeatherInfo:
    def __init__(self):
        url = "http://api.openweathermap.org/data/2.5/forecast/city?id=1796236&APPID=5d1996aae920d60161a6e1358593e249"
        rawContent = urllib2.urlopen(url).read()
        self.content = json.loads(rawContent)
    #get weather information of the nth day from now on. The free service supplied by openweathermap.org is 5 days forecast. So n must no lager than 5.
    def getNthDayWeather(self, n):
        if n > 5 and n < 0:
            return
        #specifiedDayOfMonth = utility.getDayOfToday() + datetime.timedelta(days=n)
        specifiedDayOfMonth = utility.getDayOfAfterToday(n)
        listOfResult = list()
        for index, info in enumerate(self.content['list']):
            dayOfMonth = utility.getDayOfMonth(info['dt_txt'])
            needNotify = self.whetherNeedNotify(info['weather'][0]['id']) 
            if specifiedDayOfMonth == dayOfMonth and needNotify:
                notifyDic = dict()
                notifyDic['weatherDescription'] = info['weather'][0]['description']
                notifyDic['dt_txt'] = info['dt_txt']
                listOfResult.append(notifyDic)
        return listOfResult

        #groupId indicate which kind of weather. You can get information in more detial from http://openweathermap.org/weather-conditions.
    def whetherNeedNotify(self, groupId):
        #clear day and clouds day do not need notify.Maybe there are more.
        #on openweathermap.org website, the id of clear day and clouds day are begin with '80', so exclude it.
        if str(groupId).startswith('80'):
            return False
        return True
    
    def showNotify(self, listToNotify):
        for i in range(0, len(listToNotify)):
            weatherDescription = listToNotify[i]['weatherDescription']
            dt_txt = listToNotify[i]['dt_txt']
            commandShowNotify = "osascript -e \'tell app \"System Events\" to display notification \"" + weatherDescription.encode('utf-8') + "\" with title \"Weather Forecast: " + dt_txt.encode('utf-8') + "\"\'"
            os.system(commandShowNotify)
            time.sleep(20.0)

weather = notifyWeatherInfo()
#remind me weather information of tomorrow
listInfo = weather.getNthDayWeather(1)
weather.showNotify(listInfo)
