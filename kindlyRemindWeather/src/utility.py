import datetime

def getDayOfMonth(stringDateTime):
    return datetime.datetime.strptime(stringDateTime, '%Y-%m-%d %H:%M:%S').day

def getDayOfAfterToday(n):
    futureDatetime = datetime.date.today() + datetime.timedelta(days=1)
    return futureDatetime.day


