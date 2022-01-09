import logging
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont
from PIL.ImageDraw import ImageDraw as TImageDraw

import lib.epd7in5b_V2 as eInk

logger = logging.getLogger('app')


def init_display(epd: eInk.EPD):
    logger.info("Init display")
    epd.init()


def clear_display(epd: eInk.EPD):
    logger.info("Clear display")
    epd.Clear()


def set_sleep(epd: eInk.EPD):
    logger.info("Set display to sleep-mode")
    epd.sleep()


def draw_text_centered(text: str, point: Tuple[float, float], canvas: TImageDraw, text_font: ImageFont.FreeTypeFont):
    text_width, _ = text_font.getsize(text)
    canvas.text((point[0] - text_width/2, point[1]),
                text, font=text_font, fill=0)


def get_font_height(font: ImageFont.FreeTypeFont):
    _, text_height = font.getsize("A")
    return text_height

def get_font_width(font: ImageFont.FreeTypeFont, text: str):
    text_width, _ = font.getsize(text)
    return text_width
