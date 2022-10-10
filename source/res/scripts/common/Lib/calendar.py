# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/calendar.py
import sys
import datetime
import locale as _locale
__all__ = ['IllegalMonthError',
 'IllegalWeekdayError',
 'setfirstweekday',
 'firstweekday',
 'isleap',
 'leapdays',
 'weekday',
 'monthrange',
 'monthcalendar',
 'prmonth',
 'month',
 'prcal',
 'calendar',
 'timegm',
 'month_name',
 'month_abbr',
 'day_name',
 'day_abbr']
error = ValueError

class IllegalMonthError(ValueError):

    def __init__(self, month):
        self.month = month

    def __str__(self):
        return 'bad month number %r; must be 1-12' % self.month


class IllegalWeekdayError(ValueError):

    def __init__(self, weekday):
        self.weekday = weekday

    def __str__(self):
        return 'bad weekday number %r; must be 0 (Monday) to 6 (Sunday)' % self.weekday


January = 1
February = 2
mdays = [0,
 31,
 28,
 31,
 30,
 31,
 30,
 31,
 31,
 30,
 31,
 30,
 31]

class _localized_month:
    _months = [ datetime.date(2001, i + 1, 1).strftime for i in range(12) ]
    _months.insert(0, lambda x: '')

    def __init__(self, format):
        self.format = format

    def __getitem__(self, i):
        funcs = self._months[i]
        if isinstance(i, slice):
            return [ f(self.format) for f in funcs ]
        else:
            return funcs(self.format)

    def __len__(self):
        pass


class _localized_day:
    _days = [ datetime.date(2001, 1, i + 1).strftime for i in range(7) ]

    def __init__(self, format):
        self.format = format

    def __getitem__(self, i):
        funcs = self._days[i]
        if isinstance(i, slice):
            return [ f(self.format) for f in funcs ]
        else:
            return funcs(self.format)

    def __len__(self):
        pass


day_name = _localized_day('%A')
day_abbr = _localized_day('%a')
month_name = _localized_month('%B')
month_abbr = _localized_month('%b')
MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY = range(7)

def isleap(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def leapdays(y1, y2):
    y1 -= 1
    y2 -= 1
    return y2 // 4 - y1 // 4 - (y2 // 100 - y1 // 100) + (y2 // 400 - y1 // 400)


def weekday(year, month, day):
    return datetime.date(year, month, day).weekday()


def monthrange(year, month):
    if not 1 <= month <= 12:
        raise IllegalMonthError(month)
    day1 = weekday(year, month, 1)
    ndays = mdays[month] + (month == February and isleap(year))
    return (day1, ndays)


class Calendar(object):

    def __init__(self, firstweekday=0):
        self.firstweekday = firstweekday

    def getfirstweekday(self):
        return self._firstweekday % 7

    def setfirstweekday(self, firstweekday):
        self._firstweekday = firstweekday

    firstweekday = property(getfirstweekday, setfirstweekday)

    def iterweekdays(self):
        for i in range(self.firstweekday, self.firstweekday + 7):
            yield i % 7

    def itermonthdates(self, year, month):
        date = datetime.date(year, month, 1)
        days = (date.weekday() - self.firstweekday) % 7
        date -= datetime.timedelta(days=days)
        oneday = datetime.timedelta(days=1)
        while True:
            yield date
            try:
                date += oneday
            except OverflowError:
                break

            if date.month != month and date.weekday() == self.firstweekday:
                break

    def itermonthdays2(self, year, month):
        for i, d in enumerate(self.itermonthdays(year, month), self.firstweekday):
            yield (d, i % 7)

    def itermonthdays(self, year, month):
        day1, ndays = monthrange(year, month)
        days_before = (day1 - self.firstweekday) % 7
        for _ in range(days_before):
            yield 0

        for d in range(1, ndays + 1):
            yield d

        days_after = (self.firstweekday - day1 - ndays) % 7
        for _ in range(days_after):
            yield 0

    def monthdatescalendar(self, year, month):
        dates = list(self.itermonthdates(year, month))
        return [ dates[i:i + 7] for i in range(0, len(dates), 7) ]

    def monthdays2calendar(self, year, month):
        days = list(self.itermonthdays2(year, month))
        return [ days[i:i + 7] for i in range(0, len(days), 7) ]

    def monthdayscalendar(self, year, month):
        days = list(self.itermonthdays(year, month))
        return [ days[i:i + 7] for i in range(0, len(days), 7) ]

    def yeardatescalendar(self, year, width=3):
        months = [ self.monthdatescalendar(year, i) for i in range(January, January + 12) ]
        return [ months[i:i + width] for i in range(0, len(months), width) ]

    def yeardays2calendar(self, year, width=3):
        months = [ self.monthdays2calendar(year, i) for i in range(January, January + 12) ]
        return [ months[i:i + width] for i in range(0, len(months), width) ]

    def yeardayscalendar(self, year, width=3):
        months = [ self.monthdayscalendar(year, i) for i in range(January, January + 12) ]
        return [ months[i:i + width] for i in range(0, len(months), width) ]


class TextCalendar(Calendar):

    def prweek(self, theweek, width):
        print self.formatweek(theweek, width),

    def formatday(self, day, weekday, width):
        if day == 0:
            s = ''
        else:
            s = '%2i' % day
        return s.center(width)

    def formatweek(self, theweek, width):
        return ' '.join((self.formatday(d, wd, width) for d, wd in theweek))

    def formatweekday(self, day, width):
        if width >= 9:
            names = day_name
        else:
            names = day_abbr
        return names[day][:width].center(width)

    def formatweekheader(self, width):
        return ' '.join((self.formatweekday(i, width) for i in self.iterweekdays()))

    def formatmonthname(self, theyear, themonth, width, withyear=True):
        s = month_name[themonth]
        if withyear:
            s = '%s %r' % (s, theyear)
        return s.center(width)

    def prmonth(self, theyear, themonth, w=0, l=0):
        print self.formatmonth(theyear, themonth, w, l),

    def formatmonth(self, theyear, themonth, w=0, l=0):
        w = max(2, w)
        l = max(1, l)
        s = self.formatmonthname(theyear, themonth, 7 * (w + 1) - 1)
        s = s.rstrip()
        s += '\n' * l
        s += self.formatweekheader(w).rstrip()
        s += '\n' * l
        for week in self.monthdays2calendar(theyear, themonth):
            s += self.formatweek(week, w).rstrip()
            s += '\n' * l

        return s

    def formatyear(self, theyear, w=2, l=1, c=6, m=3):
        w = max(2, w)
        l = max(1, l)
        c = max(2, c)
        colwidth = (w + 1) * 7 - 1
        v = []
        a = v.append
        a(repr(theyear).center(colwidth * m + c * (m - 1)).rstrip())
        a('\n' * l)
        header = self.formatweekheader(w)
        for i, row in enumerate(self.yeardays2calendar(theyear, m)):
            months = range(m * i + 1, min(m * (i + 1) + 1, 13))
            a('\n' * l)
            names = (self.formatmonthname(theyear, k, colwidth, False) for k in months)
            a(formatstring(names, colwidth, c).rstrip())
            a('\n' * l)
            headers = (header for k in months)
            a(formatstring(headers, colwidth, c).rstrip())
            a('\n' * l)
            height = max((len(cal) for cal in row))
            for j in range(height):
                weeks = []
                for cal in row:
                    if j >= len(cal):
                        weeks.append('')
                    weeks.append(self.formatweek(cal[j], w))

                a(formatstring(weeks, colwidth, c).rstrip())
                a('\n' * l)

        return ''.join(v)

    def pryear(self, theyear, w=0, l=0, c=6, m=3):
        print self.formatyear(theyear, w, l, c, m)


class HTMLCalendar(Calendar):
    cssclasses = ['mon',
     'tue',
     'wed',
     'thu',
     'fri',
     'sat',
     'sun']

    def formatday(self, day, weekday):
        if day == 0:
            return '<td class="noday">&nbsp;</td>'
        else:
            return '<td class="%s">%d</td>' % (self.cssclasses[weekday], day)

    def formatweek(self, theweek):
        s = ''.join((self.formatday(d, wd) for d, wd in theweek))
        return '<tr>%s</tr>' % s

    def formatweekday(self, day):
        return '<th class="%s">%s</th>' % (self.cssclasses[day], day_abbr[day])

    def formatweekheader(self):
        s = ''.join((self.formatweekday(i) for i in self.iterweekdays()))
        return '<tr>%s</tr>' % s

    def formatmonthname(self, theyear, themonth, withyear=True):
        if withyear:
            s = '%s %s' % (month_name[themonth], theyear)
        else:
            s = '%s' % month_name[themonth]
        return '<tr><th colspan="7" class="month">%s</th></tr>' % s

    def formatmonth(self, theyear, themonth, withyear=True):
        v = []
        a = v.append
        a('<table border="0" cellpadding="0" cellspacing="0" class="month">')
        a('\n')
        a(self.formatmonthname(theyear, themonth, withyear=withyear))
        a('\n')
        a(self.formatweekheader())
        a('\n')
        for week in self.monthdays2calendar(theyear, themonth):
            a(self.formatweek(week))
            a('\n')

        a('</table>')
        a('\n')
        return ''.join(v)

    def formatyear(self, theyear, width=3):
        v = []
        a = v.append
        width = max(width, 1)
        a('<table border="0" cellpadding="0" cellspacing="0" class="year">')
        a('\n')
        a('<tr><th colspan="%d" class="year">%s</th></tr>' % (width, theyear))
        for i in range(January, January + 12, width):
            months = range(i, min(i + width, 13))
            a('<tr>')
            for m in months:
                a('<td>')
                a(self.formatmonth(theyear, m, withyear=False))
                a('</td>')

            a('</tr>')

        a('</table>')
        return ''.join(v)

    def formatyearpage(self, theyear, width=3, css='calendar.css', encoding=None):
        if encoding is None:
            encoding = sys.getdefaultencoding()
        v = []
        a = v.append
        a('<?xml version="1.0" encoding="%s"?>\n' % encoding)
        a('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n')
        a('<html>\n')
        a('<head>\n')
        a('<meta http-equiv="Content-Type" content="text/html; charset=%s" />\n' % encoding)
        if css is not None:
            a('<link rel="stylesheet" type="text/css" href="%s" />\n' % css)
        a('<title>Calendar for %d</title>\n' % theyear)
        a('</head>\n')
        a('<body>\n')
        a(self.formatyear(theyear, width))
        a('</body>\n')
        a('</html>\n')
        return ''.join(v).encode(encoding, 'xmlcharrefreplace')


class TimeEncoding:

    def __init__(self, locale):
        self.locale = locale

    def __enter__(self):
        self.oldlocale = _locale.getlocale(_locale.LC_TIME)
        _locale.setlocale(_locale.LC_TIME, self.locale)
        return _locale.getlocale(_locale.LC_TIME)[1]

    def __exit__(self, *args):
        _locale.setlocale(_locale.LC_TIME, self.oldlocale)


class LocaleTextCalendar(TextCalendar):

    def __init__(self, firstweekday=0, locale=None):
        TextCalendar.__init__(self, firstweekday)
        if locale is None:
            locale = _locale.getdefaultlocale()
        self.locale = locale
        return

    def formatweekday(self, day, width):
        with TimeEncoding(self.locale) as encoding:
            if width >= 9:
                names = day_name
            else:
                names = day_abbr
            name = names[day]
            if encoding is not None:
                name = name.decode(encoding)
            return name[:width].center(width)
        return

    def formatmonthname(self, theyear, themonth, width, withyear=True):
        with TimeEncoding(self.locale) as encoding:
            s = month_name[themonth]
            if encoding is not None:
                s = s.decode(encoding)
            if withyear:
                s = '%s %r' % (s, theyear)
            return s.center(width)
        return


class LocaleHTMLCalendar(HTMLCalendar):

    def __init__(self, firstweekday=0, locale=None):
        HTMLCalendar.__init__(self, firstweekday)
        if locale is None:
            locale = _locale.getdefaultlocale()
        self.locale = locale
        return

    def formatweekday(self, day):
        with TimeEncoding(self.locale) as encoding:
            s = day_abbr[day]
            if encoding is not None:
                s = s.decode(encoding)
            return '<th class="%s">%s</th>' % (self.cssclasses[day], s)
        return

    def formatmonthname(self, theyear, themonth, withyear=True):
        with TimeEncoding(self.locale) as encoding:
            s = month_name[themonth]
            if encoding is not None:
                s = s.decode(encoding)
            if withyear:
                s = '%s %s' % (s, theyear)
            return '<tr><th colspan="7" class="month">%s</th></tr>' % s
        return


c = TextCalendar()
firstweekday = c.getfirstweekday

def setfirstweekday(firstweekday):
    try:
        firstweekday.__index__
    except AttributeError:
        raise IllegalWeekdayError(firstweekday)

    if not MONDAY <= firstweekday <= SUNDAY:
        raise IllegalWeekdayError(firstweekday)
    c.firstweekday = firstweekday


monthcalendar = c.monthdayscalendar
prweek = c.prweek
week = c.formatweek
weekheader = c.formatweekheader
prmonth = c.prmonth
month = c.formatmonth
calendar = c.formatyear
prcal = c.pryear
_colwidth = 20
_spacing = 6

def format(cols, colwidth=_colwidth, spacing=_spacing):
    print formatstring(cols, colwidth, spacing)


def formatstring(cols, colwidth=_colwidth, spacing=_spacing):
    spacing *= ' '
    return spacing.join((c.center(colwidth) for c in cols))


EPOCH = 1970
_EPOCH_ORD = datetime.date(EPOCH, 1, 1).toordinal()

def timegm(tuple):
    year, month, day, hour, minute, second = tuple[:6]
    days = datetime.date(year, month, 1).toordinal() - _EPOCH_ORD + day - 1
    hours = days * 24 + hour
    minutes = hours * 60 + minute
    seconds = minutes * 60 + second
    return seconds


def main(args):
    import optparse
    parser = optparse.OptionParser(usage='usage: %prog [options] [year [month]]')
    parser.add_option('-w', '--width', dest='width', type='int', default=2, help='width of date column (default 2, text only)')
    parser.add_option('-l', '--lines', dest='lines', type='int', default=1, help='number of lines for each week (default 1, text only)')
    parser.add_option('-s', '--spacing', dest='spacing', type='int', default=6, help='spacing between months (default 6, text only)')
    parser.add_option('-m', '--months', dest='months', type='int', default=3, help='months per row (default 3, text only)')
    parser.add_option('-c', '--css', dest='css', default='calendar.css', help='CSS to use for page (html only)')
    parser.add_option('-L', '--locale', dest='locale', default=None, help='locale to be used from month and weekday names')
    parser.add_option('-e', '--encoding', dest='encoding', default=None, help='Encoding to use for output')
    parser.add_option('-t', '--type', dest='type', default='text', choices=('text', 'html'), help='output type (text or html)')
    options, args = parser.parse_args(args)
    if options.locale and not options.encoding:
        parser.error('if --locale is specified --encoding is required')
        sys.exit(1)
    locale = (options.locale, options.encoding)
    if options.type == 'html':
        if options.locale:
            cal = LocaleHTMLCalendar(locale=locale)
        else:
            cal = HTMLCalendar()
        encoding = options.encoding
        if encoding is None:
            encoding = sys.getdefaultencoding()
        optdict = dict(encoding=encoding, css=options.css)
        if len(args) == 1:
            print cal.formatyearpage(datetime.date.today().year, **optdict)
        elif len(args) == 2:
            print cal.formatyearpage(int(args[1]), **optdict)
        else:
            parser.error('incorrect number of arguments')
            sys.exit(1)
    else:
        if options.locale:
            cal = LocaleTextCalendar(locale=locale)
        else:
            cal = TextCalendar()
        optdict = dict(w=options.width, l=options.lines)
        if len(args) != 3:
            optdict['c'] = options.spacing
            optdict['m'] = options.months
        if len(args) == 1:
            result = cal.formatyear(datetime.date.today().year, **optdict)
        elif len(args) == 2:
            result = cal.formatyear(int(args[1]), **optdict)
        elif len(args) == 3:
            result = cal.formatmonth(int(args[1]), int(args[2]), **optdict)
        else:
            parser.error('incorrect number of arguments')
            sys.exit(1)
        if options.encoding:
            result = result.encode(options.encoding)
        print result
    return


if __name__ == '__main__':
    main(sys.argv)
