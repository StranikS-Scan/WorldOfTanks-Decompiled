# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/wotdecorators.py
import inspect
from functools import update_wrapper
from typing import TypeVar, Type, Generic
from constants import IS_CLIENT, IS_BOT, IS_CGF_DUMP, IS_VS_EDITOR
from debug_utils import LOG_WRAPPED_CURRENT_EXCEPTION, CRITICAL_ERROR, LOG_ERROR, wraps
from time_tracking import LOG_TIME_WARNING
import time
import time_tracking
CLASS = TypeVar('CLASS')
if not IS_CLIENT and not IS_BOT and not IS_CGF_DUMP and not IS_VS_EDITOR:
    from insights.measurements import incrTickOverspends

def _argsToLogID(args):
    for arg in args:
        if hasattr(arg, '__getattribute__') or hasattr(arg, '__getattr__'):
            continue
        logID = getattr(arg, 'logID', None)
        if logID is not None:
            return logID

    return


def _logErrorMessageFromArgs(prefix, args):
    logID = _argsToLogID(args)
    if logID is not None:
        LOG_ERROR(prefix, logID)
    return


def noexcept(func):

    def noexceptWrapper(*args, **kwArgs):
        try:
            return func(*args, **kwArgs)
        except:
            _logErrorMessageFromArgs('Exception in noexcept', args)
            LOG_WRAPPED_CURRENT_EXCEPTION(noexceptWrapper.__name__, func.__name__, func.func_code.co_filename, func.func_code.co_firstlineno + 1)

    return noexceptWrapper


def noexceptReturn(returnOnExcept):

    def noexcept(func):

        def noexceptWrapper(*args, **kwArgs):
            try:
                return func(*args, **kwArgs)
            except:
                _logErrorMessageFromArgs('Exception in noexcept', args)
                LOG_WRAPPED_CURRENT_EXCEPTION(noexceptWrapper.__name__, func.__name__, func.func_code.co_filename, func.func_code.co_firstlineno + 1)

            return returnOnExcept

        return noexceptWrapper

    return noexcept


def nofail(func):

    def nofailWrapper(*args, **kwArgs):
        try:
            return func(*args, **kwArgs)
        except:
            LOG_WRAPPED_CURRENT_EXCEPTION(nofailWrapper.__name__, func.__name__, func.func_code.co_filename, func.func_code.co_firstlineno + 1)
            CRITICAL_ERROR('Exception in no-fail code')

    return nofailWrapper


def exposedtoclient(func):

    def exposedtoclientWrapper(*args, **kwArgs):
        try:
            lastTick = time.time()
            result = func(*args, **kwArgs)
            timeSinceLastTick = time.time() - lastTick
            if timeSinceLastTick > time_tracking.DEFAULT_TIME_LIMIT:
                LOG_TIME_WARNING(timeSinceLastTick, context=(getattr(args[0], 'id', 0),
                 func.__name__,
                 args,
                 kwArgs))
                if not IS_CLIENT and not IS_BOT:
                    incrTickOverspends()
            return result
        except:
            _logErrorMessageFromArgs('Exception in exposedtoclient', args)
            LOG_WRAPPED_CURRENT_EXCEPTION(exposedtoclientWrapper.__name__, func.__name__, func.func_code.co_filename, func.func_code.co_firstlineno + 1)

    return exposedtoclientWrapper


def singleton(cls):
    return cls()


def decorate(func, dec):
    argspec = inspect.getargspec(func)
    name = func.__name__
    signature = inspect.formatargspec(*argspec)
    params = inspect.formatargspec(formatvalue=(lambda value: ''), *argspec)
    source = 'def %s%s: return __dec%s\n' % (name, signature, params)
    code = compile(source, '<decorator-gen>', 'single')
    env = {'__dec': dec}
    eval(code, env)
    return update_wrapper(env[name], func)


def decorator(dec):

    def wrapper(func):
        return decorate(func, dec(func))

    return wrapper


def condition(attributeName, logFunc=None, logStack=True):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            attribute = getattr(args[0], attributeName)
            if not bool(attribute):
                if logFunc:
                    logFunc('Method condition failed', attributeName, attribute, getattr(args[0], 'id', None), func.__name__, args, kwargs, stack=logStack)
                return
            else:
                return func(*args, **kwargs)

        return decorate(func, wrapper)

    return decorator
