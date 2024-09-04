#!/usr/bin/python3
import calendar
import locale
import logging
import os
import random
import sys
import time
from datetime import datetime
import calendar

import schedule

from PIL import Image, ImageDraw, ImageFont, ImageOps
from PIL.Image import Image as TImage
from PIL.ImageDraw import ImageDraw as TImageDraw

import lib.epd7in5b_V2 as eInk
from dataHelper import get_events, get_birthdays
from displayHelpers import *
from settings import *

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"),
					handlers=[logging.FileHandler(filename="info.log", mode='w'),
					logging.StreamHandler()])
logger = logging.getLogger('app')

CURRENT_DICT = os.path.dirname(os.path.realpath(__file__))
PICTURE_DICT = os.path.join(CURRENT_DICT, 'pictures')
FONT_DICT = os.path.join(CURRENT_DICT, 'fonts')


#Define debug if it was not already defined in settings.py
try:
	DEBUG
except NameError:
	DEBUG = False
	
title_date_font_size=200
TITLE_DATE = ImageFont.truetype(
	os.path.join(FONT_DICT, 'DejaVuSans-Bold.ttf'), title_date_font_size)
FONT_ROBOTO_H1 = ImageFont.truetype(
	os.path.join(FONT_DICT, 'DejaVuSans-Bold.ttf'), 40)
FONT_ROBOTO_H2 = ImageFont.truetype(
	os.path.join(FONT_DICT, 'DejaVuSans-Bold.ttf'), 30)
FONT_ROBOTO_P = ImageFont.truetype(
	os.path.join(FONT_DICT, 'DejaVuSans-Bold.ttf'), 20)

#The calendar will occupy the same height of the Title Date font, and will have 7 rows.
#So the size of the font should be at maximum 7 times less (the calendar has 7 rows.)
#To make sure that there's some space between rows, for the ascenders and descenders and for the size between columns it be half of that.
calendar_number_font_size = int(round(title_date_font_size/(7*1.90)))
print("font size:"+str(calendar_number_font_size))
print("1.90font size:"+str(int(round(title_date_font_size/(7*1.90)))))

CALENDAR_NUMBER_FONT = ImageFont.truetype(
	os.path.join(FONT_DICT, 'DejaVuSansCondensed.ttf'), calendar_number_font_size)
#Font for the days numbers of the other months
CALENDAR_NUMBER_SECONDARY_FONT = ImageFont.truetype(
	os.path.join(FONT_DICT, 'DejaVuSansCondensed.ttf'), int(round(calendar_number_font_size/4*3)))
#Font for the calendar header
CALENDAR_HEADER_FONT = ImageFont.truetype(
	os.path.join(FONT_DICT, 'DejaVuSansCondensed-Bold.ttf'), calendar_number_font_size)
		
		
EVENT_TIME_FONT = ImageFont.truetype(
	os.path.join(FONT_DICT, 'DejaVuSansMono.ttf'), 20)
EVENT_TIME_SECONDARY_FONT = ImageFont.truetype(
	os.path.join(FONT_DICT, 'DejaVuSansMono.ttf'), 16)
	
EVENT_NAME_FONT = ImageFont.truetype(
	os.path.join(FONT_DICT, 'DejaVuSans.ttf'), 22)
EVENT_CALENDAR_FONT = ImageFont.truetype(
	os.path.join(FONT_DICT, 'DejaVuSans-Bold.ttf'), 18)
LINE_WIDTH = 3


def main():
	logger.info(datetime.now())
	try:
		epd = eInk.EPD()

		if DEBUG:
			logger.info("DEBUG-Mode activated...")

		#Use aperture image only if the user wants, otherwize use an image without the logo
		image_blk = Image.open(os.path.join(
			PICTURE_DICT, "blank-aperture.bmp" if APERTURE_DECORATIONS else "blank-hk.bmp"))

		image_red = Image.open(os.path.join(
			PICTURE_DICT, "blank-hk.bmp"))

		draw_blk = ImageDraw.Draw(image_blk)
		draw_red = ImageDraw.Draw(image_red)

		render_content(draw_blk, image_blk, draw_red,
					   image_red, epd.width, epd.height)
		show_content(epd, image_blk, image_red)
		# clear_content(epd)

	except Exception as e:
		logger.warning(e)
		if not DEBUG:
			logger.info("Trying to module_exit()")
			eInk.epdconfig.module_exit()
		raise e


def render_content(draw_blk: TImageDraw, image_blk: TImage,	 draw_red: TImageDraw, image_red: TImage, height: int, width: int):
	locale.setlocale(locale.LC_ALL, LOCALE)

	#Makes sure that antialiasing is disabled in font rendering
	draw_blk.fontmode = "L"
	draw_red.fontmode = "L"

	PADDING_L = int(width/10)
	PADDING_R = PADDING_L/4
	PADDING_R_COORDINATE = width - PADDING_R
	PADDING_TOP = int(height/100)
	now = time.localtime()
	max_days_in_month = calendar.monthrange(now.tm_year, now.tm_mon)[1]
	day_str = time.strftime("%A")
	day_number = now.tm_mday
	wday_number = now.tm_wday
	month_number = now.tm_mon
	year_number = now.tm_year
	is_weekend = wday_number >= 5
	month_str = time.strftime("%B")

	# draw_text_centered(str(day_number), (width/2, 0), draw_blk, FONT_ROBOTO_H1)

	
	vertical_margin = height/20
	# Heading
	current_height = vertical_margin
	
	draw_blk.line((PADDING_L, current_height, width, current_height),
				  fill=1, width=LINE_WIDTH)
	draw_blk.text((PADDING_L, current_height), month_str.upper(),
				  font=FONT_ROBOTO_H2, fill=1)
	current_height += get_font_height(FONT_ROBOTO_H2)

	# Date
	current_font_height = get_font_height(TITLE_DATE)
	
	#Write weekends days in red
	title_date_origin_y = current_height - current_font_height/10
	if is_weekend:
		draw_red.text((PADDING_L, title_date_origin_y),
					  str(day_number), font=TITLE_DATE, fill=1)
	else:
		draw_blk.text((PADDING_L, title_date_origin_y),
					  str(day_number), font=TITLE_DATE, fill=1)
					  
	current_height += current_font_height - (current_font_height/10)


	#Draws the MONTH CALENDAR
	
	#Object of the calendar
	month_calendar = calendar.TextCalendar()
	#Set the first day of the week acording with settings
	try:
		month_calendar.setfirstweekday(calendar.SUNDAY if FIRST_WEEKDAY_IS_SUNDAY else calendar.MONDAY)
	except:
		month_calendar.setfirstweekday(calendar.MONDAY)
	
	#list of lists of each day of each week of the month 
	days_of_month = month_calendar.monthdatescalendar(year_number, month_number)
	number_of_weeks = len(days_of_month)
	#Calculates distances and coordinates
	line_test_leading_x = PADDING_L+2*(width - PADDING_L - PADDING_R)/3
	line_test_trailing_x = PADDING_R_COORDINATE
	
	line_test_bottom_y = current_height
	line_test_top_y = current_height-current_font_height+2*(current_font_height/10)
	
	cal_width = line_test_trailing_x-line_test_leading_x
	day_width = round(cal_width/7)
	#A padding to make the letters/numbers be draw on the center, center align
	day_width_padding = round(day_width/2)
	
	line_height_max = (line_test_bottom_y-line_test_top_y)/7
	
	#The text should be aligned by the font baseline. However it sould appear centered on the screen below the upperedge of the current day number on the right
	#This will aloow the text to be lowered.
	#line_row_baseline_adjustment = get_font_height(CALENDAR_HEADER_FONT)/2
	
	#Month Gridlines
	#Bounds
	#draw_red.rectangle([(line_test_leading_x, line_test_top_y), (line_test_trailing_x, line_test_bottom_y)], outline=1, width= 1)
	##Rows Lines (for 6 weeks, max number of weeks in a month, and the header)
	#
	#
	#for row_number in range (1,7):
	#	row_height = line_test_top_y+row_number*line_height_max
	#	draw_red.line((line_test_leading_x, row_height, line_test_trailing_x, row_height), fill=1, width=1)

	#Iterate the rows
	for row_number in range (1,8):
		#The row heigh will be half way between rows
		row_height = int(round(line_test_top_y+(row_number-0.5)*line_height_max))
	
		#Header
		if row_number == 1:
			for index, day_name in enumerate([calendar.day_abbr[day_number] for day_number in month_calendar.iterweekdays()]):
				draw_blk.text((line_test_leading_x+index*day_width+day_width_padding, row_height),
							  day_name[0].upper(), font=CALENDAR_HEADER_FONT, anchor="mm", fill=1)		
		elif number_of_weeks > row_number-2:
			#If there is a days on the month to display in this row will retrieve and draw them
			#Iterate the number columns
			for day in range(0,7):
				day_data = days_of_month[row_number-2][day]
				cal_day_number = day_data.day
				cal_month_number = day_data.month
				cal_font = CALENDAR_NUMBER_FONT if cal_month_number == month_number else CALENDAR_NUMBER_SECONDARY_FONT
				draw_blk.text((line_test_leading_x+day*day_width+day_width_padding, row_height),
						  	str(cal_day_number), font=cal_font, anchor="mm", fill=1)

	
	# Month-Overview (with day-string)
	current_height += PADDING_TOP
	day_of_month = str(day_number) + "/" + str(max_days_in_month)
	draw_blk.text((PADDING_L, current_height), day_of_month,
				  font=FONT_ROBOTO_P, fill=1)

	draw_blk.text((PADDING_R_COORDINATE, current_height), day_str.upper(),
				  font=FONT_ROBOTO_P, anchor = "ra", fill=1)

	#First line of the calendar
	current_height += get_font_height(FONT_ROBOTO_P) + PADDING_TOP
	

	draw_blk.line((PADDING_L, current_height, width, current_height),
				  fill=1, width=LINE_WIDTH)

	# Month-Tally-Overview
	#Only show if the Aperture decorations are to be shown
	if APERTURE_DECORATIONS:
		current_height += PADDING_TOP
		tally_height = height/40
		tally_width = LINE_WIDTH + width/120  # width + padding
		available_width = width - PADDING_L
		tally_number = int(available_width / tally_width *
						   (day_number / max_days_in_month))
		x_position = PADDING_L + LINE_WIDTH/2
		for i in range(0, tally_number):
			draw_blk.line((x_position, current_height, x_position,
						  current_height + tally_height), fill=1, width=LINE_WIDTH)
			x_position += tally_width
		current_height += tally_height
		
	# Calendar
	
	#Font Heights
	event_calendar_font_height = get_font_height(EVENT_CALENDAR_FONT)
	event_name_font_height = get_font_height(EVENT_NAME_FONT)
	
	#Line height
	line_height = event_name_font_height * 1.5
	
	#Event list Top Vertical padding
	current_height += line_height
	
	
	#Stores the coordinate for later calculate the number of events to get
	calendar_start_height = current_height
	#Last line position of the calendar 
	#If the aperture science is hidden this line will be at the bottom
	calendar_end_height = height*0.73 if APERTURE_DECORATIONS else height-vertical_margin
	
	#Get the max number of event lines. Some of them will be later the days but the excess will be filtered out
	available_events_lines = int((calendar_end_height - calendar_start_height)/line_height)
	#Events
	event_list = get_events(available_events_lines)
	
	#Calendar names
	calendar_names = {event.calendar_name for event in event_list}
	
	#Get the width available to each calendar. Will not be more than 25% of the available area
	max_calendar_name_width = width*0.25
	
	calendar_names_width = {}
	calendar_names_fitted = {}

	#Iterate for each calendar name and checks if will fits in the max_calendar_name_width.
	#If not will trim the last letter until it fits (with an …)
	for calendar_name in calendar_names:
		name_to_test = calendar_name
		text_width = get_font_width(EVENT_CALENDAR_FONT, name_to_test)
		
		while len(name_to_test) > 0 and text_width > max_calendar_name_width:
			name_to_test = name_to_test[:-1]
			text_width = get_font_width(EVENT_CALENDAR_FONT, name_to_test + "…")
				
		calendar_names_fitted[calendar_name] = name_to_test + "…" if calendar_name != name_to_test else name_to_test
		calendar_names_width[calendar_name] = text_width
					
					
	calendar_names_width = {name:min(get_font_width(EVENT_CALENDAR_FONT, name), max_calendar_name_width) for name in calendar_names}
	
	
	last_event_day = datetime.now().date()

	#Distance between the time and the summary	  
	column_spacing = 10
	

	#Size of the times (they are monospaced)
	event_start_time_width = get_font_width(EVENT_TIME_FONT, "00:00")	 
	event_end_time_width = get_font_width(EVENT_TIME_SECONDARY_FONT, "00:00")		
   
	#Calculates the size of the text plus the padding, assuming a monospaced font for the times
	end_date_padding = event_start_time_width + column_spacing/2 + event_end_time_width
	summmary_padding = end_date_padding + column_spacing

	for event in event_list:
	
		#Stops the for cycle if the new line will be outside the bounds or is day name/number after it is outside the bounds
		if current_height + line_height/2 > calendar_end_height or (last_event_day != event.start.date() and current_height + line_height*1.5 > calendar_end_height):
			break
			
			
		# Draw new day
		if last_event_day != event.start.date():
			# current_height += height/40
			last_event_day = event.start.date()
			# day_string = "{} {}".format(last_event_day.day,
			#								last_event_day.strftime("%a"))
			day_string = last_event_day.strftime("%A %-d")#.upper()
			
			##Halftoned day text
			#draw_black_red_white_text(draw_blk, draw_red, text=day_string, position=(PADDING_L, current_height), font=FONT_ROBOTO_P, black_density=0.2, red_density=0.8, white_density=0.0)
			#draw_blk.text((PADDING_L, current_height), day_string, font=FONT_ROBOTO_P, fill=0, stroke_width=1, stroke_fill=1)
			draw_red.text((PADDING_L, current_height), day_string, font=FONT_ROBOTO_P, fill=1, anchor="ls", stroke_width=0, stroke_fill=0)
			#draw_blk.text((PADDING_L, current_height), day_string, font=FONT_ROBOTO_P, fill=1)
			
			#New Line
			current_height += line_height

		# Draw event
		event_text = ""

		#Event Start Date
		if event.all_day:
			draw_blk.text((PADDING_L+event_start_time_width, current_height), "- : -",
						  font=EVENT_TIME_FONT, anchor="rs", fill=1)
		elif event.start.date() < last_event_day:
		#If the date to end is before this date will only show the day, but in red
			draw_red.text((PADDING_L+event_start_time_width, current_height), event.start.strftime("%a%d").replace("0", "O"),
						  font=EVENT_TIME_FONT, anchor="rs",fill=1)
		else:
			draw_blk.text((PADDING_L+event_start_time_width, current_height), event.start.strftime("%H:%M").replace("0", "O"),
						  font=EVENT_TIME_FONT, anchor="rs", fill=1)

		#Event End Date
		if event.all_day:
			draw_blk.text((PADDING_L+end_date_padding, current_height), "- : -",
						  font=EVENT_TIME_SECONDARY_FONT, anchor="rs",fill=1)
		elif event.end.date() > last_event_day:
		#If the date to end is after today will only show the day, but in red
			draw_red.text((PADDING_L+end_date_padding, current_height), event.end.strftime("%a%d").replace("0", "O"),
						  font=EVENT_TIME_SECONDARY_FONT, anchor="rs",fill=1)
		else:
			draw_blk.text((PADDING_L+end_date_padding, current_height), event.end.strftime("%H:%M").replace("0", "O"),
						  font=EVENT_TIME_SECONDARY_FONT, anchor="rs", fill=1)

		#Title
		#Will test if the text fits in the available space. If not wil trim it char by char, appending a ... until it does
		
		#Get the available space
		available_space = width - (PADDING_L + summmary_padding + column_spacing + calendar_names_width[event.calendar_name] + PADDING_R)
		
		#WiLl store the text to display
		trimmed_event_summary = event.summary
		#Will store the width of the text
		trimmed_event_summary_width = get_font_width(EVENT_NAME_FONT, trimmed_event_summary)
		
		#Text if the text is too big (or already empy)
		while len(trimmed_event_summary) > 0 and trimmed_event_summary_width > available_space:
		#If too big will trim it and test it again
			trimmed_event_summary = trimmed_event_summary[:-1]
			trimmed_event_summary_width = get_font_width(EVENT_NAME_FONT, trimmed_event_summary + "…")
			
		#If the text was changed will append a ...
		if trimmed_event_summary != event.summary:
				trimmed_event_summary = trimmed_event_summary + "…"
		
		#Display the adjusted text
		draw_blk.text((PADDING_L + summmary_padding, current_height), trimmed_event_summary,
					  font=EVENT_NAME_FONT, anchor="ls", fill=1)			  
		

		#Calendar Name (padded to the right and using a fitted name defined above to make sure that won't occupies more space that available, as defined by max_calendar_name_width)
		draw_blk.text((PADDING_R_COORDINATE, current_height), calendar_names_fitted[event.calendar_name],
					  font=EVENT_CALENDAR_FONT, anchor="rs", fill=1)   

		#Next line location
		current_height += line_height


	#Draw the last line of the calendar
	current_height = calendar_end_height
	draw_blk.line((PADDING_L, current_height, width, current_height),
				  fill=1, width=LINE_WIDTH)
	current_height += PADDING_TOP

	#Only show Aperture Images if the user wants 
	if APERTURE_DECORATIONS:
		# Portal-Icons
		y = PADDING_L
		bithday_persons = get_birthdays()
		draw_cake = (len(bithday_persons) > 0)
		max_image_height = 0
		for image in get_portal_images(draw_cake, bool(random.getrandbits(1)), bool(random.getrandbits(1)), bool(random.getrandbits(1))):
			image_blk.paste(image, (y, int(current_height)))
			image_width, image_height = image.size
			y += image_width + PADDING_TOP
			max_image_height = image_height if (
				image_height > max_image_height) else max_image_height
		
		current_height += max_image_height + PADDING_TOP
		
		# Draw name of birthday-person
		if draw_cake:
			bithday_person_string = ", ".join(bithday_persons)
			draw_red.text((PADDING_L, int(current_height)), bithday_person_string,
						  font=FONT_ROBOTO_P, fill=1)
			current_height += get_font_height(FONT_ROBOTO_P)
	

def show_content(epd: eInk.EPD, image_blk: TImage, image_red: TImage):
	logger.info("Exporting final images")
	image_blk.save("EXPORT-black.bmp")
	image_red.save("EXPORT-red.bmp")
	if ROTATE_IMAGE:
		image_blk = image_blk.rotate(180)
		image_red = image_red.rotate(180)
	if not DEBUG:
		init_display(epd)
		logger.info("Writing on display")
		epd.display(epd.getbuffer(image_blk), epd.getbuffer(image_red))
		set_sleep(epd)


def clear_content(epd: eInk.EPD):
	if DEBUG:
		logger.warning("Clear has no effect while debugging")
	else:
		init_display(epd)
		clear_display(epd)
		set_sleep(epd)


if __name__ == '__main__':
	main()
