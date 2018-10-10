# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-riscos/riscospath.py
curdir = '@'
pardir = '^'
extsep = '/'
sep = '.'
pathsep = ','
defpath = '<Run$Dir>'
altsep = None
import os, stat, string
try:
    import swi
except ImportError:

    class _swi:

        def swi(*a):
            raise AttributeError, 'This function only available under RISC OS'

        block = swi


    swi = _swi()

_false, _true = range(2)
_roots = ['$',
 '&',
 '%',
 '@',
 '\\']
_allowMOSFSNames = _false

def _split(p):
    dash = _allowMOSFSNames and p[:1] == '-'
    if dash:
        q = string.find(p, '-', 1) + 1
    elif p[:1] == ':':
        q = 0
    else:
        q = string.find(p, ':') + 1
    s = string.find(p, '#')
    if s == -1 or s > q:
        s = q
    else:
        for c in p[dash:s]:
            if c not in string.ascii_letters:
                q = 0
                break

    r = q
    if p[q:q + 1] == ':':
        r = string.find(p, '.', q + 1) + 1
        if r == 0:
            r = len(p)
    return (p[:q], p[q:r], p[r:])


def normcase(p):
    return string.lower(p)


def isabs(p):
    fs, drive, path = _split(p)
    return drive != '' or path[:1] in _roots


def join(a, *p):
    j = a
    for b in p:
        fs, drive, path = _split(b)
        if j == '' or fs != '' or drive != '' or path[:1] in _roots:
            j = b
        if j[-1] == ':':
            j = j + b
        j = j + '.' + b

    return j


def split(p):
    fs, drive, path = _split(p)
    q = string.rfind(path, '.')
    return (fs + drive + path[:q], path[q + 1:]) if q != -1 else ('', p)


def splitext(p):
    tail, head = split(p)
    if '/' in head:
        q = len(head) - string.rfind(head, '/')
        return (p[:-q], p[-q:])
    return (p, '')


def splitdrive(p):
    fs, drive, path = _split(p)
    return (fs + drive, p)


def basename(p):
    return split(p)[1]


def dirname(p):
    return split(p)[0]


def commonprefix(m):
    if not m:
        return ''
    s1 = min(m)
    s2 = max(m)
    n = min(len(s1), len(s2))
    for i in xrange(n):
        if s1[i] != s2[i]:
            return s1[:i]

    return s1[:n]


def getsize(p):
    st = os.stat(p)
    return st[stat.ST_SIZE]


def getmtime(p):
    st = os.stat(p)
    return st[stat.ST_MTIME]


getatime = getmtime

def exists(p):
    try:
        return swi.swi('OS_File', '5s;i', p) != 0
    except swi.error:
        return 0


lexists = exists

def isdir(p):
    try:
        return swi.swi('OS_File', '5s;i', p) in (2, 3)
    except swi.error:
        return 0


def isfile(p):
    try:
        return swi.swi('OS_File', '5s;i', p) in (1, 3)
    except swi.error:
        return 0


def islink(p):
    return _false


ismount = islink

def samefile(fa, fb):
    l = 512
    b = swi.block(l)
    swi.swi('OS_FSControl', 'isb..i', 37, fa, b, l)
    fa = b.ctrlstring()
    swi.swi('OS_FSControl', 'isb..i', 37, fb, b, l)
    fb = b.ctrlstring()
    return fa == fb


def sameopenfile(a, b):
    return os.fstat(a)[stat.ST_INO] == os.fstat(b)[stat.ST_INO]


def expanduser(p):
    fs, drive, path = _split(p)
    l = 512
    b = swi.block(l)
    if path[:1] != '@':
        return p
    if fs == '':
        fsno = swi.swi('OS_Args', '00;i')
        swi.swi('OS_FSControl', 'iibi', 33, fsno, b, l)
        fsname = b.ctrlstring()
    else:
        if fs[:1] == '-':
            fsname = fs[1:-1]
        else:
            fsname = fs[:-1]
        fsname = string.split(fsname, '#', 1)[0]
    x = swi.swi('OS_FSControl', 'ib2s.i;.....i', 54, b, fsname, l)
    if x < l:
        urd = b.tostring(0, l - x - 1)
    else:
        x = swi.swi('OS_FSControl', 'ib0s.i;.....i', 54, b, fsname, l)
        if x < l:
            urd = b.tostring(0, l - x - 1)
        else:
            urd = '$'
    return fsname + ':' + urd + path[1:]


def expandvars(p):
    l = 512
    b = swi.block(l)
    return b.tostring(0, swi.swi('OS_GSTrans', 'sbi;..i', p, b, l))


abspath = os.expand
realpath = abspath

def normpath(p):
    fs, drive, path = _split(p)
    rhs = ''
    ups = 0
    while path != '':
        path, el = split(path)
        if el == '^':
            ups = ups + 1
        if ups > 0:
            ups = ups - 1
        if rhs == '':
            rhs = el
        rhs = el + '.' + rhs

    while ups > 0:
        ups = ups - 1
        rhs = '^.' + rhs

    return fs + drive + rhs


def walk(top, func, arg):
    try:
        names = os.listdir(top)
    except os.error:
        return

    func(arg, top, names)
    for name in names:
        name = join(top, name)
        if isdir(name) and not islink(name):
            walk(name, func, arg)
