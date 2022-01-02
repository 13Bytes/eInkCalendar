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

FONT_ROBOTO_DATE = ImageFont.truetype(
    os.path.join(FONT_DICT, 'Roboto-Black.ttf'), 200)
FONT_ROBOTO_H1 = ImageFont.truetype(
    os.path.join(FONT_DICT, 'Roboto-Black.ttf'), 40)
FONT_ROBOTO_H2 = ImageFont.truetype(
    os.path.join(FONT_DICT, 'Roboto-Black.ttf'), 30)
FONT_ROBOTO_P = ImageFont.truetype(
    os.path.join(FONT_DICT, 'Roboto-Black.ttf'), 20)
LINE_WIDTH = 3


def main():
    try:
        epd = eInk.EPD()

        if DEBUG:
            logger.info("DEBUG-Mode activated...")
        else:
            init_display(epd)

        image_blk = Image.new('1', (epd.height, epd.width), 255)
        image_red = Image.new('1', (epd.height, epd.width), 255)
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
    PADDING_L = width/10
    now = time.localtime()
    max_days_in_month = calendar.monthrange(now.tm_year, now.tm_mon)[1]
    day_str = time.strftime("%A")
    day_number = now.tm_mday
    month_str = time.strftime("%B")

    # draw_text_centered(str(day_number), (width/2, 0), draw_blk, FONT_ROBOTO_H1)

    # Heading
    line_height = height/20
    draw_blk.line((PADDING_L, line_height, width, line_height),
                  fill=0, width=LINE_WIDTH)
    draw_blk.text((PADDING_L, line_height), month_str.upper(),
                  font=FONT_ROBOTO_H2, fill=0)
    line_height += get_font_height(FONT_ROBOTO_H2)

    # Date
    current_font_height = get_font_height(FONT_ROBOTO_DATE)
    draw_blk.text((PADDING_L, line_height - current_font_height/10),
                  str(day_number), font=FONT_ROBOTO_DATE, fill=0)
    line_height += current_font_height

    # Month-Overview
    line_height += height/100
    day_of_month = str(day_number) + "/" + str(max_days_in_month)
    draw_blk.text((PADDING_L, line_height), day_of_month,
                  font=FONT_ROBOTO_P, fill=0)

    tmp_right_aligned = width - \
        get_font_width(FONT_ROBOTO_P, day_str) - get_font_height(FONT_ROBOTO_P)
    draw_blk.text((tmp_right_aligned, line_height), day_str.upper(),
                  font=FONT_ROBOTO_P, fill=0)

    line_height += get_font_height(FONT_ROBOTO_P) + height/100
    draw_blk.line((PADDING_L, line_height, width, line_height),
                  fill=0, width=LINE_WIDTH)

    # Month-Tally-Overview
    line_height += height/100
    tally_height = height/40
    tally_padding = width/60
    x_position = PADDING_L + LINE_WIDTH/2
    for i in range(0, day_number):
        draw_blk.line((x_position, line_height, x_position, line_height + tally_height), fill=0, width=LINE_WIDTH)
        x_position += tally_padding
    line_height += tally_height


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
