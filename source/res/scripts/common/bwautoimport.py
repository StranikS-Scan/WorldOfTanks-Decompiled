# Embedded file name: scripts/common/BWAutoImport.py
import collections
from collections import namedtuple as _orig_namedtuple

def _fixed_namedtuple(*args, **kwargs):
    res = _orig_namedtuple(*args, **kwargs)
    res._asdict = _fixed_asdict
    return res


def _fixed_asdict(t):
    return dict(zip(t._fields, t))


collections.namedtuple = _fixed_namedtuple
