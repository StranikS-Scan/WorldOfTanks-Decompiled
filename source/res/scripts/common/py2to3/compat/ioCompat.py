# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/py2to3/compat/ioCompat.py
from __future__ import absolute_import
import typing
from past.builtins import unicode

def _toUnicode(value, errors='replace'):
    if isinstance(value, unicode):
        return value
    return value.decode('utf-8', errors=errors) if isinstance(value, bytes) else unicode(value)


class UnicodeFileAdapter(object):

    def __init__(self, target):
        self.target = target

    def write(self, data):
        return self.target.write(_toUnicode(data))

    def writelines(self, lines):
        return self.target.writelines((_toUnicode(line) for line in lines))

    def __getattr__(self, name):
        return getattr(self.target, name)
