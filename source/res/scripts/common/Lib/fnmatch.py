# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/fnmatch.py
import re
__all__ = ['filter',
 'fnmatch',
 'fnmatchcase',
 'translate']
_cache = {}
_MAXCACHE = 100

def _purge():
    _cache.clear()


def fnmatch(name, pat):
    import os
    name = os.path.normcase(name)
    pat = os.path.normcase(pat)
    return fnmatchcase(name, pat)


def filter(names, pat):
    import os, posixpath
    result = []
    pat = os.path.normcase(pat)
    try:
        re_pat = _cache[pat]
    except KeyError:
        res = translate(pat)
        if len(_cache) >= _MAXCACHE:
            _cache.clear()
        _cache[pat] = re_pat = re.compile(res)

    match = re_pat.match
    if os.path is posixpath:
        for name in names:
            if match(name):
                result.append(name)

    else:
        for name in names:
            if match(os.path.normcase(name)):
                result.append(name)

    return result


def fnmatchcase(name, pat):
    try:
        re_pat = _cache[pat]
    except KeyError:
        res = translate(pat)
        if len(_cache) >= _MAXCACHE:
            _cache.clear()
        _cache[pat] = re_pat = re.compile(res)

    return re_pat.match(name) is not None


def translate(pat):
    i, n = 0, len(pat)
    res = ''
    while i < n:
        c = pat[i]
        i = i + 1
        if c == '*':
            res = res + '.*'
        if c == '?':
            res = res + '.'
        if c == '[':
            j = i
            if j < n and pat[j] == '!':
                j = j + 1
            if j < n and pat[j] == ']':
                j = j + 1
            while j < n and pat[j] != ']':
                j = j + 1

            if j >= n:
                res = res + '\\['
            else:
                stuff = pat[i:j].replace('\\', '\\\\')
                i = j + 1
                if stuff[0] == '!':
                    stuff = '^' + stuff[1:]
                elif stuff[0] == '^':
                    stuff = '\\' + stuff
                res = '%s[%s]' % (res, stuff)
        res = res + re.escape(c)

    return res + '\\Z(?ms)'
