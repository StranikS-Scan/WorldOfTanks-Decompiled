# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/stricted_loading.py
import weakref
import functools
import inspect
import BigWorld
import debug_utils
from constants import IS_EDITOR
_MAX_PRIORITY = 96
_HIGH_PRIORITY = 128

def loadingPriority(vehicleID):
    if IS_EDITOR:
        return _MAX_PRIORITY
    if not BigWorld.player().userSeesWorld():
        priority = _HIGH_PRIORITY if vehicleID == BigWorld.player().playerVehicleID else _MAX_PRIORITY
    else:
        priority = _MAX_PRIORITY
    return priority


def restrictBySpace(callback, *args, **kwargs):
    return functools.partial(_restrictedLoadCall, BigWorld.player().spaceID, None, callback, args=args, kwargs=kwargs)


def restrictBySpaceAndNode(node, callback, *args, **kwargs):
    return functools.partial(_restrictedLoadCall, BigWorld.player().spaceID, node, callback, args=args, kwargs=kwargs)


def _restrictedLoadCall(spaceID, node, callback, resource, args, kwargs):
    player = BigWorld.player()
    fail = player is None or player.spaceID != spaceID
    fail |= node is not None and node.isDangling
    if fail:
        debug_utils.LOG_DEBUG('Background loading callback is too late, stopping logic')
        return
    else:
        callback(*(args + (resource,)), **kwargs)
        return


_LOG_LEAKS = False
_LOG_MSG = 'Prevented possible leak of callback!'

def makeCallbackWeak(callback, *args, **kwargs):
    if inspect.ismethod(callback):
        if callback.im_self is not None:
            selfWeak = weakref.ref(callback.im_self)
            methodWeak = weakref.ref(callback.im_func)
            return functools.partial(_weakMethodCall, selfWeak, methodWeak, args, kwargs)
    callbackWeak = weakref.ref(callback)
    return functools.partial(_weakCall, callbackWeak, args, kwargs)


def _weakMethodCall(selfWeak, methodWeak, predefArgs, predefKwargs, *args, **kwargs):
    self = selfWeak()
    if self is None:
        if _LOG_LEAKS:
            debug_utils.LOG_WARNING(_LOG_MSG, stack=True)
        return
    else:
        method = methodWeak()
        if methodWeak is None:
            if _LOG_LEAKS:
                debug_utils.LOG_WARNING(_LOG_MSG, stack=True)
            return
        finalArgs = predefArgs + args
        finalKwargs = predefKwargs
        finalKwargs.update(kwargs)
        method(self, *finalArgs, **finalKwargs)
        return


def _weakCall(callbackWeak, predefArgs, predefKwargs, *args, **kwargs):
    callback = callbackWeak()
    if callback:
        finalArgs = predefArgs + args
        finalKwargs = predefKwargs
        finalKwargs.update(kwargs)
        callback(*finalArgs, **finalKwargs)
    elif _LOG_LEAKS:
        debug_utils.LOG_WARNING(_LOG_MSG, stack=True)
