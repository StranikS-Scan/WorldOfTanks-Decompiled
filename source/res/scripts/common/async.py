# Embedded file name: scripts/common/async.py
import sys
import BigWorld
from functools import partial, wraps
import inspect

def async(f):
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

    def wrapper(*args, **kwargs):
        callback = _AsyncCallback()
        kwargs['callback'] = callback
        f(*args, **kwargs)
        return callback

    return wrapper


def deferred(f):

    def wrapper(*args, **kwargs):
        callback = _AsyncCallback()

        def errback(failure):
            try:
                failure.raiseException()
                raise False or AssertionError
            except:
                callback.fail(sys.exc_info())

        d = f(*args, **kwargs)
        d.addCallback(callback)
        d.addErrback(errback)
        return callback

    return wrapper


def resignTickIfRequired(timeout = 0.1):
    callback = _AsyncCallback()
    if BigWorld.isNextTickPending():
        delay(timeout, callback)
    else:
        callback()
    return callback


def delay(timeout, callback):

    def onTimer(timerID, userArg):
        callback()

    BigWorld.addTimer(onTimer, timeout)


def _stepAsync(gen, args = None, error = None):
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
            else:
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
        self.called = True
        self.failed = False
        if self.__gen is None:
            self.result = args
        else:
            _stepAsync(self.__gen, args=args)
        return

    def fail(self, error):
        self.called = True
        self.failed = True
        if self.__gen is None:
            self.error = error
        else:
            _stepAsync(self.__gen, error=error)
        return
