#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# SymmetricCalendar - The Symmetry454 Calendar in Python
#
# Copyright (C) 2023–
# Copyright (C) Ari Caldeira <aricaldeira at gmail.com>
#
# Original calendar documentation is Public Domain by it’s author:
# http://individual.utoronto.ca/kalendis/symmetry.htm
#

__all__ = ('SymmetricDateTime')


import datetime as _datetime
import time as _time

from .date import SymmetricDate, POSIX_EPOCH


class SymmetricDateTime(SymmetricDate):
    __slots__ =  '_date', '_time', '_year', '_month', '_day', '_hashcode', '_gregorian_date', '_holocene', '_is_leap', '_hour', '_minute', '_second', '_microsecond', '_tzinfo', '_hashcode', '_fold', '_gregorian_date_time'

    def __new__(cls, year, month=None, day=None, hour=0, minute=0, second=0, microsecond=0, tzinfo=None, *, fold=0):
        if month is None:
            if type(year) in (_datetime.datetime, SymmetricDateTime):
                return cls.fromtimestamp(year.timestamp())

            elif type(year) == str:
                year, month, day = year.split('-')
                day, time = day.split(' ')
                year = int(year)
                month = int(month)
                day = int(day)

                if '.' in time:
                    time, microsecond = time.split('.')
                    microsecond = int(microsecond)

                hour, minute, second = time.split(':')
                hour = int(hour)
                minute = int(minute)
                second = int(second)

        self = object.__new__(cls)
        self._date = SymmetricDate(year, month, day)
        self._year = self._date.year
        self._month = self._date.month
        self._day = self._date.day
        self._hashcode = -1
        self._gregorian_date = self._date.gregorian_date
        self._holocene = self._date._holocene
        self._is_leap = self._date.is_leap

        self._time = _datetime.time(hour, minute, second, microsecond, tzinfo, fold=fold)
        self._hour = self._time.hour
        self._minute = self._time.minute
        self._second = self._time.second
        self._microsecond = self._time.microsecond
        self._tzinfo = self._time.tzinfo
        self._fold = self._time.fold

        self._gregorian_date_time = _datetime.datetime.combine(self._gregorian_date, self._time)
        return self

    @property
    def hour(self):
        return self._hour

    @property
    def minute(self):
        return self._minute

    @property
    def second(self):
        return self._second

    @property
    def microsecond(self):
        return self._microsecond

    @property
    def tzinfo(self):
        return self._tzinfo

    @property
    def fold(self):
        return self._fold

    @property
    def date(self):
        return self._date

    @property
    def time(self):
        return self._time

    def isoformat(self, sep='T', timespec='auto'):
        return self._date.isoformat() + sep + self._time.isoformat(timespec)

    def __repr__(self):
        """Convert to formal string, for repr()."""
        L = [self._year, self._month, self._day,  # These are never zero
             self._hour, self._minute, self._second, self._microsecond]

        if L[-1] == 0:
            del L[-1]

        if L[-1] == 0:
            del L[-1]

        s = f'{self.__class__.__qualname__}{tuple(L)}'

        if self._tzinfo is not None:
            assert s[-1:] == ")"
            s = s[:-1] + ", tzinfo=%r" % self._tzinfo + ")"

        if self._fold:
            assert s[-1:] == ")"
            s = s[:-1] + ", fold=1)"

        return s

    def __str__(self):
        "Convert to string, for str()."
        return self.isoformat(sep=' ')

    def timestamp(self):
        dt = _datetime.datetime.combine(self._date.gregorian_date, self._time, self._tzinfo)
        return dt.timestamp()

    @classmethod
    def fromtimestamp(cls, timestamp, tzinfo=None):
        dt = _datetime.datetime.fromtimestamp(timestamp, tzinfo)
        date = SymmetricDate(dt.date())
        return cls(date.year, date.month, date.day, dt.hour, dt.minute, dt.second, dt.microsecond, dt.tzinfo, fold=dt.fold)

    def strftime(self, fmt):
        #
        # Deals with what is or may be different from the Gregorian Calendar
        #
        fmt = fmt.replace('%%', '__PERCENT__')

        if '%a' in fmt:
            fmt = fmt.replace('%a', self._strftime_locale('%a'))

        if '%A' in fmt:
            fmt = fmt.replace('%A', self._strftime_locale('%A'))

        if '%d' in fmt:
            fmt = fmt.replace('%d', str(self.day).zfill(2))

        if '%-d' in fmt:
            fmt = fmt.replace('%-d', str(self.day))

        if '%o' in fmt:
            fmt = fmt.replace('%o', self._strftime_ordinal_suffix())

        if '%m' in fmt:
            fmt = fmt.replace('%m', str(self.month).zfill(2))

        if '%-m' in fmt:
            fmt = fmt.replace('%-m', str(self.month))

        if '%b' in fmt:
            fmt = fmt.replace('%b', self._strftime_locale('%b'))

        if '%B' in fmt:
            fmt = fmt.replace('%B', self._strftime_locale('%B'))

        if '%y' in fmt:
            fmt = fmt.replace('%y', str(self.year))

        if '%Y' in fmt:
            fmt = fmt.replace('%Y', str(self.year))

        if '%j' in fmt:
            fmt = fmt.replace('%j', self._strftime_day_in_year().zfill(3))

        if '%-j' in fmt:
            fmt = fmt.replace('%j', self._strftime_day_in_year())

        if '%w' in fmt:
            fmt = fmt.replace('%w', self._strftime_weekday_number())

        if '%U' in fmt:
            fmt = fmt.replace('%U', self._strftime_week_in_year().zfill(2))

        if '%-U' in fmt:
            fmt = fmt.replace('%U', self._strftime_week_in_year())

        if '%W' in fmt:
            fmt = fmt.replace('%W', self._strftime_week_in_year().zfill(2))

        if '%-W' in fmt:
            fmt = fmt.replace('%W', self._strftime_week_in_year())

        if '%c' in fmt:
            fmt = fmt.replace('%c', self.strftime(locale.nl_langinfo(locale.D_T_FMT)))

        if '%x' in fmt:
            fmt = fmt.replace('%x', self.strftime(locale.nl_langinfo(locale.D_FMT)))

        if '%X' in fmt:
            fmt = fmt.replace('%X', self.strftime(locale.nl_langinfo(locale.T_FMT)))

        fmt = fmt.replace('__PERCENT__', '%%')

        return self._gregorian_date_time.strftime(fmt)

    @classmethod
    def now(cls, tzinfo=None):
        return cls.fromtimestamp(_time.time(), tzinfo)

    @classmethod
    def combine(cls, date: SymmetricDate | _datetime.date | str, time: _datetime.time, tzinfo=True):
        if type(date) != SymmetricDate:
            date = SymmetricDate(date)

        if tzinfo is True:
            tzinfo = time.tzinfo

        return cls(date.year, date.month, date.day, time.hour, time.minute, time.second, time.microsecond, tzinfo, fold=time.fold)

    def __eq__(self, other):
        if type(other) in (_datetime.datetime, SymmetricDateTime):
            return self._cmp(other) == 0
        return NotImplemented

    def __le__(self, other):
        if type(other) in (_datetime.datetime, SymmetricDateTime):
            return self._cmp(other) <= 0
        return NotImplemented

    def __lt__(self, other):
        if type(other) in (_datetime.datetime, SymmetricDateTime):
            return self._cmp(other) < 0
        return NotImplemented

    def __ge__(self, other):
        if type(other) in (_datetime.datetime, SymmetricDateTime):
            return self._cmp(other) >= 0
        return NotImplemented

    def __gt__(self, other):
        if type(other) in (_datetime.datetime, SymmetricDateTime):
            return self._cmp(other) > 0
        return NotImplemented

    def _cmp(self, other):
        assert type(other) in (_datetime.datetime, SymmetricDateTime)

        this_timestamp = self.timestamp()
        other_timestamp = other.timestamp()

        if this_timestamp == other_timestamp:
            return 0
        elif this_timestamp > other_timestamp:
            return 1
        else:
            return -1

