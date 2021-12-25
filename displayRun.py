#!/usr/bin/python3
import lib.epd7in5b_V2 as eInk
from PIL import Image, ImageDraw, ImageFont
import sys
import os
import logging
import schedule
import time
from displayHelpers import *


CURRENT_DICT = os.path.dirname(os.path.realpath(__file__))
PICTURE_DICT = os.path.join(CURRENT_DICT, 'pictures')
FONT_DICT = os.path.join(CURRENT_DICT, 'fonts')

DEBUG = True

FONT_ROBOTO = ImageFont.truetype(
    os.path.join(FONT_DICT, 'Roboto-Black.ttf'), 16)


def main():
    try:
        epd = eInk.EPD()

        if DEBUG:
            print("DEBUG-Mode activated (only image export)")
        else:
            init_display(epd)

        image_blk = Image.open(os.path.join(PICTURE_DICT, 'bank.bmp'))
        image_red = Image.open(os.path.join(PICTURE_DICT, 'bank.bmp'))
        draw_blk = ImageDraw.Draw(image_blk)
        draw_red = ImageDraw.Draw(image_red)

        display_content(epd, image_blk, image_red)

    except IOError as e:
        logging.info(e)

    except KeyboardInterrupt:
        logging.info("ctrl + c:")
        eInk.epdconfig.module_exit()
        exit()


def display_content(epd, image_blk, image_red):
    if DEBUG:
        print("DEBUG-Mode activated (only image export)")
    else:
        epd.display(epd.getbuffer(image_blk), epd.getbuffer(image_red))
        set_sleep(epd)


if __name__ == '__main__':
    main()
