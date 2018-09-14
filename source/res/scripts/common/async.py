# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/async.py
"""This module is used for simplifying code based on callbacks, and can be used to write code
like this:

import BigWorld
from async import *

@async
def notify(entityID):
    entity = yield await(BigWorld.lookUpBaseByDBID)('Entity', entityID)
    if not isinstance(entity, bool):
        entity.notify()

The @async function is invoked as usual. It cannot return any value. If this is necessary,
then it should do this by using callback.
@async functions can be used in "yield await" even if they don't have callback parameter.

This module is not safe to use in multithreaded environment. All callbacks are assumed to run
in the same thread as async function calls.
"""
import sys
import BigWorld
from functools import wraps
import inspect

def async(f):
    """Decorator for converting sequence of callbacks to a sequential function.
    Functions that return results in callback should be invoked as
        results = yield await(func)(arg1, args2, ...)
    In this case it is assumed that func has callback parameter, which is called when func has
    results ready.
    """
    if 'callback' not in inspect.getargspec(f).args:

        @wraps(f)
        def caller(*args, **kwargs):
            callback = kwargs.pop('callback', None)
            gen = f(*args, **kwargs)
            try:
                value = next(gen)
                while True:
                    try:
                        result = yield value
                    except GeneratorExit as e:
                        gen.close()
                        raise e
                    except BaseException:
                        value = gen.throw(*sys.exc_info())
                    else:
                        value = gen.send(result)
                        del result

            except StopIteration:
                if callback:
                    callback()

            return

        wrapped = caller
    else:
        wrapped = f

    @wraps(wrapped)
    def wrapper(*args, **kwargs):
        gen = wrapped(*args, **kwargs)
        _stepAsync(gen, None)
        return

    return wrapper


def await(f):
    """Used inside @async functions together with yield to wait results from functions
    that return results from callback.
    Function must have parameter named callback.
    All values passed to callback will be returned from yield statement. For example:
        def remoteFind(key, callback):
            ...
    
        type, value = yield await(remoteFind)(key)
    """

    def wrapper(*args, **kwargs):
        callback = _AsyncCallback()
        kwargs['callback'] = callback
        f(*args, **kwargs)
        return callback

    return wrapper


def deferred(f):
    """Similar to await, but for waiting functions returning twisted Deferred object
    instead of using callback. Deferred is used in BigWorld's two way calls.
    For example:
        try:
            type, value = yield deferred(remoteFind)(key)
        except MyException, e:
            # this code is invoked in case errback is called on deferred
            ...
    """

    def wrapper(*args, **kwargs):
        callback = _AsyncCallback()

        def errback(failure):
            try:
                failure.raiseException()
                assert False
            except:
                callback.fail(sys.exc_info())

        d = f(*args, **kwargs)
        d.addCallback(callback)
        d.addErrback(errback)
        return callback

    return wrapper


def resignTickIfRequired(timeout=0.1):
    """Used inside @async functions together with yield to postpone execution to next tick
    if it is required. Usage example:
        yield resignTickIfRequired()
    
    Note: In case of using the function inside entity function you should check entity destruction.
    """
    callback = _AsyncCallback()
    if BigWorld.isNextTickPending():
        delay(timeout, callback)
    else:
        callback()
    return callback


def delay(timeout, callback):
    """Allows to postpone execution on the specified time."""

    def onTimer(timerID, userArg):
        callback()

    BigWorld.addTimer(onTimer, timeout)


def _stepAsync(gen, args=None, error=None):
    """Executes next fragment of generator."""
    try:
        while True:
            if args is not None and len(args) == 1:
                args = args[0]
            cb = gen.send(args) if error is None else gen.throw(*error)
            if not cb.called:
                cb.detach(gen)
                break
            if not cb.failed:
                args = cb.result
                error = None
            args = None
            error = cb.error

    except StopIteration:
        pass

    return


class _AsyncCallback(object):

    def __init__(self):
        self.__gen = None
        self.called = False
        return

    def detach(self, gen):
        self.__gen = gen

    def __call__(self, *args, **kwargs):
        """Success callback."""
        self.called = True
        self.failed = False
        if self.__gen is None:
            self.result = args
        else:
            _stepAsync(self.__gen, args=args)
        return

    def fail(self, error):
        """Failure callback."""
        self.called = True
        self.failed = True
        if self.__gen is None:
            self.error = error
        else:
            _stepAsync(self.__gen, error=error)
        return
