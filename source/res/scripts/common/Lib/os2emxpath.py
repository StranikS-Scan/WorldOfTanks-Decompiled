# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/os2emxpath.py
import os
import stat
from genericpath import *
from genericpath import _unicode
from ntpath import expanduser, expandvars, isabs, islink, splitdrive, splitext, split, walk
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
 'ismount',
 'walk',
 'expanduser',
 'expandvars',
 'normpath',
 'abspath',
 'splitunc',
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
curdir = '.'
pardir = '..'
extsep = '.'
sep = '/'
altsep = '\\'
pathsep = ';'
defpath = '.;C:\\bin'
devnull = 'nul'

def normcase(s):
    return s.replace('\\', '/').lower()


def join(a, *p):
    path = a
    for b in p:
        if isabs(b):
            path = b
        if path == '' or path[-1:] in '/\\:':
            path = path + b
        path = path + '/' + b

    return path


def splitunc(p):
    if p[1:2] == ':':
        return ('', p)
    firstTwo = p[0:2]
    if firstTwo == '//' or firstTwo == '\\\\':
        normp = normcase(p)
        index = normp.find('/', 2)
        if index == -1:
            return ('', p)
        index = normp.find('/', index + 1)
        if index == -1:
            index = len(p)
        return (p[:index], p[index:])
    return ('', p)


def basename(p):
    return split(p)[1]


def dirname(p):
    return split(p)[0]


lexists = exists

def ismount(path):
    unc, rest = splitunc(path)
    if unc:
        return rest in ('', '/', '\\')
    p = splitdrive(path)[1]
    return len(p) == 1 and p[0] in '/\\'


def normpath(path):
    path = path.replace('\\', '/')
    prefix, path = splitdrive(path)
    while path[:1] == '/':
        prefix = prefix + '/'
        path = path[1:]

    comps = path.split('/')
    i = 0
    while i < len(comps):
        if comps[i] == '.':
            del comps[i]
        if comps[i] == '..' and i > 0 and comps[i - 1] not in ('', '..'):
            del comps[i - 1:i + 1]
            i = i - 1
        if comps[i] == '' and i > 0 and comps[i - 1] != '':
            del comps[i]
        i = i + 1

    if not prefix and not comps:
        comps.append('.')
    return prefix + '/'.join(comps)


def abspath(path):
    if not isabs(path):
        if isinstance(path, _unicode):
            cwd = os.getcwdu()
        else:
            cwd = os.getcwd()
        path = join(cwd, path)
    return normpath(path)


realpath = abspath
supports_unicode_filenames = False
