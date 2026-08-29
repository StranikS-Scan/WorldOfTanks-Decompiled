# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/Listener.py
from __future__ import absolute_import
import copy
import weakref

class Listenable:

    def __init__(self):
        self.listeners = _Listeners()

    def addListener(self, eventName, fn):
        self.listeners.addListener(eventName, fn)

    def removeListener(self, eventName, fn):
        self.listeners.removeListener(eventName, fn)


class _Listeners(object):

    def __init__(self):
        self.listeners = {}

    def addListener(self, eventName, fn):
        if eventName not in self.listeners:
            self.listeners[eventName] = set()
        self.listeners[eventName].add(fn)

    def removeListener(self, eventName, fn):
        if eventName in self.listeners and fn in self.listeners[eventName]:
            self.listeners[eventName].remove(fn)
        if eventName in self.listeners and len(self.listeners[eventName]) == 0:
            del self.listeners[eventName]

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return _ListenerDispatch(self, name)


class _ListenerDispatch:

    def __init__(self, dispatcher, eventName):
        self.dispatcher = dispatcher
        self.eventName = eventName

    def __call__(self, *args, **kargs):
        if self.eventName not in self.dispatcher.listeners:
            return
        functions = self.dispatcher.listeners[self.eventName]
        for fn in copy.copy(functions):
            fn(*args, **kargs)


class _ListenerFunc(object):

    def __init__(self, func):
        if hasattr(func, 'im_self'):
            self.isBoundMethod = True
            self.ref = weakref.ref(func.im_self)
            self.func = func.im_func
        else:
            self.isBoundMethod = False
            self.ref = weakref.ref(func)

    def matches(self, func):
        if not self.alive():
            return False
        return func == getattr(self.ref(), self.func.func_name) if self.isBoundMethod else func == self.ref()

    def alive(self):
        return self.ref() is not None

    def get(self):
        obj = self.ref()
        if obj is not None:
            if self.isBoundMethod:
                return getattr(obj, self.func.func_name)
            return obj
        else:
            return

    def __call__(self, *args, **kwargs):
        fn = self.get()
        return fn(*args, **kwargs) if fn is not None else None


class FunctionListeners(object):

    def __init__(self):
        self.listeners = []

    def append(self, func):
        self.listeners.append(_ListenerFunc(func))

    def remove(self, func):
        for listener in self.listeners:
            if listener.matches(func):
                self.listeners.remove(listener)
                break

    def reset(self):
        self.listeners = []

    def __call__(self, *args, **kwargs):
        self.listeners = [ item for item in self.listeners if item.alive() ]
        for listener in self.listeners:
            listener(*args, **kwargs)
