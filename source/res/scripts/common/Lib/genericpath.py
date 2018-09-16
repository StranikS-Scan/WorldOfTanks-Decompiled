# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/genericpath.py
import os
import stat
__all__ = ['commonprefix',
 'exists',
 'getatime',
 'getctime',
 'getmtime',
 'getsize',
 'isdir',
 'isfile']

def exists(path):
    try:
        os.stat(path)
    except os.error:
        return False

    return True


def isfile(path):
    try:
        st = os.stat(path)
    except os.error:
        return False

    return stat.S_ISREG(st.st_mode)


def isdir(s):
    try:
        st = os.stat(s)
    except os.error:
        return False

    return stat.S_ISDIR(st.st_mode)


def getsize(filename):
    return os.stat(filename).st_size


def getmtime(filename):
    return os.stat(filename).st_mtime


def getatime(filename):
    return os.stat(filename).st_atime


def getctime(filename):
    return os.stat(filename).st_ctime


def commonprefix(m):
    if not m:
        return ''
    s1 = min(m)
    s2 = max(m)
    for i, c in enumerate(s1):
        if c != s2[i]:
            return s1[:i]

    return s1


def _splitext(p, sep, altsep, extsep):
    sepIndex = p.rfind(sep)
    if altsep:
        altsepIndex = p.rfind(altsep)
        sepIndex = max(sepIndex, altsepIndex)
    dotIndex = p.rfind(extsep)
    if dotIndex > sepIndex:
        filenameIndex = sepIndex + 1
        while filenameIndex < dotIndex:
            if p[filenameIndex] != extsep:
                return (p[:dotIndex], p[dotIndex:])
            filenameIndex += 1

    return (p, '')
