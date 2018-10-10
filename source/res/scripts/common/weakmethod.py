# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/WeakMethod.py
from weakref import ref

class WeakMethod(ref):
    __slots__ = ('_func_ref', '_meth_type', '_alive', '__weakref__')

    def __new__(cls, meth, callback=None):
        try:
            obj = meth.__self__
            func = meth.__func__
        except AttributeError:
            raise TypeError('argument should be a bound method')

        def _cb(arg):
            self = self_wr()
            if self._alive:
                self._alive = False
                if callback is not None:
                    callback(self)
            return

        self = ref.__new__(cls, obj, _cb)
        self._func_ref = ref(func, _cb)
        self._meth_type = type(meth)
        self._alive = True
        self_wr = ref(self)
        return self

    def __call__(self):
        obj = super(WeakMethod, self).__call__()
        func = self._func_ref()
        return None if obj is None or func is None else self._meth_type(func, obj)

    def __eq__(self, other):
        if isinstance(other, WeakMethod):
            if not self._alive or not other._alive:
                return self is other
            return ref.__eq__(self, other) and self._func_ref == other._func_ref
        return False

    def __ne__(self, other):
        if isinstance(other, WeakMethod):
            if not self._alive or not other._alive:
                return self is not other
            return ref.__ne__(self, other) or self._func_ref != other._func_ref
        return True

    def __repr__(self):
        return self._func_ref.__repr__()

    __hash__ = ref.__hash__


class WeakMethodProxy(object):

    def __init__(self, method, callback=None):
        self._methodRef = WeakMethod(method, callback)

    def __call__(self, *args, **kwargs):
        method = self._methodRef()
        return method(*args, **kwargs)

    def __eq__(self, other):
        return self._methodRef == other._methodRef if isinstance(other, WeakMethodProxy) else False

    def __ne__(self, other):
        return self._methodRef != other._methodRef if isinstance(other, WeakMethodProxy) else True

    def __hash__(self):
        return self._methodRef.__hash__()

    def __repr__(self):
        return self._methodRef.__repr__()
