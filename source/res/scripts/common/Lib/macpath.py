# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/macpath.py
import os
import warnings
from stat import *
import genericpath
from genericpath import *
from genericpath import _unicode
__all__ = ['normcase',
 'isabs',
 'join',
 'splitdrive',
 'split',
 'splitext',
 'basename',
 'dirname',
 'commonprefix',
 'getsize',
 'getmtime',
 'getatime',
 'getctime',
 'islink',
 'exists',
 'lexists',
 'isdir',
 'isfile',
 'walk',
 'expanduser',
 'expandvars',
 'normpath',
 'abspath',
 'curdir',
 'pardir',
 'sep',
 'pathsep',
 'defpath',
 'altsep',
 'extsep',
 'devnull',
 'realpath',
 'supports_unicode_filenames']
curdir = ':'
pardir = '::'
extsep = '.'
sep = ':'
pathsep = '\n'
defpath = ':'
altsep = None
devnull = 'Dev:Null'

def normcase(path):
    return path.lower()


def isabs(s):
    return ':' in s and s[0] != ':'


def join(s, *p):
    path = s
    for t in p:
        if not path or isabs(t):
            path = t
            continue
        if t[:1] == ':':
            t = t[1:]
        if ':' not in path:
            path = ':' + path
        if path[-1:] != ':':
            path = path + ':'
        path = path + t

    return path


def split(s):
    if ':' not in s:
        return ('', s)
    colon = 0
    for i in range(len(s)):
        if s[i] == ':':
            colon = i + 1

    path, file = s[:colon - 1], s[colon:]
    if path and ':' not in path:
        path = path + ':'
    return (path, file)


def splitext(p):
    return genericpath._splitext(p, sep, altsep, extsep)


splitext.__doc__ = genericpath._splitext.__doc__

def splitdrive(p):
    return ('', p)


def dirname(s):
    return split(s)[0]


def basename(s):
    return split(s)[1]


def ismount(s):
    if not isabs(s):
        return False
    components = split(s)
    return len(components) == 2 and components[1] == ''


def islink(s):
    try:
        import Carbon.File
        return Carbon.File.ResolveAliasFile(s, 0)[2]
    except:
        return False


def lexists(path):
    try:
        st = os.lstat(path)
    except os.error:
        return False

    return True


def expandvars(path):
    return path


def expanduser(path):
    return path


class norm_error(Exception):
    pass


def normpath(s):
    if ':' not in s:
        return ':' + s
    comps = s.split(':')
    i = 1
    while i < len(comps) - 1:
        if comps[i] == '' and comps[i - 1] != '':
            if i > 1:
                del comps[i - 1:i + 1]
                i = i - 1
            else:
                raise norm_error, 'Cannot use :: immediately after volume name'
        i = i + 1

    s = ':'.join(comps)
    if s[-1] == ':' and len(comps) > 2 and s != ':' * len(s):
        s = s[:-1]
    return s


def walk(top, func, arg):
    warnings.warnpy3k('In 3.x, os.path.walk is removed in favor of os.walk.', stacklevel=2)
    try:
        names = os.listdir(top)
    except os.error:
        return

    func(arg, top, names)
    for name in names:
        name = join(top, name)
        if isdir(name) and not islink(name):
            walk(name, func, arg)


def abspath(path):
    if not isabs(path):
        if isinstance(path, _unicode):
            cwd = os.getcwdu()
        else:
            cwd = os.getcwd()
        path = join(cwd, path)
    return normpath(path)


def realpath(path):
    path = abspath(path)
    try:
        import Carbon.File
    except ImportError:
        return path

    if not path:
        return path
    components = path.split(':')
    path = components[0] + ':'
    for c in components[1:]:
        path = join(path, c)
        try:
            path = Carbon.File.FSResolveAliasFile(path, 1)[0].as_pathname()
        except Carbon.File.Error:
            pass

    return path


supports_unicode_filenames = True
