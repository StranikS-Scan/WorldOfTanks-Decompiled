# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/events_containers/common/container_wrappers.py
from __future__ import absolute_import
from functools import wraps
from constants import IS_DEVELOPMENT

def activateEventsContainer(withDebug=True, withCGF=True):

    def decorator(method):

        @wraps(method)
        def wrapper(*args, **kwargs):
            eventsContainer = method(*args, **kwargs)
            if IS_DEVELOPMENT and withDebug and kwargs.get('withDebug', True):
                eventsContainer.debugEvents()
            if withCGF:
                eventsContainer.attachCFGEvents()
            return eventsContainer

        return wrapper

    return decorator
