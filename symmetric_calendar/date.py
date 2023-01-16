#!/usr/bin/python3

__all__ = ('SymmetricDate')

import time as _time
import math
import datetime as _datetime
import locale

#
# For compatibility with Python’s original date and datetime,
# MAXYEAR has to be 1 year less, because:
#
# 9_999-12-35 SYMMETRIC → 10_000-01-02 GREGORIAN
# 9_999-12-34 SYMMETRIC → 10_000-01-01 GREGORIAN
#
# 9_998-12-28 SYMMETRIC → 9_998-12-27 GREGORIAN → 3_651_690 ORDINAL
#
MINYEAR = 1
MAXYEAR = 9_998
MAXORDINAL = 3_651_690

EPOCH = 1
CYCLE_MEAN_YEAR = 365 + (71 / 293)

#
# 1970-01-04 SYMMETRIC → 1970-01-01 GREGORIAN → 719_163
#
POSIX_EPOCH = 719_163

#
# -1 is just a placeholder, so we don’t need to worry about month number 0
#
DAYS_IN_MONTH = [-1, 28, 35, 28, 28, 35, 28, 28, 35, 28, 28, 35, 28]
DAYS_BEFORE_MONTH = [-1]

days_before_month = 0

for days_in_month in DAYS_IN_MONTH[1:]:
    DAYS_BEFORE_MONTH.append(days_before_month)
    days_before_month += days_in_month

del days_before_month, days_in_month

def _is_leap(year):
    "year -> 7 if leap year, else 0."
    return 7 if (((year * 52) + 146) % 293) < 52 else 0


def _days_before_year(year):
    "year -> number of days before January 1st of year."
    year -= 1
    return (364 * year) + (7 * math.floor(((52 * year) + 146) / 293))


def _days_in_month(year, month):
    "year, month -> number of days in that month in that year."
    assert 1 <= month <= 12, month

    if month == 12 and _is_leap(year):
        return 35

    return DAYS_IN_MONTH[month]


def _days_before_month(year, month):
    "year, month -> number of days in year preceding first day of month."
    assert 1 <= month <= 12, 'month must be in 1..12'

    return DAYS_BEFORE_MONTH[month]


def _year_month_day_to_ordinal(year, month, day):
    "year, month, day -> ordinal, considering 01-Jan-0001 as day 1."
    assert 1 <= month <= 12, 'month must be in 1..12'

    days_in_month = _days_in_month(year, month)

    assert 1 <= day <= days_in_month, ('day must be in 1..%d' % days_in_month)

    ordinal_date = _days_before_year(year)
    ordinal_date += _days_before_month(year, month)
    ordinal_date += day

    return ordinal_date


def _first_day_year(year):
    return _days_before_year(year) + 1


def _ordinal_to_year(ordinal_date):
    year = ordinal_date - EPOCH
    year /= CYCLE_MEAN_YEAR
    year = math.ceil(year)
    return year


def _ordinal_to_year_month_day(ordinal_date):
    #
    # First, we find the year corresponding to the ordinal date
    #
    year = _ordinal_to_year(ordinal_date)
    first_day_year = _first_day_year(year)

    #
    # We now check if the year is correct
    # The start of the year is either on the year or we must increment the year
    #
    if ordinal_date > first_day_year:
        #
        # Check if the ordinal date informed may be
        # on the leap week of December or the next year
        #
        if ordinal_date - first_day_year >= 364:
            first_day_next_year = _first_day_year(year + 1)

            #
            # If the given ordinal date is after the next year’s first day,
            # then it is on the next year
            #
            if ordinal_date >= first_day_next_year:
                year += 1
                first_day_year = first_day_next_year

    #
    # The year estimate is too far in the future, go back 1 year
    #
    elif first_day_year > ordinal_date:
        year -= 1
        first_day_year = _first_day_year(year)

    day_in_year = ordinal_date - first_day_year + 1
    week_in_year = math.ceil(day_in_year / 7)
    quarter = math.ceil((4 / 53) *  week_in_year)
    day_in_quarter = day_in_year - (91 * (quarter - 1))
    week_in_quarter = math.ceil(day_in_quarter / 7)
    month_in_quarter = math.ceil((2 / 9) * week_in_quarter)
    month = (3 * (quarter - 1)) + month_in_quarter

    #
    # The day is in the leap week
    #
    if month == 13:
        month = 12

    day = day_in_year - _days_before_month(year, month)

    return year, month, day, day_in_year, week_in_year


def _check_date_fields(year, month, day):
    if not MINYEAR <= year <= MAXYEAR:
        raise ValueError('Year must be in %d..%d' % (MINYEAR, MAXYEAR), year)

    if not 1 <= month <= 12:
        raise ValueError('Month must be in 1..12', month)

    days_in_month = _days_in_month(year, month)

    if not 1 <= day <= days_in_month:
        raise ValueError('Day must be in 1..%d' % days_in_month, day)

    return year, month, day


class SymmetricDate():
    __slots__ = '_year', '_month', '_day', '_hashcode', '_gregorian_date', '_holocene', '_is_leap'

    def __new__(cls, year, month=None, day=None):
        """Constructor.

        Arguments:

        year, month, day (required, base 1)
        """
        if month is None:
            if type(year) == _datetime.date:
                return cls.fromordinal(year.toordinal())

            elif type(year) == str:
                year, month, day = year.split('-')
                year = int(year)
                month = int(month)
                day = int(day)

        _check_date_fields(year, month, day)

        if year > MAXYEAR:
            year -= MAXYEAR + 1
            holocene = True
        else:
            holocene = False

        self = object.__new__(cls)
        self._year = year
        self._month = month
        self._day = day
        self._hashcode = -1
        self._gregorian_date = _datetime.date.fromordinal(self.toordinal())
        self._holocene = holocene
        self._is_leap = _is_leap(year)
        return self

    # Additional constructors

    @classmethod
    def fromtimestamp(cls, t):
        "Construct a date from a POSIX timestamp (like time.time())."
        y, m, d, hh, mm, ss, weekday, jday, dst = _time.localtime(t)
        x = _datetime.date(y, m, d)
        return cls.fromordinal(x.toordinal())

    @classmethod
    def today(cls):
        "Construct a date from time.time()."
        t = _time.time()
        return cls.fromtimestamp(t)

    @classmethod
    def fromordinal(cls, n):
        y, m, d, diy, wiy = _ordinal_to_year_month_day(n)
        return cls(y, m, d)

    @classmethod
    def fromisoformat(cls, date_string):
        return cls.fromordinal(_datetime.date.fromisoformat(date_string).toordinal())

    @classmethod
    def fromisocalendar(cls, year, week, day):
        return cls.fromordinal(_datetime.date.fromisocalendar(year, week, day).toordinal())

    def __repr__(self):
        return f'{self.__class__.__qualname__}({self.year}, {self.month}, {self.day})'

    # XXX These shouldn't depend on time.localtime(), because that
    # clips the usable dates to [1970 .. 2038).  At least ctime() is
    # easily done without using strftime() -- that's better too because
    # strftime("%c", ...) is locale specific.

    def ctime(self):
        return self._gregorian_date.ctime()

    def _strftime_locale(self, format='%a'):
        if format == '%a' or format == '%A':
            weekday_names = {
                0: (locale.ABDAY_2, locale.DAY_2),
                1: (locale.ABDAY_3, locale.DAY_3),
                2: (locale.ABDAY_4, locale.DAY_4),
                3: (locale.ABDAY_5, locale.DAY_5),
                4: (locale.ABDAY_6, locale.DAY_6),
                5: (locale.ABDAY_7, locale.DAY_7),
                6: (locale.ABDAY_1, locale.DAY_1),
            }

            weekday = self.weekday()

            if format == '%a':
                return locale.nl_langinfo(weekday_names[self.weekday()][0])
            else:
                return locale.nl_langinfo(weekday_names[self.weekday()][1])

        elif format == '%b' or format == '%B':
            month_names = {
                1: (locale.ABMON_1, locale.MON_1),
                2: (locale.ABMON_2, locale.MON_2),
                3: (locale.ABMON_3, locale.MON_3),
                4: (locale.ABMON_4, locale.MON_4),
                5: (locale.ABMON_5, locale.MON_5),
                6: (locale.ABMON_6, locale.MON_6),
                7: (locale.ABMON_7, locale.MON_7),
                8: (locale.ABMON_8, locale.MON_8),
                9: (locale.ABMON_9, locale.MON_9),
                10: (locale.ABMON_10, locale.MON_10),
                11: (locale.ABMON_11, locale.MON_11),
                12: (locale.ABMON_12, locale.MON_12),
            }

            if format == '%b':
                return locale.nl_langinfo(month_names[self._month][0])
            else:
                return locale.nl_langinfo(month_names[self._month][1])

    def _strftime_day_in_year(self):
        y, m, d, diy, wiy = _ordinal_to_year_month_day(self.toordinal())
        return str(diy)

    def _strftime_week_in_year(self):
        y, m, d, diy, wiy = _ordinal_to_year_month_day(self.toordinal())
        return str(wiy)

    def _strftime_weekday_number(self):
        return str(self.weekday() + 1)

    def _strftime_ordinal_suffix(self):
        used_locale = locale.getlocale()[0]

        if 'pt_' in used_locale:
            if self.day != 1:
                return ''

            if used_locale == 'pt_BR':
                return 'º'
            else:
                return '.º'

        if self.day == 1:
            return 'st'
        elif self.day == 2:
            return 'nd'
        elif self.day == 3:
            return 'rd'
        else:
            return 'th'

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

        return self._gregorian_date.strftime(fmt)

    def __format__(self, fmt):
        if not isinstance(fmt, str):
            raise TypeError("must be str, not %s" % type(fmt).__name__)
        if len(fmt) != 0:
            return self.strftime(fmt)
        return str(self)

    def isoformat(self):
        return f'{str(self.year).zfill(4)}-{str(self.month).zfill(2)}-{str(self.day).zfill(2)}'

    __str__ = isoformat

    # Read-only field accessors
    @property
    def year(self):
        """year (1-9999)"""
        if self._holocene:
            return self._year + 10_000

        return self._year

    @property
    def month(self):
        """month (1-12)"""
        return self._month

    @property
    def day(self):
        """day (1-31)"""
        return self._day

    @property
    def is_leap(self):
        return bool(self._is_leap)

    @property
    def gregorian_date(self):
        return self._gregorian_date

    @property
    def gregorian_year(self):
        return self._gregorian_date.year

    @property
    def gregorian_month(self):
        return self._gregorian_date.month

    @property
    def gregorian_day(self):
        return self._gregorian_date.day

    # Standard conversions, __eq__, __le__, __lt__, __ge__, __gt__,
    # __hash__ (and helpers)

    def timetuple(self):
        return self._gregorian_date.timetuple()

    def toordinal(self):
        return _year_month_day_to_ordinal(self._year, self._month, self._day)

    def replace(self, year=None, month=None, day=None):
        """Return a new date with new values for the specified fields."""
        if year is None:
            year = self._year
        if month is None:
            month = self._month
        if day is None:
            day = self._day
        return type(self)(year, month, day)

    # Comparisons of date objects with other.

    def __eq__(self, other):
        if type(other) in (_datetime.date, SymmetricDate):
            return self._cmp(other) == 0
        return NotImplemented

    def __le__(self, other):
        if type(other) in (_datetime.date, SymmetricDate):
            return self._cmp(other) <= 0
        return NotImplemented

    def __lt__(self, other):
        if type(other) in (_datetime.date, SymmetricDate):
            return self._cmp(other) < 0
        return NotImplemented

    def __ge__(self, other):
        if type(other) in (_datetime.date, SymmetricDate):
            return self._cmp(other) >= 0
        return NotImplemented

    def __gt__(self, other):
        if type(other) in (_datetime.date, SymmetricDate):
            return self._cmp(other) > 0
        return NotImplemented

    def _cmp(self, other):
        assert type(other) in (_datetime.date, SymmetricDate)

        this_ordinal = self.toordinal()
        other_ordinal = other.toordinal()

        if this_ordinal == other_ordinal:
            return 0
        elif this_ordinal > other_ordinal:
            return 1
        else:
            return -1

    def __hash__(self):
        "Hash."
        if self._hashcode == -1:
            self._hashcode = hash(self._getstate())
        return self._hashcode

    # Computations

    def __add__(self, other):
        "Add a date to a timedelta."
        if isinstance(other, timedelta):
            o = self.toordinal() + other.days
            if 0 < o <= MAXORDINAL:
                return type(self).fromordinal(o)
            raise OverflowError("result out of range")
        return NotImplemented

    __radd__ = __add__

    def __sub__(self, other):
        """Subtract two dates, or a date and a timedelta."""
        if isinstance(other, timedelta):
            return self + timedelta(-other.days)
        if isinstance(other, _datetime.date) or isinstance(other, SymmetricDate):
            days1 = self.toordinal()
            days2 = other.toordinal()
            return timedelta(days1 - days2)
        return NotImplemented

    def weekday(self):
        return self._gregorian_date.weekday()

    def isoweekday(self):
        return self._gregorian_date.isoweekday()

    def isocalendar(self):
        return self._gregorian_date.isocalendar()

    # Pickle support.

    def _getstate(self):
        return self._gregorian_date._getstate()

    def __setstate(self, string):
        yhi, ylo, self._month, self._day = string
        self._year = yhi * 256 + ylo

    def __reduce__(self):
        return (self.__class__, self._getstate())


SymmetricDate.min = SymmetricDate(1, 1, 1)
SymmetricDate.max = SymmetricDate(9_998, 12, 28)
SymmetricDate.resolution = _datetime.timedelta(days=1)


if __name__ == '__main__':
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
        locale.setlocale(locale.LC_COLLATE, 'pt_BR.UTF-8')
        documentation_title = '     Datas da Documentação do Calendário'
        holidays_title = '   Feriados e Eventos Históricos do Brasil'
        size = 16
        date_format = '%a. %d-%b-%Y'
        symmetric_separator = 'sim.'
        gregorian_separator = 'greg.'

    except:
        documentation_title = '  Dates from the Symmetry454 Documentation'
        holidays_title = '   Brazilian Holidays and Historical Events'
        size = 15
        date_format = '%Y-%b-%d %a.'
        symmetric_separator = 'sym.'
        gregorian_separator = 'greg.'

    dates = [
        # (-121, 4, 27),
        # (-91, 9, 22),
        ((1, 1, 1), 'First date possible, Python’s date doesn’t deal with years before 1'),
        ((122, 9, 8), 'Building of Hadrian’s Wall (circa)'),
        ((1776, 7, 4), 'Independence Day - USA'),
        ((1867, 7, 1), 'Canadian Confederence - Canada'),
        ((1947, 10, 26), ''),
        ((1970, 1, 4), 'POSIX epoch'),
        ((1995, 8, 11), ''),
        ((2000, 2, 30), ''),
        ((2004, 5, 7), ''),
        ((2004, 12, 33), 'Dr. Irv Bromberg proposed switching calendars on 2005-01-01'),
        ((2020, 2, 25), ''),
        ((2023, 1, 15), 'Day I commited this code to GitHub'),
        ((2222, 2, 6), ''),
        ((3333, 2, 35), ''),
        ((9998, 12, 28), 'Last date compatible with Python’s date, see code'),
    ]

    print()
    print('  http://individual.utoronto.ca/kalendis/Symmetry454-Arithmetic.pdf')
    print()
    print(documentation_title)
    print(' ===========================================')

    for ymd, name in dates:
        sd = SymmetricDate(*ymd)
        print(' ', sd.gregorian_date.strftime(date_format).rjust(size), f'{gregorian_separator} =', sd.strftime(date_format).rjust(size), f'{symmetric_separator}', name)

    print()
    print()
    print(holidays_title)
    print(' ===========================================')

    dates = [
        ((1500, 5, 21), 'Descobrimento do Brasil (22-abr-1500 cal. juliano)'),
        ((1532, 2, 15), 'Fundação de São Vicente (22-jan-1532 cal. juliano)'),
        ((1554, 2, 22), 'Fundação de São Paulo (25-jan-1554 cal. juliano)'),
        ((1792, 4, 20), 'Tiradentes'),
        ((1822, 9, 6), 'Independência'),
        ((1857, 5, 12), 'Dia da Mulher'),
        ((1886, 4, 27), 'Dia do Trabalhador'),
        ((1889, 11, 19), 'Proclamação da República'),
        ((1932, 7, 6), 'Revolução Constitucionalista'),
        ((1968, 1, 1), 'Fraternidade Universal'),
        ((1980, 10, 14), 'Nossa Senhora Aparecida'),
    ]

    for ymd, name in dates:
        sd = SymmetricDate(*ymd)
        print(' ', sd.gregorian_date.strftime(date_format).rjust(size), f'{gregorian_separator} =', sd.strftime(date_format).rjust(size), f'{symmetric_separator}', name)