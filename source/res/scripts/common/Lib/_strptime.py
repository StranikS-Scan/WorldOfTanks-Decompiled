# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/_strptime.py
import time
import locale
import calendar
from re import compile as re_compile
from re import IGNORECASE
from re import escape as re_escape
from datetime import date as datetime_date
try:
    from thread import allocate_lock as _thread_allocate_lock
except:
    from dummy_thread import allocate_lock as _thread_allocate_lock

__all__ = []

def _getlang():
    return locale.getlocale(locale.LC_TIME)


class LocaleTime(object):

    def __init__(self):
        self.lang = _getlang()
        self.__calc_weekday()
        self.__calc_month()
        self.__calc_am_pm()
        self.__calc_timezone()
        self.__calc_date_time()
        if _getlang() != self.lang:
            raise ValueError('locale changed during initialization')

    def __pad(self, seq, front):
        seq = list(seq)
        if front:
            seq.insert(0, '')
        else:
            seq.append('')
        return seq

    def __calc_weekday(self):
        a_weekday = [ calendar.day_abbr[i].lower() for i in range(7) ]
        f_weekday = [ calendar.day_name[i].lower() for i in range(7) ]
        self.a_weekday = a_weekday
        self.f_weekday = f_weekday

    def __calc_month(self):
        a_month = [ calendar.month_abbr[i].lower() for i in range(13) ]
        f_month = [ calendar.month_name[i].lower() for i in range(13) ]
        self.a_month = a_month
        self.f_month = f_month

    def __calc_am_pm(self):
        am_pm = []
        for hour in (1, 22):
            time_tuple = time.struct_time((1999,
             3,
             17,
             hour,
             44,
             55,
             2,
             76,
             0))
            am_pm.append(time.strftime('%p', time_tuple).lower())

        self.am_pm = am_pm

    def __calc_date_time(self):
        time_tuple = time.struct_time((1999, 3, 17, 22, 44, 55, 2, 76, 0))
        date_time = [None, None, None]
        date_time[0] = time.strftime('%c', time_tuple).lower()
        date_time[1] = time.strftime('%x', time_tuple).lower()
        date_time[2] = time.strftime('%X', time_tuple).lower()
        replacement_pairs = [('%', '%%'),
         (self.f_weekday[2], '%A'),
         (self.f_month[3], '%B'),
         (self.a_weekday[2], '%a'),
         (self.a_month[3], '%b'),
         (self.am_pm[1], '%p'),
         ('1999', '%Y'),
         ('99', '%y'),
         ('22', '%H'),
         ('44', '%M'),
         ('55', '%S'),
         ('76', '%j'),
         ('17', '%d'),
         ('03', '%m'),
         ('3', '%m'),
         ('2', '%w'),
         ('10', '%I')]
        replacement_pairs.extend([ (tz, '%Z') for tz_values in self.timezone for tz in tz_values ])
        for offset, directive in ((0, '%c'), (1, '%x'), (2, '%X')):
            current_format = date_time[offset]
            for old, new in replacement_pairs:
                if old:
                    current_format = current_format.replace(old, new)

            time_tuple = time.struct_time((1999, 1, 3, 1, 1, 1, 6, 3, 0))
            if '00' in time.strftime(directive, time_tuple):
                U_W = '%W'
            else:
                U_W = '%U'
            date_time[offset] = current_format.replace('11', U_W)

        self.LC_date_time = date_time[0]
        self.LC_date = date_time[1]
        self.LC_time = date_time[2]
        return

    def __calc_timezone(self):
        try:
            time.tzset()
        except AttributeError:
            pass

        no_saving = frozenset(['utc', 'gmt', time.tzname[0].lower()])
        if time.daylight:
            has_saving = frozenset([time.tzname[1].lower()])
        else:
            has_saving = frozenset()
        self.timezone = (no_saving, has_saving)


class TimeRE(dict):

    def __init__(self, locale_time=None):
        if locale_time:
            self.locale_time = locale_time
        else:
            self.locale_time = LocaleTime()
        base = super(TimeRE, self)
        base.__init__({'d': '(?P<d>3[0-1]|[1-2]\\d|0[1-9]|[1-9]| [1-9])',
         'f': '(?P<f>[0-9]{1,6})',
         'H': '(?P<H>2[0-3]|[0-1]\\d|\\d)',
         'I': '(?P<I>1[0-2]|0[1-9]|[1-9])',
         'j': '(?P<j>36[0-6]|3[0-5]\\d|[1-2]\\d\\d|0[1-9]\\d|00[1-9]|[1-9]\\d|0[1-9]|[1-9])',
         'm': '(?P<m>1[0-2]|0[1-9]|[1-9])',
         'M': '(?P<M>[0-5]\\d|\\d)',
         'S': '(?P<S>6[0-1]|[0-5]\\d|\\d)',
         'U': '(?P<U>5[0-3]|[0-4]\\d|\\d)',
         'w': '(?P<w>[0-6])',
         'y': '(?P<y>\\d\\d)',
         'Y': '(?P<Y>\\d\\d\\d\\d)',
         'A': self.__seqToRE(self.locale_time.f_weekday, 'A'),
         'a': self.__seqToRE(self.locale_time.a_weekday, 'a'),
         'B': self.__seqToRE(self.locale_time.f_month[1:], 'B'),
         'b': self.__seqToRE(self.locale_time.a_month[1:], 'b'),
         'p': self.__seqToRE(self.locale_time.am_pm, 'p'),
         'Z': self.__seqToRE((tz for tz_names in self.locale_time.timezone for tz in tz_names), 'Z'),
         '%': '%'})
        base.__setitem__('W', base.__getitem__('U').replace('U', 'W'))
        base.__setitem__('c', self.pattern(self.locale_time.LC_date_time))
        base.__setitem__('x', self.pattern(self.locale_time.LC_date))
        base.__setitem__('X', self.pattern(self.locale_time.LC_time))

    def __seqToRE(self, to_convert, directive):
        to_convert = sorted(to_convert, key=len, reverse=True)
        for value in to_convert:
            if value != '':
                break
        else:
            return ''

        regex = '|'.join((re_escape(stuff) for stuff in to_convert))
        regex = '(?P<%s>%s' % (directive, regex)
        return '%s)' % regex

    def pattern(self, format):
        processed_format = ''
        regex_chars = re_compile('([\\\\.^$*+?\\(\\){}\\[\\]|])')
        format = regex_chars.sub('\\\\\\1', format)
        whitespace_replacement = re_compile('\\s+')
        format = whitespace_replacement.sub('\\s+', format)
        while '%' in format:
            directive_index = format.index('%') + 1
            processed_format = '%s%s%s' % (processed_format, format[:directive_index - 1], self[format[directive_index]])
            format = format[directive_index + 1:]

        return '%s%s' % (processed_format, format)

    def compile(self, format):
        return re_compile(self.pattern(format), IGNORECASE)


_cache_lock = _thread_allocate_lock()
_TimeRE_cache = TimeRE()
_CACHE_MAX_SIZE = 5
_regex_cache = {}

def _calc_julian_from_U_or_W(year, week_of_year, day_of_week, week_starts_Mon):
    first_weekday = datetime_date(year, 1, 1).weekday()
    if not week_starts_Mon:
        first_weekday = (first_weekday + 1) % 7
        day_of_week = (day_of_week + 1) % 7
    week_0_length = (7 - first_weekday) % 7
    if week_of_year == 0:
        return 1 + day_of_week - first_weekday
    else:
        days_to_week = week_0_length + 7 * (week_of_year - 1)
        return 1 + days_to_week + day_of_week


def _strptime(data_string, format='%a %b %d %H:%M:%S %Y'):
    global _TimeRE_cache
    global _regex_cache
    with _cache_lock:
        if _getlang() != _TimeRE_cache.locale_time.lang:
            _TimeRE_cache = TimeRE()
            _regex_cache.clear()
        if len(_regex_cache) > _CACHE_MAX_SIZE:
            _regex_cache.clear()
        locale_time = _TimeRE_cache.locale_time
        format_regex = _regex_cache.get(format)
        if not format_regex:
            try:
                format_regex = _TimeRE_cache.compile(format)
            except KeyError as err:
                bad_directive = err.args[0]
                if bad_directive == '\\':
                    bad_directive = '%'
                del err
                raise ValueError("'%s' is a bad directive in format '%s'" % (bad_directive, format))
            except IndexError:
                raise ValueError("stray %% in format '%s'" % format)

            _regex_cache[format] = format_regex
    found = format_regex.match(data_string)
    if not found:
        raise ValueError('time data %r does not match format %r' % (data_string, format))
    if len(data_string) != found.end():
        raise ValueError('unconverted data remains: %s' % data_string[found.end():])
    year = None
    month = day = 1
    hour = minute = second = fraction = 0
    tz = -1
    week_of_year = -1
    week_of_year_start = -1
    weekday = julian = -1
    found_dict = found.groupdict()
    for group_key in found_dict.iterkeys():
        if group_key == 'y':
            year = int(found_dict['y'])
            if year <= 68:
                year += 2000
            else:
                year += 1900
        if group_key == 'Y':
            year = int(found_dict['Y'])
        if group_key == 'm':
            month = int(found_dict['m'])
        if group_key == 'B':
            month = locale_time.f_month.index(found_dict['B'].lower())
        if group_key == 'b':
            month = locale_time.a_month.index(found_dict['b'].lower())
        if group_key == 'd':
            day = int(found_dict['d'])
        if group_key == 'H':
            hour = int(found_dict['H'])
        if group_key == 'I':
            hour = int(found_dict['I'])
            ampm = found_dict.get('p', '').lower()
            if ampm in ('', locale_time.am_pm[0]):
                if hour == 12:
                    hour = 0
            elif ampm == locale_time.am_pm[1]:
                if hour != 12:
                    hour += 12
        if group_key == 'M':
            minute = int(found_dict['M'])
        if group_key == 'S':
            second = int(found_dict['S'])
        if group_key == 'f':
            s = found_dict['f']
            s += '0' * (6 - len(s))
            fraction = int(s)
        if group_key == 'A':
            weekday = locale_time.f_weekday.index(found_dict['A'].lower())
        if group_key == 'a':
            weekday = locale_time.a_weekday.index(found_dict['a'].lower())
        if group_key == 'w':
            weekday = int(found_dict['w'])
            if weekday == 0:
                weekday = 6
            else:
                weekday -= 1
        if group_key == 'j':
            julian = int(found_dict['j'])
        if group_key in ('U', 'W'):
            week_of_year = int(found_dict[group_key])
            if group_key == 'U':
                week_of_year_start = 6
            else:
                week_of_year_start = 0
        if group_key == 'Z':
            found_zone = found_dict['Z'].lower()
            for value, tz_values in enumerate(locale_time.timezone):
                if found_zone in tz_values:
                    if time.tzname[0] == time.tzname[1] and time.daylight and found_zone not in ('utc', 'gmt'):
                        break
                    else:
                        tz = value
                        break

    leap_year_fix = False
    if year is None and month == 2 and day == 29:
        year = 1904
        leap_year_fix = True
    elif year is None:
        year = 1900
    if julian == -1 and week_of_year != -1 and weekday != -1:
        week_starts_Mon = True if week_of_year_start == 0 else False
        julian = _calc_julian_from_U_or_W(year, week_of_year, weekday, week_starts_Mon)
    if julian == -1:
        julian = datetime_date(year, month, day).toordinal() - datetime_date(year, 1, 1).toordinal() + 1
    else:
        datetime_result = datetime_date.fromordinal(julian - 1 + datetime_date(year, 1, 1).toordinal())
        year = datetime_result.year
        month = datetime_result.month
        day = datetime_result.day
    if weekday == -1:
        weekday = datetime_date(year, month, day).weekday()
    if leap_year_fix:
        year = 1900
    return (time.struct_time((year,
      month,
      day,
      hour,
      minute,
      second,
      weekday,
      julian,
      tz)), fraction)


def _strptime_time(data_string, format='%a %b %d %H:%M:%S %Y'):
    return _strptime(data_string, format)[0]
