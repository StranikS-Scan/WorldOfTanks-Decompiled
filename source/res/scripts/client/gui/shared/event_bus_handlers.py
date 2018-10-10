# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/event_bus_handlers.py
from functools import partial, wraps
from types import FunctionType
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from soft_exception import SoftException

class EventBusListener(type):

    def __new__(mcs, name, bases, namespace):
        cls = type.__new__(mcs, name, bases, namespace)
        if not issubclass(cls, EventSystemEntity):
            raise SoftException('This meta should be applied only to EventSystemEntity classes')
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
                    raise SoftException('Event %s is handled multiple times in %s' % (event, cls))

        cls.__event_bus_handlers__ = handlers
        cls.__event_bus_bound_handlers__ = {}
        return cls


def eventBusHandler(event, scope):

    def wrapped(method):
        method.__event_bus_data__ = (event, scope)
        return method

    return wrapped


def _populateWrapper(method):

    @wraps(method)
    def wrapped(self, *args, **kwargs):
        for (event, scope), handler in self.__event_bus_handlers__.items():
            boundHandler = partial(handler, self)
            self.addListener(event, boundHandler, scope)
            self.__event_bus_bound_handlers__[event, scope] = boundHandler

        return method(self, *args, **kwargs)

    return wrapped


def _disposeWrapper(method):

    @wraps(method)
    def wrapped(self, *args, **kwargs):
        for (event, scope), boundHandler in self.__event_bus_bound_handlers__.items():
            self.removeListener(event, boundHandler, scope)

        return method(self, *args, **kwargs)

    return wrapped
