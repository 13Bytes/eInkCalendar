#!/usr/bin/python3
import lib.epd7in5b_V2 as eInk
from PIL import Image, ImageDraw, ImageFont
from PIL.ImageDraw import ImageDraw as TImageDraw
from PIL.Image import Image as TImage
import sys
import os
import logging
import schedule
import time
import calendar
from displayHelpers import *

logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))
logger = logging.getLogger('app')

CURRENT_DICT = os.path.dirname(os.path.realpath(__file__))
PICTURE_DICT = os.path.join(CURRENT_DICT, 'pictures')
FONT_DICT = os.path.join(CURRENT_DICT, 'fonts')

DEBUG = True

FONT_ROBOTO_H1 = ImageFont.truetype(
    os.path.join(FONT_DICT, 'Roboto-Black.ttf'), 40)
LINE_WIDTH = 3


def main():
    try:
        epd = eInk.EPD()

        if DEBUG:
            logger.info("DEBUG-Mode activated...")
        else:
            init_display(epd)

        image_blk =  Image.new('1', (epd.height, epd.width),255)
        image_red = Image.new('1', (epd.height, epd.width),255)
        draw_blk = ImageDraw.Draw(image_blk)
        draw_red = ImageDraw.Draw(image_red)

        draw_content(draw_blk, draw_red, epd.width, epd.height)
        render_content(epd, image_blk, image_red)

    except Exception as e:
        logger.warning(e)
        if not DEBUG:
            logger.info("Trying to module_exit()")
            eInk.epdconfig.module_exit()
        raise e


def draw_content(draw_blk: TImageDraw, draw_red: TImageDraw,  height: int, width: int):
    now = time.localtime()
    max_days_in_month = calendar.monthrange(now.tm_year, now.tm_mon)[1]
    day_str = time.strftime("%A")
    day_number = now.tm_mday
    month_str = time.strftime("%B") + ' ' + time.strftime("%Y")

    # Date-Text
    with_day_number, _ = FONT_ROBOTO_H1.getsize(str(day_number))
    draw_blk.text((width/2 - with_day_number/2, 0),
                  str(day_number), font=FONT_ROBOTO_H1, fill=0)

    draw_blk.line((0, height/15, width, height/15), fill=0, width=LINE_WIDTH)
    draw_blk.arc((0, 0, height/15, height/15), 0,
                 360, fill=0, width=LINE_WIDTH)


def render_content(epd: eInk.EPD, image_blk: TImage, image_red: TImage):
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
