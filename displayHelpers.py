import logging
import os
from typing import List, Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from PIL.Image import Image as TImage
from PIL.ImageDraw import ImageDraw as TImageDraw

import lib.epd7in5b_V2 as eInk

logger = logging.getLogger('app')
CURRENT_DICT = os.path.dirname(os.path.realpath(__file__))
PICTURE_DICT = os.path.join(CURRENT_DICT, 'pictures')


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


def convert_image_to_screen(image: TImage) -> TImage:
    def convert_f(e):
        if (e > 0):
            return 0
        else:
            return 2
    vfunc = np.vectorize(convert_f)

    image_array = np.array(image)
    converted_image_array = vfunc(image_array)
    return Image.fromarray(converted_image_array)


def get_portal_images(cake=False, flying=False, pellet_hazard=False, bridge=False) -> List[TImage]:
    def load_picture(name: str) -> TImage:
        return convert_image_to_screen(Image.open(
            os.path.join(PICTURE_DICT, name)))

    def bool_to_array_index(boolean: bool) -> int:
        if boolean:
            return 1
        else:
            return 0

    image_cake_names = ["Chamber_icon_cake.gif", "Chamber_icon_cake_on.gif"]
    image_pellet_hazard_names = [
        "Chamber_icon_pellet_hazard.gif", "Chamber_icon_pellet_hazard_on.gif"]
    image_cube_hazard_names = ["Chamber_icon_cube_hazard.gif",
                               "Chamber_icon_cube_hazard_on.gif"]
    image_light_bridge_names = [
        "Chamber_icon_light_bridge.gif", "Chamber_icon_light_bridge_on.gif"]
    image_flying_exit_names = [
        "Chamber_icon_flying_exit.gif", "Chamber_icon_flying_exit_on.gif"]

    image_list = []
    image_list.append(load_picture(
        image_cake_names[bool_to_array_index(cake)]))
    image_list.append(load_picture(
        image_flying_exit_names[bool_to_array_index(flying)]))
    image_list.append(load_picture(
        image_pellet_hazard_names[bool_to_array_index(pellet_hazard)]))
    image_list.append(load_picture(
        image_light_bridge_names[bool_to_array_index(bridge)]))
    return image_list
