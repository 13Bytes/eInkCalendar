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

    try:
        event_list = events(WEBDAV_CALENDAR_URL, fix_apple=WEBDAV_IS_APPLE)
        event_list.sort(key=sort_by_date)

        start_count = 0
        for event in event_list:
            event.start.replace(tzinfo=utc_timezone)
            event.start = event.start.astimezone(current_timezone)

            # remove events from previous day (problem based on time-zones)
            day_number = time.localtime().tm_mday
            event_date = event.start.date()
            if (day_number == 1 and event_date.month < time.localtime().tm_mon):
                start_count += 1
                max_number += 1
            elif (event_date.day < day_number):
                start_count += 1
                max_number += 1

        logger.info("Got {} calendar-entries (capped to {})".format(
            len(event_list), max_number-start_count))
        return event_list[start_count:max_number]

    except Exception as e:
        logger.critical(e)
        return []


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
