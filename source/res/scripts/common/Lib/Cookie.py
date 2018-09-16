# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/Cookie.py
import string
try:
    from cPickle import dumps, loads
except ImportError:
    from pickle import dumps, loads

import re, warnings
__all__ = ['CookieError',
 'BaseCookie',
 'SimpleCookie',
 'SerialCookie',
 'SmartCookie',
 'Cookie']
_nulljoin = ''.join
_semispacejoin = '; '.join
_spacejoin = ' '.join

class CookieError(Exception):
    pass


_LegalChars = string.ascii_letters + string.digits + "!#$%&'*+-.^_`|~"
_Translator = {'\x00': '\\000',
 '\x01': '\\001',
 '\x02': '\\002',
 '\x03': '\\003',
 '\x04': '\\004',
 '\x05': '\\005',
 '\x06': '\\006',
 '\x07': '\\007',
 '\x08': '\\010',
 '\t': '\\011',
 '\n': '\\012',
 '\x0b': '\\013',
 '\x0c': '\\014',
 '\r': '\\015',
 '\x0e': '\\016',
 '\x0f': '\\017',
 '\x10': '\\020',
 '\x11': '\\021',
 '\x12': '\\022',
 '\x13': '\\023',
 '\x14': '\\024',
 '\x15': '\\025',
 '\x16': '\\026',
 '\x17': '\\027',
 '\x18': '\\030',
 '\x19': '\\031',
 '\x1a': '\\032',
 '\x1b': '\\033',
 '\x1c': '\\034',
 '\x1d': '\\035',
 '\x1e': '\\036',
 '\x1f': '\\037',
 ',': '\\054',
 ';': '\\073',
 '"': '\\"',
 '\\': '\\\\',
 '\x7f': '\\177',
 '\x80': '\\200',
 '\x81': '\\201',
 '\x82': '\\202',
 '\x83': '\\203',
 '\x84': '\\204',
 '\x85': '\\205',
 '\x86': '\\206',
 '\x87': '\\207',
 '\x88': '\\210',
 '\x89': '\\211',
 '\x8a': '\\212',
 '\x8b': '\\213',
 '\x8c': '\\214',
 '\x8d': '\\215',
 '\x8e': '\\216',
 '\x8f': '\\217',
 '\x90': '\\220',
 '\x91': '\\221',
 '\x92': '\\222',
 '\x93': '\\223',
 '\x94': '\\224',
 '\x95': '\\225',
 '\x96': '\\226',
 '\x97': '\\227',
 '\x98': '\\230',
 '\x99': '\\231',
 '\x9a': '\\232',
 '\x9b': '\\233',
 '\x9c': '\\234',
 '\x9d': '\\235',
 '\x9e': '\\236',
 '\x9f': '\\237',
 '\xa0': '\\240',
 '\xa1': '\\241',
 '\xa2': '\\242',
 '\xa3': '\\243',
 '\xa4': '\\244',
 '\xa5': '\\245',
 '\xa6': '\\246',
 '\xa7': '\\247',
 '\xa8': '\\250',
 '\xa9': '\\251',
 '\xaa': '\\252',
 '\xab': '\\253',
 '\xac': '\\254',
 '\xad': '\\255',
 '\xae': '\\256',
 '\xaf': '\\257',
 '\xb0': '\\260',
 '\xb1': '\\261',
 '\xb2': '\\262',
 '\xb3': '\\263',
 '\xb4': '\\264',
 '\xb5': '\\265',
 '\xb6': '\\266',
 '\xb7': '\\267',
 '\xb8': '\\270',
 '\xb9': '\\271',
 '\xba': '\\272',
 '\xbb': '\\273',
 '\xbc': '\\274',
 '\xbd': '\\275',
 '\xbe': '\\276',
 '\xbf': '\\277',
 '\xc0': '\\300',
 '\xc1': '\\301',
 '\xc2': '\\302',
 '\xc3': '\\303',
 '\xc4': '\\304',
 '\xc5': '\\305',
 '\xc6': '\\306',
 '\xc7': '\\307',
 '\xc8': '\\310',
 '\xc9': '\\311',
 '\xca': '\\312',
 '\xcb': '\\313',
 '\xcc': '\\314',
 '\xcd': '\\315',
 '\xce': '\\316',
 '\xcf': '\\317',
 '\xd0': '\\320',
 '\xd1': '\\321',
 '\xd2': '\\322',
 '\xd3': '\\323',
 '\xd4': '\\324',
 '\xd5': '\\325',
 '\xd6': '\\326',
 '\xd7': '\\327',
 '\xd8': '\\330',
 '\xd9': '\\331',
 '\xda': '\\332',
 '\xdb': '\\333',
 '\xdc': '\\334',
 '\xdd': '\\335',
 '\xde': '\\336',
 '\xdf': '\\337',
 '\xe0': '\\340',
 '\xe1': '\\341',
 '\xe2': '\\342',
 '\xe3': '\\343',
 '\xe4': '\\344',
 '\xe5': '\\345',
 '\xe6': '\\346',
 '\xe7': '\\347',
 '\xe8': '\\350',
 '\xe9': '\\351',
 '\xea': '\\352',
 '\xeb': '\\353',
 '\xec': '\\354',
 '\xed': '\\355',
 '\xee': '\\356',
 '\xef': '\\357',
 '\xf0': '\\360',
 '\xf1': '\\361',
 '\xf2': '\\362',
 '\xf3': '\\363',
 '\xf4': '\\364',
 '\xf5': '\\365',
 '\xf6': '\\366',
 '\xf7': '\\367',
 '\xf8': '\\370',
 '\xf9': '\\371',
 '\xfa': '\\372',
 '\xfb': '\\373',
 '\xfc': '\\374',
 '\xfd': '\\375',
 '\xfe': '\\376',
 '\xff': '\\377'}
_idmap = ''.join((chr(x) for x in xrange(256)))

def _quote(str, LegalChars=_LegalChars, idmap=_idmap, translate=string.translate):
    if '' == translate(str, idmap, LegalChars):
        return str
    else:
        return '"' + _nulljoin(map(_Translator.get, str, str)) + '"'


_OctalPatt = re.compile('\\\\[0-3][0-7][0-7]')
_QuotePatt = re.compile('[\\\\].')

def _unquote(str):
    if len(str) < 2:
        return str
    if str[0] != '"' or str[-1] != '"':
        return str
    str = str[1:-1]
    i = 0
    n = len(str)
    res = []
    while 0 <= i < n:
        Omatch = _OctalPatt.search(str, i)
        Qmatch = _QuotePatt.search(str, i)
        if not Omatch and not Qmatch:
            res.append(str[i:])
            break
        j = k = -1
        if Omatch:
            j = Omatch.start(0)
        if Qmatch:
            k = Qmatch.start(0)
        if Qmatch and (not Omatch or k < j):
            res.append(str[i:k])
            res.append(str[k + 1])
            i = k + 2
        res.append(str[i:j])
        res.append(chr(int(str[j + 1:j + 4], 8)))
        i = j + 4

    return _nulljoin(res)


_weekdayname = ['Mon',
 'Tue',
 'Wed',
 'Thu',
 'Fri',
 'Sat',
 'Sun']
_monthname = [None,
 'Jan',
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
 'Dec']

def _getdate(future=0, weekdayname=_weekdayname, monthname=_monthname):
    from time import gmtime, time
    now = time()
    year, month, day, hh, mm, ss, wd, y, z = gmtime(now + future)
    return '%s, %02d %3s %4d %02d:%02d:%02d GMT' % (weekdayname[wd],
     day,
     monthname[month],
     year,
     hh,
     mm,
     ss)


class Morsel(dict):
    _reserved = {'expires': 'expires',
     'path': 'Path',
     'comment': 'Comment',
     'domain': 'Domain',
     'max-age': 'Max-Age',
     'secure': 'secure',
     'httponly': 'httponly',
     'version': 'Version'}

    def __init__(self):
        self.key = self.value = self.coded_value = None
        for K in self._reserved:
            dict.__setitem__(self, K, '')

        return

    def __setitem__(self, K, V):
        K = K.lower()
        if K not in self._reserved:
            raise CookieError('Invalid Attribute %s' % K)
        dict.__setitem__(self, K, V)

    def isReservedKey(self, K):
        return K.lower() in self._reserved

    def set(self, key, val, coded_val, LegalChars=_LegalChars, idmap=_idmap, translate=string.translate):
        if key.lower() in self._reserved:
            raise CookieError('Attempt to set a reserved key: %s' % key)
        if '' != translate(key, idmap, LegalChars):
            raise CookieError('Illegal key value: %s' % key)
        self.key = key
        self.value = val
        self.coded_value = coded_val

    def output(self, attrs=None, header='Set-Cookie:'):
        return '%s %s' % (header, self.OutputString(attrs))

    __str__ = output

    def __repr__(self):
        return '<%s: %s=%s>' % (self.__class__.__name__, self.key, repr(self.value))

    def js_output(self, attrs=None):
        return '\n        <script type="text/javascript">\n        <!-- begin hiding\n        document.cookie = "%s";\n        // end hiding -->\n        </script>\n        ' % (self.OutputString(attrs).replace('"', '\\"'),)

    def OutputString(self, attrs=None):
        result = []
        RA = result.append
        RA('%s=%s' % (self.key, self.coded_value))
        if attrs is None:
            attrs = self._reserved
        items = self.items()
        items.sort()
        for K, V in items:
            if V == '':
                continue
            if K not in attrs:
                continue
            if K == 'expires' and type(V) == type(1):
                RA('%s=%s' % (self._reserved[K], _getdate(V)))
            if K == 'max-age' and type(V) == type(1):
                RA('%s=%d' % (self._reserved[K], V))
            if K == 'secure':
                RA(str(self._reserved[K]))
            if K == 'httponly':
                RA(str(self._reserved[K]))
            RA('%s=%s' % (self._reserved[K], V))

        return _semispacejoin(result)


_LegalCharsPatt = "[\\w\\d!#%&'~_`><@,:/\\$\\*\\+\\-\\.\\^\\|\\)\\(\\?\\}\\{\\=]"
_CookiePattern = re.compile('(?x)(?P<key>' + _LegalCharsPatt + '+?)\\s*=\\s*(?P<val>"(?:[^\\\\"]|\\\\.)*"|\\w{3},\\s[\\s\\w\\d-]{9,11}\\s[\\d:]{8}\\sGMT|' + _LegalCharsPatt + '*)\\s*;?')

class BaseCookie(dict):

    def value_decode(self, val):
        return (val, val)

    def value_encode(self, val):
        strval = str(val)
        return (strval, strval)

    def __init__(self, input=None):
        if input:
            self.load(input)

    def __set(self, key, real_value, coded_value):
        M = self.get(key, Morsel())
        M.set(key, real_value, coded_value)
        dict.__setitem__(self, key, M)

    def __setitem__(self, key, value):
        rval, cval = self.value_encode(value)
        self.__set(key, rval, cval)

    def output(self, attrs=None, header='Set-Cookie:', sep='\r\n'):
        result = []
        items = self.items()
        items.sort()
        for K, V in items:
            result.append(V.output(attrs, header))

        return sep.join(result)

    __str__ = output

    def __repr__(self):
        L = []
        items = self.items()
        items.sort()
        for K, V in items:
            L.append('%s=%s' % (K, repr(V.value)))

        return '<%s: %s>' % (self.__class__.__name__, _spacejoin(L))

    def js_output(self, attrs=None):
        result = []
        items = self.items()
        items.sort()
        for K, V in items:
            result.append(V.js_output(attrs))

        return _nulljoin(result)

    def load(self, rawdata):
        if type(rawdata) == type(''):
            self.__ParseString(rawdata)
        else:
            for k, v in rawdata.items():
                self[k] = v

    def __ParseString(self, str, patt=_CookiePattern):
        i = 0
        n = len(str)
        M = None
        while 0 <= i < n:
            match = patt.search(str, i)
            if not match:
                break
            K, V = match.group('key'), match.group('val')
            i = match.end(0)
            if K[0] == '$':
                if M:
                    M[K[1:]] = V
            if K.lower() in Morsel._reserved:
                if M:
                    M[K] = _unquote(V)
            rval, cval = self.value_decode(V)
            self.__set(K, rval, cval)
            M = self[K]

        return


class SimpleCookie(BaseCookie):

    def value_decode(self, val):
        return (_unquote(val), val)

    def value_encode(self, val):
        strval = str(val)
        return (strval, _quote(strval))


class SerialCookie(BaseCookie):

    def __init__(self, input=None):
        warnings.warn('SerialCookie class is insecure; do not use it', DeprecationWarning)
        BaseCookie.__init__(self, input)

    def value_decode(self, val):
        return (loads(_unquote(val)), val)

    def value_encode(self, val):
        return (val, _quote(dumps(val)))


class SmartCookie(BaseCookie):

    def __init__(self, input=None):
        warnings.warn('Cookie/SmartCookie class is insecure; do not use it', DeprecationWarning)
        BaseCookie.__init__(self, input)

    def value_decode(self, val):
        strval = _unquote(val)
        try:
            return (loads(strval), val)
        except:
            return (strval, val)

    def value_encode(self, val):
        if type(val) == type(''):
            return (val, _quote(val))
        else:
            return (val, _quote(dumps(val)))


Cookie = SmartCookie

def _test():
    import doctest, Cookie
    return doctest.testmod(Cookie)


if __name__ == '__main__':
    _test()
