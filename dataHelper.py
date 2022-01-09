import logging
from datetime import datetime, timezone
from typing import List

from dateutil.tz import tzutc
from icalevents.icalevents import events
from icalevents.icalparser import Event

from settings import *

logger = logging.getLogger('app')


def sort_by_date(e: Event):
    return e.start.astimezone()


def get_events(max_number: int) -> List[Event]:
    logger.info("Retrieving calendar infos")
    event_list = events(WEBDAV_URL, fix_apple=WEBDAV_IS_APPLE)
    event_list.sort(key=sort_by_date)
    logger.info(
        "Got {} calendar-entries (capped to {})".format(len(event_list), max_number))

    return event_list[:max_number]


def check_for_birthday(events: List[Event]) -> bool:
    birthday_present = False
    for event in events:
        if "Geburtstag" in event.description:
            birthday_present = True
            return birthday_present
