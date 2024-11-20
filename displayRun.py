#!/usr/bin/python3
import calendar
import locale
import logging
import os
import random
import sys
import time
from datetime import datetime
import zoneinfo

from enum import Enum

import calendar

from holidays import country_holidays

import schedule

import re

import requests

from PIL import Image, ImageDraw, ImageFont, ImageOps
from PIL.Image import Image as TImage
from PIL.ImageDraw import ImageDraw as TImageDraw

import lib.epd7in5b_V2 as eInk
from dataHelper import get_events, get_birthdays

from displayHelpers import *
from settings import *

#For reading battery levels from the I2C bus (will assume that witty pi is on address 0x08 address)
from smbus2 import SMBus


#Get the conversion from the weather codes to emoji symbols
from weatherCodesEmoji import *

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

WEATHER_FONT = ImageFont.truetype(
	os.path.join(FONT_DICT, 'DejaVuSans-Bold.ttf'), 20)
#To display the glyphs for the state of the weather
WEATHER_EMOJI_FONT = ImageFont.truetype(
	os.path.join(FONT_DICT, 'NotoEmoji-Regular.ttf'), 20)	
	
	
#The calendar will occupy the same height of the Title Date font, and will have 7 rows.
#So the size of the font should be at maximum 7 times less (the calendar has 7 rows.)
#To make sure that there's some space between rows, for the ascenders and descenders and for the size between columns it be half of that.
calendar_number_font_size = int(round(title_date_font_size/(7*2)))

CALENDAR_NUMBER_FONT = ImageFont.truetype(
	os.path.join(FONT_DICT, 'DejaVuSansMono.ttf'), calendar_number_font_size)
	
CALENDAR_NUMBER_TODAY_FONT = ImageFont.truetype(
	os.path.join(FONT_DICT, 'DejaVuSansMono-Bold.ttf'), calendar_number_font_size)
	
#Font for the days numbers of the other months
CALENDAR_NUMBER_SECONDARY_FONT = ImageFont.truetype(
	os.path.join(FONT_DICT, 'DejaVuSansMono.ttf'), int(round(calendar_number_font_size/4*3)))
#Font for the calendar header
CALENDAR_HEADER_FONT = ImageFont.truetype(
	os.path.join(FONT_DICT, 'DejaVuSansMono-Bold.ttf'), calendar_number_font_size)
		
		
EVENT_TIME_FONT = ImageFont.truetype(
	os.path.join(FONT_DICT, 'DejaVuSansMono.ttf'), 20)
EVENT_TIME_SECONDARY_FONT = ImageFont.truetype(
	os.path.join(FONT_DICT, 'DejaVuSansMono.ttf'), 16)
	
EVENT_NAME_FONT = ImageFont.truetype(
	os.path.join(FONT_DICT, 'DejaVuSans.ttf'), 22)
EVENT_CALENDAR_FONT = ImageFont.truetype(
	os.path.join(FONT_DICT, 'DejaVuSans-Bold.ttf'), 18)
	
FOOTNOTE_FONT = ImageFont.truetype(
	os.path.join(FONT_DICT, 'DejaVuSans.ttf'), 8)
	
LINE_WIDTH = 3
CALENDAR_LINE_WIDTH = 10


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
	draw_blk.fontmode = "1"
	draw_red.fontmode = "1"

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

	#Get the country code from the locale
	try:
		country_code = re.split(r'[_\.]', LOCALE)[1]
	except:
		country_code = ""
	#Get the holidays
	locale_holidays = country_holidays(country_code, years = year_number)
	
	date_now = datetime(year_number, month_number, day_number).date()
	#Test if today is a holiday
	is_holiday = date_now in locale_holidays
	
	# draw_text_centered(str(day_number), (width/2, 0), draw_blk, FONT_ROBOTO_H1)

	
	vertical_margin = height/20
	
	current_height = vertical_margin
	
	#First Line
	draw_blk.line((PADDING_L, current_height, width, current_height),
				  fill=1, width=LINE_WIDTH)
	#Weather
	
	#Check the temperature units settings
	global TEMPERATURE_UNIT
	if 'TEMPERATURE_UNIT' not in globals():
		TEMPERATURE_UNIT = "C"
	elif TEMPERATURE_UNIT.upper() not in ['C', 'F']:
		TEMPERATURE_UNIT = "C"

	try:

		unit_system = "imperial" if TEMPERATURE_UNIT.upper() == "F" else "metric" 


		url = f"https://api.tomorrow.io/v4/timelines?apikey={TOMORROWIO_API_KEY}"

		payload = {
		    "location": WEATHER_LOCATION,
		    "fields": ["temperatureMax", "temperatureMin", "weatherCodeDay", "weatherCodeNight", "weatherCode", "temperatureMinTime", "temperatureMaxTime", "sunriseTime", "sunsetTime"],
		    "units": unit_system,
		    "timesteps": ["1d"],
		    "startTime": "now",
		    "endTime": "nowPlus1d"
		}
		headers = {
		    "accept": "application/json",
		    "Accept-Encoding": "gzip",
		    "content-type": "application/json"
		}



	except:
		url = None
		logger.info("Weather tomorrowIO location or API Key not set")
	
	tomorrowIO_response = None
	wait_for_new_request = False
	
	if url != None:	
		#Will make a request for weather data.
		#If there's an error will make it again after 10 minutes
		try:
			tomorrowIO_response = requests.post(url, json=payload, headers=headers)
		except:
			tomorrowIO_response = None
			wait_for_new_request = True
		
		if 	tomorrowIO_response != None:
			try:
				tomorrowIO_response.raise_for_status()
			except Exception as err:
				wait_for_new_request = True
				
				if tomorrowIO_response.status_code == 400:
					logger.error(f"The URL seems to be malformed. Check the wether parameters on settings - {err}")
				else:
					logger.warning(f"Could not make a connection to weather server: {err}. Will try again in 10 minutes.")
					
					
		if wait_for_new_request:			
			#If there was an error try again 10 minutes later
			time.sleep(600)
			
			#try again a request
			try:
				tomorrowIO_response = requests.post(url, json=payload, headers=headers)
			except:
				tomorrowIO_response = None
			
			#Check the response
			if 	tomorrowIO_response != None:
				try:
					tomorrowIO_response.raise_for_status()
				except requests.exceptions.HTTPError as err:
				# Handle specific HTTP error responses (non-200)
					print(f"HTTP error occurred: {err}")
				except Exception as err:
				# Handle other errors (e.g., network errors)
					print(f"Other error occurred: {err}")
	
	
	if tomorrowIO_response != None and tomorrowIO_response.status_code == 200:
		tomorrowIO_response_json = tomorrowIO_response.json()
		# Get the location
		#responselocation = tomorrowIO_response_json["location"]
		logger.info(f"Retrieved weather data for {WEATHER_LOCATION}.")
		
		#Get the current weather
		weather_data_by_interval = tomorrowIO_response_json["data"]["timelines"][0]["intervals"]
		
		
		# Get the current time in the local timezone
		local_timezone = zoneinfo.ZoneInfo("localtime")
		now = datetime.now(local_timezone)

		#Get an dict of results with a tuple were the key is the datetime of the forecast
		max_temp_date = { datetime.fromisoformat(interval["values"]["temperatureMaxTime"]): interval["values"]["temperatureMax"] for interval in weather_data_by_interval}
		min_temp_date = { datetime.fromisoformat(interval["values"]["temperatureMinTime"]): interval["values"]["temperatureMin"] for interval in weather_data_by_interval}
		
		
		#Select the max temperature
		#It will be the one closest with the current time on the current day or after.

		#If there more that 1 value will test for the ones of the current day or after
		if len(max_temp_date) > 1:
			#Current day at midnight
			midnight_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
			max_temp_date_filtered = [time for time in max_temp_date if time > midnight_today]
		
			#Will get the datetime of the value closest to now
			max_closest_time = min(max_temp_date_filtered, key=lambda date: abs(now - date))
		
			#Will define the maximum temperature
			max_temp = max_temp_date[max_closest_time]
		else:
			max_temp = max_temp_date.values()[0]
			
			
		#Select the min temperature
		#It will be the one closest with the current time.
		# I think is the best way to have a meaningfull value
		min_closest_time = min(min_temp_date.keys(), key=lambda date: abs(now - date))
		min_temp = min_temp_date[min_closest_time]
		
		
		#Get the next sunset and sunrise
		sunrises_times = [datetime.fromisoformat(interval["values"]["sunriseTime"]) for interval in weather_data_by_interval]
		sunsets_times =  [datetime.fromisoformat(interval["values"]["sunsetTime"]) for interval in weather_data_by_interval]

		next_sunrise = min([sunrise for sunrise in sunrises_times if sunrise >= now])
		next_sunset = min([sunset for sunset in sunsets_times if sunset >= now])

		#Get the day/night status
		is_night = next_sunrise < next_sunset
		
		#WeatherCodeDay
		#Test if the current time is at night (between sunset and sunrise). If the sunrise is before the next predition use the current weathercodeDay prediction. Otherwise use the next one.
		#This is only to not show a prediction fior a period in the past (if the next prediction is before the new day the current weather code for the day time is for yestarday)
		if is_night and len(weather_data_by_interval)>1 and next_sunrise > datetime.fromisoformat(weather_data_by_interval[1]["startTime"]):
			weatherCodeDay = weather_data_by_interval[1]["values"]["weatherCodeDay"]
		else:
			weatherCodeDay = weather_data_by_interval[0]["values"]["weatherCodeDay"]
			
			
		#WeatherCodeNight
		#Test if the current time is at day (between sunrise and sunset). If the sunset is before the next predition use the current weathercodeNight prediction. Otherwise use the next one.
		if not is_night and len(weather_data_by_interval)>1 and next_sunset > datetime.fromisoformat(weather_data_by_interval[1]["startTime"]):
			weatherCodeNight = weather_data_by_interval[1]["values"]["weatherCodeNight"]
		else:
			weatherCodeNight = weather_data_by_interval[0]["values"]["weatherCodeNight"]
		
		
		
	
			
		try:	
			current_height += get_font_height(WEATHER_FONT) + PADDING_TOP
			
			weather_box_leading_x = PADDING_L
			weather_box_trailling_x = width - PADDING_R
			weather_box_top_y = current_height - get_font_height(WEATHER_FONT)
			weather_box_bottom_y = current_height 
			
			draw_blk.line((PADDING_L, current_height, width, current_height),
						  fill=1, width=LINE_WIDTH)
			#Text will be white or red in a black background
			
			#background
			draw_blk.rectangle([(weather_box_leading_x, vertical_margin), (width, weather_box_bottom_y)], fill=1)
			
			
			#Text
			#Will draw something like ont the bar: |↥🌤️⛈️ ↧☀️ ↧-1ºC ↥5ºC| or |☀️ ↧-1ºC ↥5ºC| if the weather is similar during the day

			#Temperature
			#It will be draw from right to left.
			display_celsius = TEMPERATURE_UNIT.upper() != "F"
			
			temp_symbol = "℃" if display_celsius else "℉"
			
			high_temp_string = str(round(max_temp))
			high_temp = high_temp_string+temp_symbol # "28℃"
			high_temp_symbol = "↑"
			
			low_temp_string = str(round(min_temp))
			low_temp = low_temp_string+temp_symbol
			low_temp_symbol = "↓"
			
			draw_blk.text((weather_box_trailling_x, weather_box_bottom_y), high_temp, font=WEATHER_FONT, anchor="rd",  fill=0)
			
			high_temp_width = get_font_width(WEATHER_FONT, high_temp_symbol+high_temp)
			
			draw_blk.text((weather_box_trailling_x-high_temp_width, weather_box_bottom_y), high_temp_symbol, font=WEATHER_FONT, anchor="ld",  fill=0)
			
			high_temp_symbol_space_width = get_font_width(WEATHER_FONT, " " + high_temp_symbol + high_temp)
			
			low_temp_string = low_temp_symbol+low_temp
			
			draw_blk.text((weather_box_trailling_x-high_temp_symbol_space_width, weather_box_bottom_y), low_temp_symbol+low_temp, font=WEATHER_FONT, anchor="rd",  fill=0)
			
			
			#weather



			weather_leading_space =  weather_box_leading_x + PADDING_R #PADDING_R to give a padding equal to the right side
			
			#If both weather codes are equal...
			if weatherCodeDay//10 == weatherCodeNight//10:
				#...Only draw one of them 
				all_weather_emojis = wheater_codes_emojis[weatherCodeNight//10]
				
				draw_blk.text((weather_leading_space, weather_box_bottom_y), all_weather_emojis, font=WEATHER_EMOJI_FONT, anchor="ld",  fill=0)
			
			else:
				#Otherwise draws both of them with an arrow pointing up or down with each of them
				#Day weather
				day_weather_emojis = wheater_codes_emojis[weatherCodeDay]

				#Night weather
				night_weather_emojis = wheater_codes_emojis[weatherCodeNight]


				#Draw the low weather state
				draw_blk.text((weather_leading_space, weather_box_bottom_y), day_weather_emojis, font=WEATHER_EMOJI_FONT, anchor="ld",  fill=0)
				
				#Get the width of the string of the day weather state
				day_weather_string_width = get_font_width(WEATHER_EMOJI_FONT, day_weather_emojis+" ")
	
				#Get the padding for the high weather state symbol
				night_weather_padding = weather_leading_space + day_weather_string_width

				
				#Draw the night symbol
				draw_blk.text((night_weather_padding, weather_box_bottom_y), night_weather_emojis, font=WEATHER_EMOJI_FONT, anchor="ld",  fill=0)
							

		except Exception as err:
			# Handle other errors (e.g., network errors)
			print(f"Error occurred: {err}")


	
	
				  
	# Heading

	draw_blk.text((PADDING_L, current_height), month_str.upper(),
				  font=FONT_ROBOTO_H2, fill=1)

	#Weather
	#Bounds
	#weather_box_leading_x = PADDING_L+(width - PADDING_L - PADDING_R)/2
	#weather_box_trailling_x = width - PADDING_R
	#weather_box_top_y = current_height
	#weather_box_bottom_y = current_height + get_font_height(WEATHER_FONT)
#
	##draw_red.rectangle([(weather_box_leading_x, weather_box_top_y), (weather_box_trailling_x, weather_box_bottom_y)], outline=1, width= 1)
	#draw_blk.multiline_text((weather_box_trailling_x, weather_box_top_y), "↥28℃ 18h\n↧12℃ 04h", font=WEATHER_FONT, anchor="ra", align="right", fill=1)

	#Moves the height down
	current_height += get_font_height(FONT_ROBOTO_H2)

	# Day Number Title
	current_font_height = get_font_height(TITLE_DATE)
	
	#Write weekends days in red
	title_date_origin_y = current_height - current_font_height/10
	
	
	if is_weekend or is_holiday:
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
	
	#Radius for the circle of the today day. The radius will be half the row or column size, whatever the lesser. 
	#Will be a bit bigger if the number has two digits (bigger so to evolve better the number but more little so it doesnt go abve the header if in the first row)
	today_circle_radius = min(line_height_max, day_width) / 2 + (1 if day_number >= 10 else 0)
	
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
	
		# In the first row draws the header with the week days name
		if row_number == 1:
			for index, header_day_number in enumerate(month_calendar.iterweekdays()):
			
				#Day name first letter in caps
				day_name = calendar.day_abbr[header_day_number]
				day_name_header = day_name[0].upper()
				day_name_coordinate = (line_test_leading_x+index*day_width+day_width_padding, row_height)
				
				#Coordinates for the rectangle/background color
				header_x_leading = line_test_leading_x+index*day_width
				header_y_top = row_height - line_height_max/2
				
				header_x_trailing = line_test_leading_x+index*day_width+day_width
				header_y_bottom = row_height + line_height_max/2
				
				#Will draw the rectangle in red if in a weekend. Otherwise in black
				if header_day_number >= 5:
					draw_red.rectangle([(header_x_leading, header_y_top), (header_x_trailing, header_y_bottom)], fill=1)
					
					#Draw the first letter of the weekday in the background color	
					draw_red.text(day_name_coordinate, day_name_header, font=CALENDAR_HEADER_FONT, anchor="mm", fill=0) 
							  
				else:
					draw_blk.rectangle([(header_x_leading, header_y_top), (header_x_trailing, header_y_bottom)], fill=1)
					
					#Draw the first letter of the weekday in the background color	
					draw_blk.text(day_name_coordinate, day_name_header, font=CALENDAR_HEADER_FONT, anchor="mm", fill=0)
							  
									
							  
		elif number_of_weeks > row_number-2:
			#If there is a days on the month to display in this row will retrieve and draw them
			#Iterate the number columns
			for day in range(0,7):
				day_data = days_of_month[row_number-2][day]
				cal_day_number = day_data.day
				cal_day_number_string = str(cal_day_number).replace("0", "O")
				cal_month_number = day_data.month
				#The week day
				cal_day_weekday = day_data.weekday()


				center_day_coord = (line_test_leading_x+day*day_width+day_width_padding, row_height)
				
				
				if cal_day_number == day_number and cal_month_number == month_number:
					#Draw a circle on the current day. The radius will be half the row or column size, whatever the lesser
					#Will be red on the weekends or holidays
					if cal_day_weekday >= 5 or day_data in locale_holidays:
						draw_red.circle(center_day_coord, today_circle_radius, fill=1)
						draw_red.text(center_day_coord, cal_day_number_string, font=CALENDAR_NUMBER_TODAY_FONT, anchor="mm", fill=0, features=["-zero"])
					else:
						draw_blk.circle(center_day_coord, today_circle_radius, fill=1)
						draw_blk.text(center_day_coord, cal_day_number_string, font=CALENDAR_NUMBER_TODAY_FONT, anchor="mm", fill=0, features=["-zero"])
					
				else:
					cal_font = CALENDAR_NUMBER_FONT if cal_month_number == month_number else CALENDAR_NUMBER_SECONDARY_FONT

					#If the weekday is saturday or sunday or a holiday will paint it red
					if cal_day_weekday >= 5 or day_data in locale_holidays:
						draw_red.text(center_day_coord, cal_day_number_string, font=cal_font, anchor="mm", fill=1, features=["-zero"])
					else:
						draw_blk.text(center_day_coord, cal_day_number_string, font=cal_font, anchor="mm", fill=1, features=["-zero"])

	
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
		

				  
	# schedule
	
	#Font Heights
	event_calendar_font_height = get_font_height(EVENT_CALENDAR_FONT)
	event_name_font_height = get_font_height(EVENT_NAME_FONT, withDescender = True)
	
	#Line height
	line_height = event_name_font_height * 1.0

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


	#New line
	current_height += line_height
	
	#current calendar for drawing id lines
	event_to_draw = None
	current_event_height_start = None

	#Size of the event font descender to correct the calendars vertical lines.	
	event_font_ascent , event_font_descent = EVENT_NAME_FONT.getmetrics()
	
	#Vertical padding to separate each vertical line identifying a calendar 
	event_line_vertical_padding = 2
	
	#Start the loop to write each event
	for event in event_list:
	
	#Calendar Lines
	#Draw the lines that identify areas with same calendar.
	#Note: As the text is aligned by its baseline all the vertical points have to be shifted dow by the size of the descending of the fon
		if current_event_height_start == None:
			event_to_draw = event
			current_event_height_start = current_height - event_name_font_height + event_font_descent + event_line_vertical_padding
			
		elif (event.calendar_name != event_to_draw.calendar_name or last_event_day != event.start.date()) and event_to_draw != None:
			current_event_height_stop = current_height - line_height + event_font_descent - event_line_vertical_padding

			#draw_blk.rectangle([(PADDING_L-CALENDAR_LINE_WIDTH-column_spacing, current_event_height_start), (PADDING_L-column_spacing, current_event_height_stop)], fill=1)
			draw_pattern(
				Pattern[event_to_draw.pattern_fill],
				draw_blk, 
				draw_red, 
				(PADDING_L-CALENDAR_LINE_WIDTH-column_spacing, current_event_height_start), 
				(PADDING_L-column_spacing, current_event_height_stop),
				use_red = event_to_draw.pattern_red_stripes,
			)
			
			event_to_draw = event
			current_event_height_start = current_height - event_name_font_height + event_font_descent + event_line_vertical_padding
	
		#Stops the for cycle if the new line will be outside the bounds or is day name/number after it is outside the bounds
		#Use 1.5 times the line size to do a bit of padding.
		if current_height + line_height * 0.5 > calendar_end_height or (last_event_day != event.start.date() and current_height + line_height * 1.5 > calendar_end_height):
			#Finish drawing the calendar line
			
			#get the height of the last line
			current_event_height_stop = current_height + event_font_descent - line_height - event_line_vertical_padding
			
			#if this height is superior of the stored line start height it will draw the line
			#Otherwise a new line was to be started and was to be drawn
			if current_event_height_stop >= current_event_height_start:
				draw_pattern(
					Pattern[event_to_draw.pattern_fill],
					draw_blk, 
					draw_red, 
					(PADDING_L-CALENDAR_LINE_WIDTH-column_spacing, current_event_height_start), 
					(PADDING_L-column_spacing, current_event_height_stop),
					use_red = event_to_draw.pattern_red_stripes,
				)
			#Stops writting more calendar events
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
			
			#Resets the vertical line placement
			event_to_draw = event
			current_event_height_start = current_height - event_name_font_height + event_font_descent

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
		#If there is only one clanedar he will not be displayed and there will more space
		calendar_name_space = column_spacing + calendar_names_width[event.calendar_name] if len(calendar_names) > 1 else 0
		available_space = width - (PADDING_L + summmary_padding + calendar_name_space + PADDING_R)
		
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
		
		if len(calendar_names) > 1:
		#Calendar Name (padded to the right and using a fitted name defined above to make sure that won't occupies more space that available, as defined by max_calendar_name_width)
		#Will only be shown if there is more than one calendar
			draw_blk.text((PADDING_R_COORDINATE, current_height), calendar_names_fitted[event.calendar_name],
						font=EVENT_CALENDAR_FONT, anchor="rs", fill=1)	 

		#Next line location
		current_height += line_height


	#Draw the last line of the calendar
	current_height = calendar_end_height
	draw_blk.line((PADDING_L, current_height, width, current_height),
				  fill=1, width=LINE_WIDTH)
	

	#Only show Aperture Images if the user wants 
	if APERTURE_DECORATIONS:
		current_height += PADDING_TOP
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
	

	#Footnote with data
	#Will print current date and hour for update reference 
	now = datetime.now()
	draw_blk.text((PADDING_R_COORDINATE, height), now.strftime('%x')+" "+now.strftime('%X'),
						font=FOOTNOTE_FONT, anchor="rd", fill=1)	 
						
	#BATTERY LEVELS
	#Will show a red empty battery for charging when the battery is more empty 
	bus = SMBus(1)
	# 1 Integer part for input voltage, 2 Decimal part (multiple 100 times) for input voltage
	battery_voltage = float(bus.read_byte_data(8, 1) + bus.read_byte_data(8, 2)/100)
	#7 Power mode:  Power via LDO regulator = 1, Input 5V via USB Type C = 0
	is_charging = bus.read_byte_data(8, 7) == 0
	bus.close()
	
	try:
		should_recharge = battery_voltage <= RECHARGE_VOlTAGE
	except:
		should_recharge = false
	
	
	if should_recharge:
		image_bat = Image.open(os.path.join(PICTURE_DICT, "battery-icon-1_3.bmp"))
		
		_, height = image_bat.size
		image_vertical_padding = abs(round((vertical_margin-height)/2))
		image_red.paste(image_bat, (PADDING_L, image_vertical_padding))
		image_bat.close()
		
	#A more compreensive battery status icons
	# 	
# 	print_bat_red = False
# 	if is_charging:
# 	# print a charging icon
# 		bat_file = "battery-icon-charging.bmp"
# 	elif should_recharge:
# 	# Print a low charge icon in red
# 		bat_file = "battery-icon-1_3.bmp"
# 		print_bat_red = True
# 	else:
# 	# Batt full
# 		bat_file = "battery-icon-3_3.bmp"
# 						  
# 	#Battery charge:
# 	#Only show a low bat indicator when in battery and its depleted.
# 	#Get for the registers 1 and 2
# 	image_bat = Image.open(os.path.join(PICTURE_DICT, bat_file))
# 
# 	_, height = image_bat.size
# 	image_vertical_padding = abs(round((vertical_margin-height)/2))
# 	
# 	if print_bat_red:
# 		image_red.paste(image_bat, (PADDING_L, image_vertical_padding))
# 	else:
# 		image_blk.paste(image_bat, (PADDING_L, image_vertical_padding))
# 	
# 	image_bat.close()


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
