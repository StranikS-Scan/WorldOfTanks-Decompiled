# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/BWAutoImport.py
import collections
from weakref import proxy as _proxy

def _fix_base_handler_in_urllib2():
    import functools
    from urllib2 import BaseHandler

    def add_parent(self_, parent):
        self_.parent = _proxy(parent)

    functools.update_wrapper(add_parent, BaseHandler.add_parent)
    setattr(BaseHandler, 'add_parent', add_parent)


def _fix_ordered_dict():
    from collections import MutableMapping

    class _Link(object):
        __slots__ = ('prev', 'next', 'key', '__weakref__')

    class OrderedDict(dict, MutableMapping):
        """Dictionary that remembers insertion order"""

        def __init__(self, *args, **kwds):
            """Initialize an ordered dictionary.  Signature is the same as for
            regular dictionaries, but keyword arguments are not recommended
            because their insertion order is arbitrary.
            
            """
            if len(args) > 1:
                raise TypeError('expected at most 1 arguments, got %d' % len(args))
            try:
                self.__root
            except AttributeError:
                self.__hardroot = _Link()
                self.__root = root = _proxy(self.__hardroot)
                root.prev = root.next = root
                self.__map = {}

            self.update(*args, **kwds)

        def __setitem__(self, key, value, dict_setitem=dict.__setitem__, proxy=_proxy, Link=_Link):
            """od.__setitem__(i, y) <==> od[i]=y"""
            if key not in self:
                self.__map[key] = link = Link()
                root = self.__root
                last = root.prev
                link.prev, link.next, link.key = last, root, key
                last.next = link
                root.prev = proxy(link)
            dict.__setitem__(self, key, value)

        def __delitem__(self, key, dict_delitem=dict.__delitem__):
            """od.__delitem__(y) <==> del od[y]"""
            dict_delitem(self, key)
            link = self.__map.pop(key)
            link_prev = link.prev
            link_next = link.next
            link_prev.next = link_next
            link_next.prev = link_prev

        def __iter__(self):
            """od.__iter__() <==> iter(od)"""
            root = self.__root
            curr = root.next
            while curr is not root:
                yield curr.key
                curr = curr.next

        def iteritems(self):
            for key in self:
                yield (key, self[key])

        def itervalues(self):
            for key in self:
                yield self[key]

        def __reversed__(self):
            """od.__reversed__() <==> reversed(od)"""
            root = self.__root
            curr = root.prev
            while curr is not root:
                yield curr.key
                curr = curr.prev

        def __reduce__(self):
            """Return state information for pickling"""
            items = [ [k, self[k]] for k in self ]
            tmp = (self.__map, self.__root)
            del self.__map
            del self.__root
            inst_dict = vars(self).copy()
            self.__map, self.__root = tmp
            return (self.__class__, (items,), inst_dict) if inst_dict else (self.__class__, (items,))

        def clear(self):
            """od.clear() -> None.  Remove all items from od."""
            root = self.__root
            root.prev = root.next = root
            self.__map.clear()
            dict.clear(self)

        def popitem(self, last=True):
            """od.popitem() -> (k, v), return and remove a (key, value) pair.
            Pairs are returned in LIFO order if last is true or FIFO order if false.
            
            """
            if not self:
                raise KeyError('dictionary is empty')
            root = self.__root
            if last:
                link = root.prev
                link_prev = link.prev
                link_prev.next = root
                root.prev = link_prev
            else:
                link = root.next
                link_next = link.next
                root.next = link_next
                link_next.prev = root
            key = link.key
            del self.__map[key]
            value = dict.pop(self, key)
            return (key, value)

        def move_to_end(self, key, last=True):
            """Move an existing element to the end (or beginning if last==False).
            
            Raises KeyError if the element does not exist.
            When last=True, acts like a fast version of self[key]=self.pop(key).
            
            """
            link = self.__map[key]
            link_prev = link.prev
            link_next = link.next
            link_prev.next = link_next
            link_next.prev = link_prev
            root = self.__root
            if last:
                last = root.prev
                link.prev = last
                link.next = root
                last.next = root.prev = link
            else:
                first = root.next
                link.prev = root
                link.next = first
                root.next = first.prev = link

        iterkeys = __iter__
        setdefault = MutableMapping.setdefault
        update = MutableMapping.update
        pop = MutableMapping.pop
        keys = MutableMapping.keys
        values = MutableMapping.values
        items = MutableMapping.items
        __ne__ = MutableMapping.__ne__

        def __repr__(self):
            """od.__repr__() <==> repr(od)"""
            return '%s()' % (self.__class__.__name__,) if not self else '%s(%r)' % (self.__class__.__name__, list(self.items()))

        def copy(self):
            """od.copy() -> a shallow copy of od"""
            return self.__class__(self)

        @classmethod
        def fromkeys(cls, iterable, value=None):
            """OD.fromkeys(S[, v]) -> New ordered dictionary with keys from S
            and values equal to v (which defaults to None).
            
            """
            d = cls()
            for key in iterable:
                d[key] = value

            return d

        def __eq__(self, other):
            """od.__eq__(y) <==> od==y.  Comparison to another OD is order-sensitive
            while comparison to a regular mapping is order-insensitive.
            
            """
            return len(self) == len(other) and all((p == q for p, q in zip(self.items(), other.items()))) if isinstance(other, OrderedDict) else dict.__eq__(self, other)

    collections.OrderedDict = OrderedDict


def _fix_namedtuple():
    from collections import namedtuple as _orig_namedtuple
    import sys as _sys

    def _fixed_namedtuple(*args, **kwargs):

        def _fixed_asdict(t):
            return dict(zip(t._fields, t))

        res = _orig_namedtuple(*args, **kwargs)
        res._asdict = _fixed_asdict
        try:
            res.__module__ = _sys._getframe(1).f_globals.get('__name__', '__main__')
        except (AttributeError, ValueError):
            pass

        return res

    collections.namedtuple = _fixed_namedtuple


_fix_base_handler_in_urllib2()
_fix_ordered_dict()
_fix_namedtuple()
