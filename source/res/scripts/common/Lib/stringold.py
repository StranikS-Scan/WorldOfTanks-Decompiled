# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/stringold.py
from warnings import warnpy3k
warnpy3k('the stringold module has been removed in Python 3.0', stacklevel=2)
del warnpy3k
whitespace = ' \t\n\r\x0b\x0c'
lowercase = 'abcdefghijklmnopqrstuvwxyz'
uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
letters = lowercase + uppercase
digits = '0123456789'
hexdigits = digits + 'abcdef' + 'ABCDEF'
octdigits = '01234567'
_idmap = ''
for i in range(256):
    _idmap = _idmap + chr(i)

del i
index_error = ValueError
atoi_error = ValueError
atof_error = ValueError
atol_error = ValueError

def lower(s):
    return s.lower()


def upper(s):
    return s.upper()


def swapcase(s):
    return s.swapcase()


def strip(s):
    return s.strip()


def lstrip(s):
    return s.lstrip()


def rstrip(s):
    return s.rstrip()


def split(s, sep=None, maxsplit=0):
    return s.split(sep, maxsplit)


splitfields = split

def join(words, sep=' '):
    return sep.join(words)


joinfields = join
_apply = apply

def index(s, *args):
    return _apply(s.index, args)


def rindex(s, *args):
    return _apply(s.rindex, args)


def count(s, *args):
    return _apply(s.count, args)


def find(s, *args):
    return _apply(s.find, args)


def rfind(s, *args):
    return _apply(s.rfind, args)


_float = float
_int = int
_long = long
_StringType = type('')

def atof(s):
    if type(s) == _StringType:
        return _float(s)
    raise TypeError('argument 1: expected string, %s found' % type(s).__name__)


def atoi(*args):
    try:
        s = args[0]
    except IndexError:
        raise TypeError('function requires at least 1 argument: %d given' % len(args))

    if type(s) == _StringType:
        return _apply(_int, args)
    raise TypeError('argument 1: expected string, %s found' % type(s).__name__)


def atol(*args):
    try:
        s = args[0]
    except IndexError:
        raise TypeError('function requires at least 1 argument: %d given' % len(args))

    if type(s) == _StringType:
        return _apply(_long, args)
    raise TypeError('argument 1: expected string, %s found' % type(s).__name__)


def ljust(s, width):
    n = width - len(s)
    return s if n <= 0 else s + ' ' * n


def rjust(s, width):
    n = width - len(s)
    return s if n <= 0 else ' ' * n + s


def center(s, width):
    n = width - len(s)
    if n <= 0:
        return s
    half = n / 2
    if n % 2 and width % 2:
        half = half + 1
    return ' ' * half + s + ' ' * (n - half)


def zfill(x, width):
    if type(x) == type(''):
        s = x
    else:
        s = repr(x)
    n = len(s)
    if n >= width:
        return s
    sign = ''
    if s[0] in ('-', '+'):
        sign, s = s[0], s[1:]
    return sign + '0' * (width - n) + s


def expandtabs(s, tabsize=8):
    res = line = ''
    for c in s:
        if c == '\t':
            c = ' ' * (tabsize - len(line) % tabsize)
        line = line + c
        if c == '\n':
            res = res + line
            line = ''

    return res + line


def translate(s, table, deletions=''):
    return s.translate(table, deletions)


def capitalize(s):
    return s.capitalize()


def capwords(s, sep=None):
    return join(map(capitalize, s.split(sep)), sep or ' ')


_idmapL = None

def maketrans(fromstr, tostr):
    global _idmapL
    if len(fromstr) != len(tostr):
        raise ValueError, 'maketrans arguments must have same length'
    if not _idmapL:
        _idmapL = list(_idmap)
    L = _idmapL[:]
    fromstr = map(ord, fromstr)
    for i in range(len(fromstr)):
        L[fromstr[i]] = tostr[i]

    return join(L, '')


def replace(s, old, new, maxsplit=0):
    return s.replace(old, new, maxsplit)


try:
    ''.upper
except AttributeError:
    from stringold import *

try:
    from strop import maketrans, lowercase, uppercase, whitespace
    letters = lowercase + uppercase
except ImportError:
    pass
