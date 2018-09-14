# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/glob.py
"""Filename globbing utility."""
import sys
import os
import re
import fnmatch
try:
    _unicode = unicode
except NameError:

    class _unicode(object):
        pass


__all__ = ['glob', 'iglob']

def glob(pathname):
    """Return a list of paths matching a pathname pattern.
    
    The pattern may contain simple shell-style wildcards a la
    fnmatch. However, unlike fnmatch, filenames starting with a
    dot are special cases that are not matched by '*' and '?'
    patterns.
    
    """
    return list(iglob(pathname))


def iglob(pathname):
    """Return an iterator which yields the paths matching a pathname pattern.
    
    The pattern may contain simple shell-style wildcards a la
    fnmatch. However, unlike fnmatch, filenames starting with a
    dot are special cases that are not matched by '*' and '?'
    patterns.
    
    """
    if not has_magic(pathname):
        if os.path.lexists(pathname):
            yield pathname
        return
    dirname, basename = os.path.split(pathname)
    if not dirname:
        for name in glob1(os.curdir, basename):
            yield name

        return
    if dirname != pathname and has_magic(dirname):
        dirs = iglob(dirname)
    else:
        dirs = [dirname]
    if has_magic(basename):
        glob_in_dir = glob1
    else:
        glob_in_dir = glob0
    for dirname in dirs:
        for name in glob_in_dir(dirname, basename):
            yield os.path.join(dirname, name)


def glob1(dirname, pattern):
    if not dirname:
        dirname = os.curdir
    if isinstance(pattern, _unicode) and not isinstance(dirname, unicode):
        dirname = unicode(dirname, sys.getfilesystemencoding() or sys.getdefaultencoding())
    try:
        names = os.listdir(dirname)
    except os.error:
        return []

    if pattern[0] != '.':
        names = filter(lambda x: x[0] != '.', names)
    return fnmatch.filter(names, pattern)


def glob0(dirname, basename):
    if basename == '':
        if os.path.isdir(dirname):
            return [basename]
    elif os.path.lexists(os.path.join(dirname, basename)):
        return [basename]
    return []


magic_check = re.compile('[*?[]')

def has_magic(s):
    return magic_check.search(s) is not None
