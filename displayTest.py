#!/usr/bin/python3
import lib.epd7in5b_V2 as eInk
from PIL import Image, ImageDraw, ImageFont
import sys
import os
import logging
import schedule
import time

def clearDisplay():
    logging.info("Clear Display")
    epd.init()
    epd.Clear()


pictureDict = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pictures')

try:
    logging.info("epd7in5b_V2 Demo")

    epd = eInk.EPD()
    logging.info("init and Clear")
    epd.init()
    epd.Clear()

    image = Image.open(os.path.join(pictureDict, 'Weihnachsbaum-b.bmp'))
    image_red = Image.open(os.path.join(pictureDict, 'Weihnachsbaum-r.bmp'))
    epd.display(epd.getbuffer(image), epd.getbuffer(image_red))
    time.sleep(10)

    clearDisplay()

    logging.info("Goto Sleep...")
    epd.sleep()

except IOError as e:
    logging.info(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    eInk.epdconfig.module_exit()
    exit()
