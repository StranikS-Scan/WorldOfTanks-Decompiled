# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/events_handler.py
from inspect import isfunction, ismethod, getmembers
from metaclass import Metaclass
from operator import attrgetter
from typing import Callable, Type
from Event import Event

def eventHandler(func):
    func.isEventHandler = True
    return func


def eventHandlerFor(events):

    def eventHandlerWrapper(func):
        func.events = events
        return eventHandler(func)

    return eventHandlerWrapper


def _isEventHandler(func):
    return getattr(func, 'isEventHandler', False)


def _isMethodEventHandler(method):
    return ismethod(method) and _isEventHandler(method)


def _isFunctionEventHandler(function):
    return isfunction(function) and _isEventHandler(function)


def _getEventHandlers(handler):
    try:
        eventHandlers = handler.__eventHandlers__
    except AttributeError:
        eventHandlers = getmembers(type(handler), _isMethodEventHandler)

    return [ (name, method.__get__(handler)) for name, method in eventHandlers ]


def subscribeToEvents(handler, events, raiseException=True):
    result = False
    if events is not None:
        for name, method in _getEventHandlers(handler):
            event = getattr(events, name) if raiseException else getattr(events, name, None)
            if event is None or not isinstance(event, Event):
                continue
            if hasattr(method, 'events') and not isinstance(events, method.events):
                continue
            event += method
            result = True

    return result


def unsubscribeFromEvents(handler, events):
    result = False
    if events is not None:
        for name, method in _getEventHandlers(handler):
            if hasattr(method, 'events') and not isinstance(events, method.events):
                continue
            event = getattr(events, name, None)
            if event is None or not isinstance(event, Event):
                continue
            event -= method
            result = True

    return result


class EventsHandler(object):
    __metaclass__ = Metaclass

    @classmethod
    def __init_subclass__(cls, _, bases, attributes):
        cls.__eventHandlers__ = getmembers(cls, _isMethodEventHandler)

    def _subscribeToEvents(self, events):
        return subscribeToEvents(self, events)

    def _unsubscribeFromEvents(self, events):
        return unsubscribeFromEvents(self, events)


class EventsQuery(object):
    EVENTS_PROPERTY_NAME = None
    __metaclass__ = Metaclass

    @classmethod
    def __init_subclass__(cls, _, bases, attributes):
        if cls.EVENTS_PROPERTY_NAME:
            cls.__eventsQuery__ = attrgetter(cls.EVENTS_PROPERTY_NAME)
        else:
            cls.__eventsQuery__ = lambda *args: None

    def _getEvents(self, object):
        try:
            return self.__eventsQuery__(object)
        except AttributeError:
            return None

        return None
