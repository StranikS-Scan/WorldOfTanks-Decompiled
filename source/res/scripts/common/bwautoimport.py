# Embedded file name: scripts/common/BWAutoImport.py
import collections
from collections import namedtuple as _orig_namedtuple
import sys as _sys

def _fixed_namedtuple(*args, **kwargs):
    res = _orig_namedtuple(*args, **kwargs)
    res._asdict = _fixed_asdict
    try:
        res.__module__ = _sys._getframe(1).f_globals.get('__name__', '__main__')
    except (AttributeError, ValueError):
        pass

    return res


def _fixed_asdict(t):
    return dict(zip(t._fields, t))


collections.namedtuple = _fixed_namedtuple
