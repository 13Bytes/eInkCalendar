import logging
import os
import random
from typing import List, Tuple

from enum import Enum
from enum import auto

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


def get_font_height(font: ImageFont.FreeTypeFont, withDescender: bool = False):
	"""
	Calculate the height of the given font, including or excluding font extenders (ascenders and descenders).

	Parameters:
	-----------
	font : ImageFont.FreeTypeFont
		The font object from which the height is calculated. This should be an instance of `ImageFont.FreeTypeFont`
		(from the Pillow library).
	
	withDescender : bool, optional, default=False
		If True, the height includes the size of the descender. If False, it only will returns the font's ascent.

	Returns:
	--------
	int
		The total height of the font. These values define the distance from the baseline to the top of the highest ascender and if withDescender is True to the bottom of the lowest descender.

	Example:
	--------
	```python
	from PIL import ImageFont
	
	font = ImageFont.truetype("arial.ttf", 40)
	height = get_font_height(font)
	print(f"Font height: {height} pixels")
	```
	
	This will output the combined ascent and descent of the given font.

	"""
	font_ascent, font_descent = font.getmetrics()
	if withDescender:
		# _, _, _, bottom = font.getbbox("A")  # Potential future enhancement for more accurate extenders handling
		return font_ascent + abs(font_descent)
	else:
		return font_ascent

def get_font_width(font: ImageFont.FreeTypeFont, text: str):
	_, _, right, _ = font.getbbox(text)
	return right


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

def draw_black_red_white_text(draw_blk, draw_red, text, position, font, black_density, red_density=0.0, white_density=0.0):
	"""
	Draw text with epaper black/red color text on a black-and-white image context by controlling the density of black pixels using the existing draw contexts for black and red.
	
	:param draw_blk: ImageDraw.Draw object for the image
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
	text_image = Image.new('L', (text_width, text_height), 255)	 # White background
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
					draw_blk.point((x + i, y + j), fill=1)
				elif random_value < red_density + black_density:
					#draw a red point if the value is between the black density and its sum wih the red one
					draw_red.point((x + i, y + j), fill=1)
					#Otherwise will stay white
class Pattern(Enum):
	BLACK = auto()
	RED = auto()
	VERTICALSTRIPES = auto()
	HORIZONTALSTRIPES = auto()
	DIAGONALSTRIPESLOWERRIGHT = auto()
	DIAGONALSTRIPESUPPERRIGHT = auto()
#import random	
def draw_pattern(
		pattern: Pattern,
		draw_blk: ImageDraw.Draw,
		draw_red: ImageDraw.Draw,
		corner1: (int, int),
		corner2: (int, int),
		use_red: bool = False
	) -> None:
	"""
	Draws a specified pattern within a rectangle defined by two corner points.

	The pattern can be solid black, solid red, or various striped patterns (vertical, horizontal, diagonal).
	Striped patterns can be black and white, or black and red depending on the use_red flag.

	Parameters:
	-----------
	pattern : Pattern
		The pattern to draw. Must be one of the defined Pattern Enum values.
	draw_blk : ImageDraw.Draw
		The drawing context for black color. Typically obtained from PIL.ImageDraw.Draw for the black image.
	draw_red : ImageDraw.Draw
		The drawing context for red color. Typically obtained from PIL.ImageDraw.Draw for the red image.
	corner1 : (int, int)
		The (x, y) coordinates of one corner of the rectangle.
	corner2 : (int, int)
		The (x, y) coordinates of the opposite corner of the rectangle.
	use_red : bool, optional
		If True, red color will be used in the striped patterns instead of white.
		Default is False (black and white stripes).

	Returns:
	--------
	None
	"""
	line_width = 1	# The width of the lines in the patterns

	# Determine the min and max x coordinates
	extremes_x = int(corner1[0]), int(corner2[0])
	x_min = min(extremes_x)
	x_max = max(extremes_x)

	# Determine the min and max y coordinates
	extremes_y = int(corner1[1]), int(corner2[1])
	y_min = min(extremes_y)
	y_max = max(extremes_y)

	# Calculate the width and height of the rectangle
	width = x_max - x_min
	height = y_max - y_min

	#Use for testing
	#pattern=random.choice(list(Pattern))
	#use_red=random.choice([True, False])

	# Draw the pattern based on the specified type
	match pattern:
		case Pattern.BLACK:
			# Fill the rectangle with solid black
			draw_blk.rectangle([corner1, corner2], fill=1)

		case Pattern.RED:
			# Fill the rectangle with solid red
			draw_red.rectangle([corner1, corner2], fill=1)

		case Pattern.VERTICALSTRIPES:
			# Draw vertical stripes within the rectangle
			for x in range(x_min, x_max, line_width):
				line = [(x, y_min), (x, y_max)]

				if ((x - x_min) % (line_width*3)) == 0:
					# Draw black stripe
					draw_blk.line(line, width=line_width*2, fill=1)
				elif use_red and ((x - x_min) % (line_width*3)) > line_width*2-1:
					# Draw red stripe if use_red is True
					draw_red.line(line, width=line_width, fill=1)

		case Pattern.HORIZONTALSTRIPES:
			# Draw horizontal stripes within the rectangle
			for y in range(y_min, y_max, line_width):
				line = [(x_min, y), (x_max, y)]

				if ((y - y_min) % (line_width * 3)) == 0:
					# Draw black stripe
					draw_blk.line(line, width=line_width*2, fill=1)
				elif use_red and ((y - y_min) % (line_width * 3)) > line_width*2-1:
					# Draw red stripe if use_red is True
					draw_red.line(line, width=line_width, fill=1)

		case Pattern.DIAGONALSTRIPESLOWERRIGHT:
			# Draw diagonal stripes from lower left to upper right (sloping downwards to the right)
			line_width = 2
			##Correct a optical artifact for the diagonals
			x_max = x_max-1
			width = width-1
			
			# First set of lines starting from x-axis increments
			for delta_x in range(0, width, line_width):
				x = x_min + delta_x

				line = [
					(x, y_min),
					(min(x_max, x + height), min(y_min + (x_max - x), y_max))
				]

				if (delta_x % (line_width * 2)) == 0:
					# Draw black stripe
					draw_blk.line(line, width=line_width, fill=1)
				elif use_red:
					# Draw red stripe (with thinner line width)
					draw_red.line(line, width=round(line_width / 2), fill=1)
					# The red lines are thinner to account for the extra pixels in a diagonal.

			# Second set of lines starting from y-axis increments
			for delta_y in range(0, height, line_width):
				y = y_min + delta_y
				
				line = [
					(x_min, y),
					(min(x_max, x_min + (y_max - y)), min(y_max, y + width))
				]

				if (delta_y % (line_width * 2)) == 0:
					# Draw black stripe
					draw_blk.line(line, width=line_width, fill=1)
				elif use_red:
					# Draw red stripe
					draw_red.line(line, width=round(line_width / 2), fill=1)

		case Pattern.DIAGONALSTRIPESUPPERRIGHT:
			# Draw diagonal stripes from upper left to lower right (sloping upwards to the right)
			line_width = 2
			##Correct a optical artifact for the diagonals
			x_min = x_min+1
			width = width-1
				
			# First set of lines starting from y-axis decrements
			for delta_y in range(0, height, line_width):
				y = y_max - delta_y
				
				line = [
					(x_min, y),
					(min(x_max, x_min + (y - y_min)), max(y_min, y - width))
				]

				if (delta_y % (line_width * 2)) == 0:
					# Draw black stripe
					draw_blk.line(line, width=line_width, fill=1)
				elif use_red:
					# Draw red stripe
					draw_red.line(line, width=round(line_width / 2), fill=1)

			# Second set of lines starting from x-axis increments
			for delta_x in range(0, width, line_width):
				x = x_min + delta_x

				line = [
					(x, y_max),
					(min(x_max, x + height), max(y_max - (x_max - x), y_min))
				]

				if (delta_x % (line_width * 2)) == 0:
					# Draw black stripe
					draw_blk.line(line, width=line_width, fill=1)
				elif use_red:
					# Draw red stripe
					draw_red.line(line, width=round(line_width / 2), fill=1)

		case _:
			# Default case: fill the rectangle with solid black
			draw_blk.rectangle([corner1, corner2], fill=1)