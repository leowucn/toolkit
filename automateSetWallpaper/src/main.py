# -*- coding: utf-8 -*-
import time
from bing import *
import urllib
from os.path import expanduser

# the directory in which to store bing image
image_store_dir = expanduser("~") + '/Pictures/'


def test_network():
    code = urllib.urlopen("http://www.bing.com/").getcode()
    if code != 200:
        return False
    return True


def check_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


if __name__ == "__main__":
    try_times = 0
    while True:
        ok = test_network()
        if ok:
            enjoy = EnjoyBing(image_store_dir)
            enjoy.set_wallpaper()
            enjoy.pop_up_story_window()
            break
        time.sleep(60)
        try_times += 1
        if try_times == 10:
            break


