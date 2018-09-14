# Embedded file name: scripts/common/async.py
import BigWorld
from functools import partial, wraps
import inspect

def async(f):
    if 'callback' not in inspect.getargspec(f).args:

        @wraps(f)
        def caller(*args, **kwargs):
            callback = kwargs.pop('callback', None)
            gen = f(*args, **kwargs)
            result = None
            try:
                while True:
                    value = gen.send(result)
                    result = yield value

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

        def caller(callback):
            kwargs['callback'] = callback
            return f(*args, **kwargs)

        return caller

    return wrapper


def delay(timeout, callback):

    def onTimer(timerID, userArg):
        callback()

    BigWorld.addTimer(onTimer, timeout)


def _stepAsync(gen, args):
    try:
        waitable = gen.send(args)
        waitable(callback=partial(_asyncCallback, gen))
    except StopIteration:
        pass


def _asyncCallback(gen, *args):
    if len(args) == 1:
        args = args[0]
    _stepAsync(gen, args)
