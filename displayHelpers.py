import lib.epd7in5b_V2 as eInk
from PIL import Image, ImageDraw, ImageFont
import logging


def init_display(epd):
    logging.info("Init display")
    epd.init()


def clear_display(epd):
    logging.info("Clear display")
    epd.Clear()


def set_sleep(epd):
    logging.info("Set display to sleep-mode")
    epd.sleep()
