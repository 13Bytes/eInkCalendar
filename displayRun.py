#!/usr/bin/python3
import lib.epd7in5b_V2 as eInk
from PIL import Image, ImageDraw, ImageFont
import sys
import os
import logging
import schedule
import time
from displayHelpers import *

logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))
logger = logging.getLogger('app')

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
            logger.info("DEBUG-Mode activated...")
        else:
            init_display(epd)

        image_blk = Image.open(os.path.join(PICTURE_DICT, 'blank.bmp'))
        image_red = Image.open(os.path.join(PICTURE_DICT, 'blank.bmp'))
        draw_blk = ImageDraw.Draw(image_blk)
        draw_red = ImageDraw.Draw(image_red)

        display_content(epd, image_blk, image_red)

    except Exception as e:
        logger.warning(e)
        if not DEBUG:
            logger.info("Trying to module_exit()")
            eInk.epdconfig.module_exit()
        raise e


def display_content(epd, image_blk, image_red):
    if DEBUG:
        logger.info("exporting finial images")
        image_blk.save("EXPORT-black.bmp")
        image_red.save("EXPORT-red.bmp")
    else:
        logger.info("writing on display")
        epd.display(epd.getbuffer(image_blk), epd.getbuffer(image_red))
        set_sleep(epd)


if __name__ == '__main__':
    main()
