# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/shelve.py
try:
    from cPickle import Pickler, Unpickler
except ImportError:
    from pickle import Pickler, Unpickler

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import UserDict
__all__ = ['Shelf',
 'BsdDbShelf',
 'DbfilenameShelf',
 'open']

class _ClosedDict(UserDict.DictMixin):

    def closed(self, *args):
        raise ValueError('invalid operation on closed shelf')

    __getitem__ = __setitem__ = __delitem__ = keys = closed

    def __repr__(self):
        pass


class Shelf(UserDict.DictMixin):

    def __init__(self, dict, protocol=None, writeback=False):
        self.dict = dict
        if protocol is None:
            protocol = 0
        self._protocol = protocol
        self.writeback = writeback
        self.cache = {}
        return

    def keys(self):
        return self.dict.keys()

    def __len__(self):
        return len(self.dict)

    def has_key(self, key):
        return key in self.dict

    def __contains__(self, key):
        return key in self.dict

    def get(self, key, default=None):
        return self[key] if key in self.dict else default

    def __getitem__(self, key):
        try:
            value = self.cache[key]
        except KeyError:
            f = StringIO(self.dict[key])
            value = Unpickler(f).load()
            if self.writeback:
                self.cache[key] = value

        return value

    def __setitem__(self, key, value):
        if self.writeback:
            self.cache[key] = value
        f = StringIO()
        p = Pickler(f, self._protocol)
        p.dump(value)
        self.dict[key] = f.getvalue()

    def __delitem__(self, key):
        del self.dict[key]
        try:
            del self.cache[key]
        except KeyError:
            pass

    def close(self):
        self.sync()
        try:
            self.dict.close()
        except AttributeError:
            pass

        try:
            self.dict = _ClosedDict()
        except (NameError, TypeError):
            self.dict = None

        return

    def __del__(self):
        if not hasattr(self, 'writeback'):
            return
        self.close()

    def sync(self):
        if self.writeback and self.cache:
            self.writeback = False
            for key, entry in self.cache.iteritems():
                self[key] = entry

            self.writeback = True
            self.cache = {}
        if hasattr(self.dict, 'sync'):
            self.dict.sync()


class BsdDbShelf(Shelf):

    def __init__(self, dict, protocol=None, writeback=False):
        Shelf.__init__(self, dict, protocol, writeback)

    def set_location(self, key):
        key, value = self.dict.set_location(key)
        f = StringIO(value)
        return (key, Unpickler(f).load())

    def next(self):
        key, value = self.dict.next()
        f = StringIO(value)
        return (key, Unpickler(f).load())

    def previous(self):
        key, value = self.dict.previous()
        f = StringIO(value)
        return (key, Unpickler(f).load())

    def first(self):
        key, value = self.dict.first()
        f = StringIO(value)
        return (key, Unpickler(f).load())

    def last(self):
        key, value = self.dict.last()
        f = StringIO(value)
        return (key, Unpickler(f).load())


class DbfilenameShelf(Shelf):

    def __init__(self, filename, flag='c', protocol=None, writeback=False):
        import anydbm
        Shelf.__init__(self, anydbm.open(filename, flag), protocol, writeback)


def open(filename, flag='c', protocol=None, writeback=False):
    return DbfilenameShelf(filename, flag, protocol, writeback)
