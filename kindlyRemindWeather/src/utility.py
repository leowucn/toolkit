# -*- coding: utf-8 -*-
import datetime


def get_day_of_month(string_date_time):
    return datetime.datetime.strptime(string_date_time, '%Y-%m-%d %H:%M:%S').day


def get_day_based_on_today(n):
    future_date_time = datetime.date.today() + datetime.timedelta(n)
    return future_date_time.day

