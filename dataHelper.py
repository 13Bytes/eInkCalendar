import logging
import time
from datetime import datetime, timezone
from typing import List
from urllib.parse import urlparse

import requests
import vobject
from dateutil import tz
from icalevents.icalevents import events
from icalevents.icalparser import Event
from lxml import etree
from requests.auth import HTTPBasicAuth

from settings import *

logger = logging.getLogger('app')


def sort_by_date(e: Event):
	return e.start.astimezone()


def get_events(max_number: int) -> List[Event]:
	logger.info("Retrieving calendar infos")
	utc_timezone = tz.tzutc()
	current_timezone = tz.tzlocal()
	
	#Current date used to filter events
	current_UTC_date = datetime.now(timezone.utc)

	#Will store all the events
	event_list = []
	
	#Get all the events of the provided calendars, after the current date
	for calendar_settings in WEBDAV_CALENDAR_URLS:
		try:
			calendar_events_list = events(
				url=calendar_settings["url"], 
				start=current_UTC_date, 
				fix_apple=calendar_settings["is_apple"]
			)
		except Exception as e:
			logger.critical(e)
			continue
		
		for event in calendar_events_list:
			#Add a property called "calendar_name" to the event with the calendar name
			#Will be used to identify the owner of the event  
			setattr(event, "calendar_name", calendar_settings["calendar_name"])
			#Will add two attributes for the calendar so it can be drawn with different patterns
			#If they are not available will fill a default value
			try:
				setattr(event, "pattern_fill", calendar_settings["pattern_fill"])
			except:
				setattr(event, "pattern_fill", "BLACK")
			try:
				setattr(event, "pattern_red_stripes", calendar_settings["pattern_red_stripes"])
			except:
				setattr(event, "pattern_red_stripes", False)


		
		#Filter out the events that are before the current time (icalevents only filter by day and not hour and minute)
		calendar_events_list = [event for event in calendar_events_list if event.end.astimezone(timezone.utc) >= current_UTC_date]
		#Add the new events to the list
		event_list = event_list + calendar_events_list
			
	#Sort the list by date
	event_list.sort(key=sort_by_date)

	logger.info("Got {} calendar-entries (capped to {})".format(
		len(event_list), max_number))
	return event_list[0:max_number]



def get_birthdays() -> List[str]:
	logger.info("Retrieving contact (birthday) infos")
	try:
		auth = HTTPBasicAuth(CALDAV_CONTACT_USER, CALDAV_CONTACT_PWD)
		baseurl = urlparse(CALDAV_CONTACT_URL).scheme + \
			'://' + urlparse(CALDAV_CONTACT_URL).netloc

		r = requests.request('PROPFIND', CALDAV_CONTACT_URL, auth=auth, headers={
			'content-type': 'text/xml', 'Depth': '1'})
		if r.status_code != 207:
			raise RuntimeError('error in response from %s: %r' %
							   (CALDAV_CONTACT_URL, r))

		vcardUrlList = []
		root = etree.XML(r.text.encode())
		for link in root.xpath('./d:response/d:propstat/d:prop/d:getcontenttype[starts-with(.,"text/vcard")]/../../../d:href', namespaces={"d": "DAV:"}):
			vcardUrlList.append(baseurl + link.text)

		today = datetime.today()
		birthday_names: List[str] = []
		for vurl in vcardUrlList:
			r = requests.request("GET", vurl, auth=auth)
			vcard = vobject.readOne(r.text)
			if 'bday' in vcard.contents.keys():
				birthday = vcard.contents['bday'][0]
				try:
					birthday_date = datetime.strptime(
						birthday.value, "%Y-%m-%d")
				except ValueError:
					# necessary, because multipe formats are used...
					birthday_date = datetime.strptime(birthday.value, "%Y%m%d")

				if (birthday_date.day == today.day) and (birthday_date.month == today.month):
					name = vcard.contents['fn'][0].value
					birthday_names.append(name)
		return birthday_names
	except Exception as e:
		logger.critical(e)
		return []
