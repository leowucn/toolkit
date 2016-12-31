# -*- coding: utf-8 -*-
import os
import urllib
import requests
from Foundation import *
import subprocess
from utility import *

imageLocationPrefix = "/Users/leo/Pictures/"

class BingImageInfo(object):
    def __init__(self):
        self.jsonUrl = "http://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-US"
        self.response = requests.get(self.jsonUrl).json()
    def getImageUrl(self):
        imageUrl = self.response['images'][0]['url']
        #I often use vpn, and found that the server address of bing image is different between countries.
        if imageUrl.startswith("http://s.cn.bing.net"):
            return imageUrl
        elif imageUrl.startswith("https://www.bing.com") == False and imageUrl.startswith("http://www.bing.com") == False:
            imageUrl = "https://www.bing.com" + imageUrl
        return imageUrl
    def getStory(self):
        return self.response['images'][0]['copyright']

class EnjoyBing(BingImageInfo):
    def __init__(self):
        super(EnjoyBing, self).__init__() #super() method is used for access parent class or sibling class.An alternatvie way is "BingImageInfo.__init__()"
        imageUrl = self.getImageUrl()
        imageLocationPrefix = "/Users/leo/Pictures/"
        imageName = imageUrl.rsplit('/', 1)[-1]
        urllib.urlretrieve(imageUrl, imageLocationPrefix + imageName)
        self.imagePath = imageLocationPrefix + imageName
    def setWallpaper(self):
        #/Users/leowu/Pictures/BingImages/1.jpg
        applescriptForSetWallpaper = """tell application "Finder"
        set desktop picture to POSIX file "%s"
        end tell"""
        s = NSAppleScript.alloc().initWithSource_(applescriptForSetWallpaper%self.imagePath)
        info = s.executeAndReturnError_(None) 
    def popUpStoryWindow(self):
        #terminal-notifier -message "Hello, this is my message" -title "Message Title"
        #osascript -e 'tell app "System Events" to display notification "Lorem ipsum dolor sit amet" with title "Title"' 
        bingImageStory = self.getStory()
        commandShowStoryInfo = "osascript -e \'tell app \"System Events\" to display notification \"" + bingImageStory.encode('utf-8') + "\" with title \"Bing Image Story\"\'"
        os.system(commandShowStoryInfo)
