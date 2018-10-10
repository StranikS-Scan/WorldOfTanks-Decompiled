# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/_threading_local.py
__all__ = ['local']

class _localbase(object):
    __slots__ = ('_local__key', '_local__args', '_local__lock')

    def __new__(cls, *args, **kw):
        self = object.__new__(cls)
        key = ('_local__key', 'thread.local.' + str(id(self)))
        object.__setattr__(self, '_local__key', key)
        object.__setattr__(self, '_local__args', (args, kw))
        object.__setattr__(self, '_local__lock', RLock())
        if (args or kw) and cls.__init__ is object.__init__:
            raise TypeError('Initialization arguments are not supported')
        dict = object.__getattribute__(self, '__dict__')
        current_thread().__dict__[key] = dict
        return self


def _patch(self):
    key = object.__getattribute__(self, '_local__key')
    d = current_thread().__dict__.get(key)
    if d is None:
        d = {}
        current_thread().__dict__[key] = d
        object.__setattr__(self, '__dict__', d)
        cls = type(self)
        if cls.__init__ is not object.__init__:
            args, kw = object.__getattribute__(self, '_local__args')
            cls.__init__(self, *args, **kw)
    else:
        object.__setattr__(self, '__dict__', d)
    return


class local(_localbase):

    def __getattribute__(self, name):
        lock = object.__getattribute__(self, '_local__lock')
        lock.acquire()
        try:
            _patch(self)
            return object.__getattribute__(self, name)
        finally:
            lock.release()

    def __setattr__(self, name, value):
        if name == '__dict__':
            raise AttributeError("%r object attribute '__dict__' is read-only" % self.__class__.__name__)
        lock = object.__getattribute__(self, '_local__lock')
        lock.acquire()
        try:
            _patch(self)
            return object.__setattr__(self, name, value)
        finally:
            lock.release()

    def __delattr__(self, name):
        if name == '__dict__':
            raise AttributeError("%r object attribute '__dict__' is read-only" % self.__class__.__name__)
        lock = object.__getattribute__(self, '_local__lock')
        lock.acquire()
        try:
            _patch(self)
            return object.__delattr__(self, name)
        finally:
            lock.release()

    def __del__(self):
        import threading
        key = object.__getattribute__(self, '_local__key')
        try:
            threads = threading._enumerate()
        except:
            return

        for thread in threads:
            try:
                __dict__ = thread.__dict__
            except AttributeError:
                continue

            if key in __dict__:
                try:
                    del __dict__[key]
                except KeyError:
                    pass


from threading import current_thread, RLock
