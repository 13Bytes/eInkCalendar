#!/usr/bin/python3
import sys
import os
import logging
import time

libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

from waveshare_epd import epd7in5b_V2
from PIL import Image,ImageDraw,ImageFont


def clearDisplay():
    logging.info("Clear Display")
    epd.init()
    epd.Clear()

picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pictures')

try:
    logging.info("epd7in5b_V2 Demo")

    epd = epd7in5b_V2.EPD()
    logging.info("init and Clear")
    epd.init()
    epd.Clear()

    Himage = Image.open(os.path.join(picdir, 'Weihnachsbaum-b.bmp'))
    Himage_red = Image.open(os.path.join(picdir, 'Weihnachsbaum-r.bmp'))
    epd.display(epd.getbuffer(Himage),epd.getbuffer(Himage_red))
    time.sleep(10)

    clearDisplay()

    logging.info("Goto Sleep...")
    epd.sleep()
    
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd7in5b_V2.epdconfig.module_exit()
    exit()

