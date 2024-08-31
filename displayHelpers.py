import logging
import os
import random
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
    _ ,_, text_width, _ = text_font.getbbox(text)
    canvas.text((point[0] - text_width/2, point[1]),
                text, font=text_font, fill=0)


def get_font_height(font: ImageFont.FreeTypeFont):
    _, _, _, text_height = font.getbbox("A")
    return text_height


def get_font_width(font: ImageFont.FreeTypeFont, text: str):
    _, _, text_width, _ = font.getbbox(text)
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
    
    # Cast the result to uint8 (Image only supports uint8 and this is int64)
    converted_image_array = converted_image_array.astype(np.uint8)
    
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

def draw_black_red_white_text(draw_black, draw_red, text, position, font, black_density, red_density=0.0, white_density=0.0):
    """
    Draw text with epaper black/red color text on a black-and-white image context by controlling the density of black pixels using the existing draw contexts for black and red.
    
    :param draw_black: ImageDraw.Draw object for the image
    :param draw_red: ImageDraw.Draw object for the image
    :param text: Text to be written
    :param position: Tuple (x, y) for text position
    :param font: Font to use
    :param black_density: Fraction of black pixels in the text. It will be normalized to a total of 1 with the other two colors.
    :param red_density: Fraction of red pixels in the text. It will be normalized to a total of 1 with the other two colors.
    :param white_density: Fraction of white pixels in the text. It will be normalized to a total of 1 with the other two colors.

    """
    #Normalize color values
    total_density = black_density + red_density + white_density
    
    black_density = black_density/total_density
    red_density = red_density/total_density
    white_density = white_density/total_density

    # Calculate text size
    _, _, text_width, text_height = font.getbbox(text)

    x, y = position
    
    # Generate an image with the text
    # Create a blank image for the text
    text_image = Image.new('L', (text_width, text_height), 255)  # White background
    #Generate the context for writing the text
    text_draw = ImageDraw.Draw(text_image)
    ##Write the text
    text_draw.text((0, 0), text, font=font, fill=1) 

    # Convert the text image to a NumPy array for manipulation
    text_array = np.array(text_image)

    # Iterate over the array and test each point. If pass will write a point to the main context
    for j in range(text_height):
        for i in range(text_width):
            if text_array[j, i] == 1:  # If the pixel is part of the text
                #The test is for the color density of the letters.
                #A random number is generated and if is above the threshold no point will be written
                random_value = random.random()
                if random_value < black_density:
                    # Draw a black point if the random value is below the black density 
                    draw_black.point((x + i, y + j), fill=1)
                elif random_value < red_density + black_density:
                    #draw a red point if the value is between the black density and its sum wih the red one
                    draw_red.point((x + i, y + j), fill=1)
                    #Otherwise will stay white

