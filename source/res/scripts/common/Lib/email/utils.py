# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/email/utils.py
__all__ = ['collapse_rfc2231_value',
 'decode_params',
 'decode_rfc2231',
 'encode_rfc2231',
 'formataddr',
 'formatdate',
 'getaddresses',
 'make_msgid',
 'mktime_tz',
 'parseaddr',
 'parsedate',
 'parsedate_tz',
 'unquote']
import os
import re
import time
import base64
import random
import socket
import urllib
import warnings
from email._parseaddr import quote
from email._parseaddr import AddressList as _AddressList
from email._parseaddr import mktime_tz
from email._parseaddr import parsedate as _parsedate
from email._parseaddr import parsedate_tz as _parsedate_tz
from quopri import decodestring as _qdecode
from email.encoders import _bencode, _qencode
COMMASPACE = ', '
EMPTYSTRING = ''
UEMPTYSTRING = u''
CRLF = '\r\n'
TICK = "'"
specialsre = re.compile('[][\\\\()<>@,:;".]')
escapesre = re.compile('[][\\\\()"]')

def _identity(s):
    return s


def _bdecode(s):
    return s if not s else base64.decodestring(s)


def fix_eols(s):
    s = re.sub('(?<!\\r)\\n', CRLF, s)
    s = re.sub('\\r(?!\\n)', CRLF, s)
    return s


def formataddr(pair):
    name, address = pair
    if name:
        quotes = ''
        if specialsre.search(name):
            quotes = '"'
        name = escapesre.sub('\\\\\\g<0>', name)
        return '%s%s%s <%s>' % (quotes,
         name,
         quotes,
         address)
    return address


def getaddresses(fieldvalues):
    all = COMMASPACE.join(fieldvalues)
    a = _AddressList(all)
    return a.addresslist


ecre = re.compile('\n  =\\?                   # literal =?\n  (?P<charset>[^?]*?)   # non-greedy up to the next ? is the charset\n  \\?                    # literal ?\n  (?P<encoding>[qb])    # either a "q" or a "b", case insensitive\n  \\?                    # literal ?\n  (?P<atom>.*?)         # non-greedy up to the next ?= is the atom\n  \\?=                   # literal ?=\n  ', re.VERBOSE | re.IGNORECASE)

def formatdate(timeval=None, localtime=False, usegmt=False):
    if timeval is None:
        timeval = time.time()
    if localtime:
        now = time.localtime(timeval)
        if time.daylight and now[-1]:
            offset = time.altzone
        else:
            offset = time.timezone
        hours, minutes = divmod(abs(offset), 3600)
        if offset > 0:
            sign = '-'
        else:
            sign = '+'
        zone = '%s%02d%02d' % (sign, hours, minutes // 60)
    else:
        now = time.gmtime(timeval)
        if usegmt:
            zone = 'GMT'
        else:
            zone = '-0000'
    return '%s, %02d %s %04d %02d:%02d:%02d %s' % (['Mon',
      'Tue',
      'Wed',
      'Thu',
      'Fri',
      'Sat',
      'Sun'][now[6]],
     now[2],
     ['Jan',
      'Feb',
      'Mar',
      'Apr',
      'May',
      'Jun',
      'Jul',
      'Aug',
      'Sep',
      'Oct',
      'Nov',
      'Dec'][now[1] - 1],
     now[0],
     now[3],
     now[4],
     now[5],
     zone)


def make_msgid(idstring=None):
    timeval = time.time()
    utcdate = time.strftime('%Y%m%d%H%M%S', time.gmtime(timeval))
    pid = os.getpid()
    randint = random.randrange(100000)
    if idstring is None:
        idstring = ''
    else:
        idstring = '.' + idstring
    idhost = socket.getfqdn()
    msgid = '<%s.%s.%s%s@%s>' % (utcdate,
     pid,
     randint,
     idstring,
     idhost)
    return msgid


def parsedate(data):
    return None if not data else _parsedate(data)


def parsedate_tz(data):
    return None if not data else _parsedate_tz(data)


def parseaddr(addr):
    addrs = _AddressList(addr).addresslist
    return ('', '') if not addrs else addrs[0]


def unquote(str):
    if len(str) > 1:
        if str.startswith('"') and str.endswith('"'):
            return str[1:-1].replace('\\\\', '\\').replace('\\"', '"')
        if str.startswith('<') and str.endswith('>'):
            return str[1:-1]
    return str


def decode_rfc2231(s):
    parts = s.split(TICK, 2)
    return (None, None, s) if len(parts) <= 2 else parts


def encode_rfc2231(s, charset=None, language=None):
    import urllib
    s = urllib.quote(s, safe='')
    if charset is None and language is None:
        return s
    else:
        if language is None:
            language = ''
        return "%s'%s'%s" % (charset, language, s)


rfc2231_continuation = re.compile('^(?P<name>\\w+)\\*((?P<num>[0-9]+)\\*?)?$')

def decode_params(params):
    params = params[:]
    new_params = []
    rfc2231_params = {}
    name, value = params.pop(0)
    new_params.append((name, value))
    while params:
        name, value = params.pop(0)
        if name.endswith('*'):
            encoded = True
        else:
            encoded = False
        value = unquote(value)
        mo = rfc2231_continuation.match(name)
        if mo:
            name, num = mo.group('name', 'num')
            if num is not None:
                num = int(num)
            rfc2231_params.setdefault(name, []).append((num, value, encoded))
        new_params.append((name, '"%s"' % quote(value)))

    if rfc2231_params:
        for name, continuations in rfc2231_params.items():
            value = []
            extended = False
            continuations.sort()
            for num, s, encoded in continuations:
                if encoded:
                    s = urllib.unquote(s)
                    extended = True
                value.append(s)

            value = quote(EMPTYSTRING.join(value))
            if extended:
                charset, language, value = decode_rfc2231(value)
                new_params.append((name, (charset, language, '"%s"' % value)))
            new_params.append((name, '"%s"' % value))

    return new_params


def collapse_rfc2231_value(value, errors='replace', fallback_charset='us-ascii'):
    if isinstance(value, tuple):
        rawval = unquote(value[2])
        charset = value[0] or 'us-ascii'
        try:
            return unicode(rawval, charset, errors)
        except LookupError:
            return unicode(rawval, fallback_charset, errors)

    else:
        return unquote(value)
