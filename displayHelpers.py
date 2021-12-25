import lib.epd7in5b_V2 as eInk
from PIL import Image, ImageDraw, ImageFont
import logging

logger = logging.getLogger('app')

def init_display(epd):
    logger.info("Init display")
    epd.init()


def clear_display(epd):
    logger.info("Clear display")
    epd.Clear()


def set_sleep(epd):
    logger.info("Set display to sleep-mode")
    epd.sleep()