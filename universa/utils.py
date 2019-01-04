# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import calendar
from datetime import datetime


def ut(date_time):
    return calendar.timegm(date_time.timetuple())


def dt(unix_time):
    return datetime.utcfromtimestamp(float(unix_time))

