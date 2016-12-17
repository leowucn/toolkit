import time
from bing import *
from utility import *

#There are cases when I just startup computer or I was in a place which has no valid wireless networks. I should try ping bing.com
startTime = time.time()
tryTimes = 0
while True:
    networkReachable = testNetwork()
    if networkReachable == True:
        enjoy = EnjoyBing()
        enjoy.setWallpaper()
        enjoy.popUpStoryWindow()
        break
    time.sleep(60.0 - ((time.time() - startTime) % 60.0))
    tryTimes = tryTimes + 1
    if tryTimes == 10:
        break
