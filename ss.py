#!/usr/bin/env python
"""
A pygame program to show a slideshow of all images buried in a given directory.

Originally Released: 2007.10.31 (Happy halloween!)

"""
from __future__ import division
import argparse
import os
import stat
import sys
import time
import datetime


import pygame
from pygame.locals import QUIT, KEYDOWN, K_ESCAPE


#weather
import pyowm



file_list = []  # a list of all images being shown
title = "pgSlideShow | My Slideshow!"  # caption of the window...
waittime = 5   # default time to wait between images (in seconds)


def walktree(top, callback):
    """recursively descend the directory tree rooted at top, calling the
    callback function for each regular file. Taken from the module-stat
    example at: http://docs.python.org/lib/module-stat.html
    """
    for f in os.listdir(top):
        pathname = os.path.join(top, f)
        mode = os.stat(pathname)[stat.ST_MODE]
        if stat.S_ISDIR(mode):
            # It's a directory, recurse into it
            walktree(pathname, callback)
        elif stat.S_ISREG(mode):
            # It's a file, call the callback function
            callback(pathname)
        else:
            # Unknown file type, print a message
            print 'Skipping %s' % pathname


def addtolist(file, extensions=['.png', '.jpg', '.jpeg', '.gif', '.bmp']):
    """Add a file to a global list of image files."""
    global file_list  # ugh
    filename, ext = os.path.splitext(file)
    e = ext.lower()
    # Only add common image types to the list.
    if e in extensions:
        print 'Adding to list: ', file
        file_list.append(file)
        file_list.sort()
    else:
        print 'Skipping: ', file, ' (NOT a supported image)'


def input(events):
    """A function to handle keyboard/mouse/device input events. """
    for event in events:  # Hit the ESC key to quit the slideshow.
        if (event.type == QUIT or
            (event.type == KEYDOWN and event.key == K_ESCAPE)):
            pygame.quit()


def timeSince(lastTime,interval):
    if (time.time() - lastTime)>=interval:
        return True
    else:
        return False


def main(startdir="."):
    global file_list, title, waittime
    lastSwitch=time.time()
    lastWeather=time.time()

    owm = pyowm.OWM('4cc9ae1d116c7e70c145252ab605f260')
    observation = owm.weather_at_place('Ottawa,CA')
    w = observation.get_weather()
    temperature=(w.get_temperature('celsius'))['temp']
    status=w.get_status()
    #print w

    pygame.init()

    # Test for image support
    if not pygame.image.get_extended():
        print "Your Pygame isn't built with extended image support."
        print "It's likely this isn't going to work."
        sys.exit(1)

    walktree(startdir, addtolist)  # this may take a while...
    if len(file_list) == 0:
        print "Sorry. No images found. Exiting."
        sys.exit(1)

    modes = pygame.display.list_modes()
    print max(modes)
    pygame.display.set_mode(max(modes))

    screen = pygame.display.get_surface()
    screen_width, screen_height= screen.get_size()
    pygame.display.set_caption(title)
    #pygame.display.toggle_fullscreen()
    pygame.display.set_mode(max(modes),pygame.FULLSCREEN)

    pygame.mouse.set_visible(0)

    #create font
    timeFont = pygame.font.Font("indulta/Indulta-SemiSerif-boldFFP.otf", 100)
    dateFont = pygame.font.Font("indulta/Indulta-SemiSerif-boldFFP.otf", 60)
    weatherFont = pygame.font.Font("indulta/Indulta-SemiSerif-boldFFP.otf", 60)

    print str(waittime) +"wait time"


    current = 0
    num_files = len(file_list)
    while(True):
        try:
            img = pygame.image.load(file_list[current])
            img = img.convert()
            tempX,tempY=img.get_size()
            ratio =tempX/tempY
            center = (screen_height-(screen_width/ratio))/2
            margin = 10
            tempSize=(screen_width,int(screen_width/ratio))
            print str(img.get_size())+" to "+ str(tempSize) +"and ratio: "+str(ratio)
            # rescale the image to fit the current display
            img = pygame.transform.scale(img, tempSize)
            screen.blit(img, (0, center))

            #gets current weather
            if timeSince(lastWeather,30):
                observation = owm.weather_at_place('Ottawa,CA')
                w = observation.get_weather()
                temperature=(w.get_temperature('celsius'))['temp']
                status=w.get_status()
                print status
                lastWeather=time.time()
                print "updateing weather"

            #gets the current time and displays it
            #EU FORMATING:
            #timeText=datetime.datetime.now().strftime("%H:%M")
            #dateText=datetime.datetime.now().strftime("%d %B, %Y")
            #US FORMATING:            
            timeText=datetime.datetime.now().strftime("%I:%M%p")
            dateText=datetime.datetime.now().strftime("%B %d, %Y")
            weatherText=str(int(temperature))+"`C  "+status


            timeLabel = timeFont.render(timeText, 1, (255,255,255))
            dateLabel = dateFont.render(dateText, 1, (255,255,255))
            weatherLabel = weatherFont.render(weatherText, 1, (255,255,255))

            timeWidth, timeHeight= timeLabel.get_size()
            dateWidth, dateHeight= dateLabel.get_size()
            weatherWidth, weatherHeight= weatherLabel.get_size()

            screen.blit(weatherLabel, (0, screen_height-weatherHeight))

            screen.blit(timeLabel, (screen_width-timeWidth, screen_height-timeHeight-dateHeight-center-margin))
            screen.blit(dateLabel, (screen_width-dateWidth, screen_height-dateHeight-center-margin))

            pygame.display.flip()

            input(pygame.event.get())
            time.sleep(1/60)
        except pygame.error as err:
            print "Failed to display %s: %s" % (file_list[current], err)
            sys.exit(1)

        # When we get to the end, re-start at the beginning
        if timeSince(lastSwitch,waittime):
            current = (current + 1) % num_files;
            lastSwitch=time.time()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Recursively loads images '
        'from a directory, then displays them in a Slidshow.'
    )

    parser.add_argument(
        'path',
        metavar='ImagePath',
        type=str,
        default='.',
        nargs="?",
        help='Path to a directory that contains images'
    )
    parser.add_argument(
        '--waittime',
        type=int,
        dest='waittime',
        action='store',
        default=1,
        help='Amount of time to wait before showing the next image.'
    )
    parser.add_argument(
        '--title',
        type=str,
        dest='title',
        action='store',
        default="pgSlidShow | My Slideshow!",
        help='Set the title for the display window.'
    )
    args = parser.parse_args()
    #waittime = args.waittime

    title = args.title
    main(startdir=args.path)
