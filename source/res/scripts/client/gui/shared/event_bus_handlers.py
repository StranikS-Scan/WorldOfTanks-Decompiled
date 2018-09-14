# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/event_bus_handlers.py
"""Automatic event subscriber/unsubscriber.

Usage:

1. Set the EventBusListener as a metaclass for your class:

    class Foo(EventSystemEntity):
        __metaclass__ = EventBusListener
        ...

2. Mark your handler methods with the @eventBusHandler decorator:

    @eventBusHandler(GameEvent.RADIAL_MENU_CMD, EVENT_BUS_SCOPE.BATTLE)
    def handler(self, event):
        pass

Event subscribing/unsubscribing is performed automatically before the calls
of _populate/_dispose. Note that there is no need to explicitly define
_populate and _dispose methods if your class doesn't use them.
"""
from functools import partial, wraps
from types import FunctionType
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity

class EventBusListener(type):
    """Metaclass for automatic event subscribing/unsubscribing.
    """

    def __new__(mcs, name, bases, namespace):
        cls = type.__new__(mcs, name, bases, namespace)
        if not issubclass(cls, EventSystemEntity):
            raise ValueError('This meta should be applied only to EventSystemEntity classes')
        try:
            handlers = cls.__event_bus_handlers__.copy()
        except AttributeError:
            handlers = {}
            cls._populate = _populateWrapper(cls._populate)
            cls._dispose = _disposeWrapper(cls._dispose)

        for attribute in namespace.values():
            if isinstance(attribute, FunctionType) and getattr(attribute, '__event_bus_data__', None) is not None:
                event = attribute.__event_bus_data__
                if event not in handlers:
                    handlers[event] = attribute
                else:
                    raise ValueError('Event %s is handled multiple times in %s' % (event, cls))

        cls.__event_bus_handlers__ = handlers
        cls.__event_bus_bound_handlers__ = {}
        return cls


def eventBusHandler(event, scope):
    """Decorator for marking method as an event handler.
    """

    def wrapped(method):
        method.__event_bus_data__ = (event, scope)
        return method

    return wrapped


def _populateWrapper(method):
    """Event-subscribing wrapper for the _populate method.
    """

    @wraps(method)
    def wrapped(self, *args, **kwargs):
        for (event, scope), handler in self.__event_bus_handlers__.items():
            boundHandler = partial(handler, self)
            self.addListener(event, boundHandler, scope)
            self.__event_bus_bound_handlers__[event, scope] = boundHandler

        return method(self, *args, **kwargs)

    return wrapped


def _disposeWrapper(method):
    """Event-unsubscribing wrapper for the _dispose method.
    """

    @wraps(method)
    def wrapped(self, *args, **kwargs):
        for (event, scope), boundHandler in self.__event_bus_bound_handlers__.items():
            self.removeListener(event, boundHandler, scope)

        return method(self, *args, **kwargs)

    return wrapped
