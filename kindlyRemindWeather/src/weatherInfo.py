# -*- coding: utf-8 -*-
import json
import urllib2
import utility
import os
import time


class NotifyWeatherInfo:
    def __init__(self):
        url = "http://api.openweathermap.org/data/2.5/forecast/city?id=1796236&APPID=5d1996aae920d60161a6e1358593e249"
        raw_content = urllib2.urlopen(url).read()
        self.content = json.loads(raw_content)

    # get weather information of the nth day from now on. The free service supplied
    # by openweathermap.org is 5 days forecast. So n must no lager than 5.
    def get_nth_day_weather(self, n):
        if n > 5 or n < 0:
            return
        tomorrow_day = utility.get_day_based_on_today(n)
        list_of_result = list()
        for index, info in enumerate(self.content['list']):
            nth_day_of_month = utility.get_day_of_month(info['dt_txt'])
            need_notify = False
            # clear day and clouds day do not need to notify.Maybe there are more.
            # on openweathermap.org website, the id of clear day and clouds day are begin with '80', so exclude it.
            if not str(info['weather'][0]['id']).startswith('80'):
                need_notify = True
            if nth_day_of_month == tomorrow_day and need_notify:
                notify_dic = dict()
                notify_dic['weatherDescription'] = info['weather'][0]['description']
                notify_dic['dt_txt'] = info['dt_txt']
                list_of_result.append(notify_dic)
        return list_of_result

    def show_notify(self, list_to_notify):
        for i in range(0, len(list_to_notify)):
            weather_description = list_to_notify[i]['weatherDescription']
            dt_txt = list_to_notify[i]['dt_txt']
            command_show_notify = "osascript -e \'tell app \"System Events\" to display notification \"" + weather_description.encode('utf-8') + "\" with title \"Weather Forecast: " + dt_txt.encode('utf-8') + "\"\'"
            os.system(command_show_notify)
            time.sleep(6.0)

weather = NotifyWeatherInfo()
# remind me weather of tomorrow
listInfo = weather.get_nth_day_weather(1)
weather.show_notify(listInfo)
