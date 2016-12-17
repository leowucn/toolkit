import os
from Foundation import *

def testNetwork():
    hostname = "http://www.bing.com/"
    response = os.system("ping -c 1 -W 2000 " + hostname + " > /dev/null 2>&1")
    #and then check the response...
    if response == 0:
        return False
    else:
        return True
