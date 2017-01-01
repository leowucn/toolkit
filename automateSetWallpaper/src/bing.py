# -*- coding: utf-8 -*-
import os
import urllib
import requests
import Foundation


class BingImageInfo:
    def __init__(self):
        self.jsonUrl = "http://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-US"
        self.response = requests.get(self.jsonUrl).json()

    def get_image_url(self):
        image_url = self.response['images'][0]['url']
        # When using vpn, the server address of bing image may be different between countries.
        if image_url.startswith("http://s.cn.bing.net"):
            return image_url
        elif not image_url.startswith("https://www.bing.com") and not image_url.startswith("http://www.bing.com"):
            image_url = "https://www.bing.com" + image_url
        return image_url

    def get_story(self):
        return self.response['images'][0]['copyright']


class EnjoyBing:
    def __init__(self, image_location_prefix):
        self.bing_image_info = BingImageInfo()
        image_url = self.bing_image_info.get_image_url()
        image_path = image_location_prefix + image_url.rsplit('/', 1)[-1]
        urllib.urlretrieve(image_url, image_path)
        self.image_path = image_path

    def set_wallpaper(self):
        set_wallpaper_script = """tell application "Finder"
        set desktop picture to POSIX file "%s"
        end tell"""
        s = Foundation.NSAppleScript.alloc().initWithSource_(set_wallpaper_script % self.image_path)
        info = s.executeAndReturnError_(None)

    def pop_up_story_window(self):
        bing_image_story = self.bing_image_info.get_story()
        command_show_story_info = "osascript -e \'tell app \"System Events\" to display notification \"" + bing_image_story.encode('utf-8') + "\" with title \"Bing Image Story\"\'"
        os.system(command_show_story_info)
