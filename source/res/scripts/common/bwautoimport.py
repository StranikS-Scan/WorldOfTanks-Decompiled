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

def _fix_base_handler_in_urllib2():
    import weakref
    import functools
    from urllib2 import BaseHandler

    def add_parent(self_, parent):
        self_.parent = weakref.proxy(parent)

    functools.update_wrapper(add_parent, BaseHandler.add_parent)
    setattr(BaseHandler, 'add_parent', add_parent)


_fix_base_handler_in_urllib2()
