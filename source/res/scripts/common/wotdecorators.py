# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/wotdecorators.py
import inspect
import logging
from functools import update_wrapper, wraps
from typing import TypeVar, Type, Generic, Callable, Any
from constants import IS_CLIENT, IS_BOT, IS_CGF_DUMP, IS_VS_EDITOR, IS_UE_EDITOR, IS_BASEAPP, IS_CELLAPP, IS_DEVELOPMENT, SERVER_TICK_LENGTH
from debug_utils import LOG_CURRENT_EXCEPTION, CRITICAL_ERROR, LOG_ERROR
from soft_exception import SoftException
from time_tracking import LOG_TIME_WARNING
import time
import time_tracking
CLASS = TypeVar('CLASS')
if not IS_CLIENT and not IS_BOT and not IS_CGF_DUMP and not IS_VS_EDITOR and not IS_UE_EDITOR:
    from insights.measurements import incrTickOverspends
logger = logging.getLogger(__name__)

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

    @wraps(func)
    def noexceptWrapper(*args, **kwArgs):
        try:
            return func(*args, **kwArgs)
        except:
            _logErrorMessageFromArgs('Exception in noexcept', args)
            LOG_CURRENT_EXCEPTION()

    return noexceptWrapper


def noexceptReturn(returnOnExcept):

    def noexcept(func):

        @wraps(func)
        def noexceptWrapper(*args, **kwArgs):
            try:
                return func(*args, **kwArgs)
            except:
                _logErrorMessageFromArgs('Exception in noexcept', args)
                LOG_CURRENT_EXCEPTION()

            return returnOnExcept

        return noexceptWrapper

    return noexcept


def nofail(func):

    @wraps(func)
    def nofailWrapper(*args, **kwArgs):
        try:
            return func(*args, **kwArgs)
        except:
            LOG_CURRENT_EXCEPTION()
            CRITICAL_ERROR('Exception in no-fail code')

    return nofailWrapper


def exposedtoclient(func):

    @wraps(func)
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
            LOG_CURRENT_EXCEPTION()

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

        def wrapper(*args, **kwargs):
            attribute = getattr(args[0], attributeName)
            if not bool(attribute):
                if logFunc:
                    logFunc('Method condition failed', func, args, kwargs, stack=logStack)
                return
            return func(*args, **kwargs)

        return decorate(func, wrapper)

    return decorator


def limitExposedToClientCalls(cooldown=SERVER_TICK_LENGTH - 0.01, periodLength=1.0, errorThreshold=1, storageAttr='__exposedCallsStorage__'):
    if IS_DEVELOPMENT:
        if not (IS_BASEAPP or IS_CELLAPP) or cooldown <= 0 or periodLength <= cooldown or errorThreshold < 1:
            raise SoftException('Invalid parameters for limitExposedToClientCalls decorator: cooldown=%.4f, periodLength=%.2f, errorThreshold=%d, isBase=%s, isCell=%s' % (cooldown,
             periodLength,
             errorThreshold,
             IS_BASEAPP,
             IS_CELLAPP))
    DROP_COUNT, PERIOD_START, LAST_CALL = (0, 1, 2)

    def _decorator(func):

        @wraps(func)
        def _wrapper(*args, **kwargs):
            self = args[0]
            now = time.time()
            key = (args[1], func.__name__) if IS_CELLAPP else func.__name__
            storage = getattr(self, storageAttr, None)
            if storage is None:
                storage = {}
                setattr(self, storageAttr, storage)
            stats = storage.get(key)
            if stats is None:
                stats = [0, now, 0.0]
                storage[key] = stats
            if now - stats[PERIOD_START] >= periodLength:
                stats[DROP_COUNT] = 0
                stats[PERIOD_START] = now
            if now - stats[LAST_CALL] < cooldown:
                stats[DROP_COUNT] += 1
                if stats[DROP_COUNT] == errorThreshold:
                    logger.error('%s | %s | %d calls were dropped in the last %.4f seconds | cooldown=%.4f, periodLength=%.2f, errorThreshold=%d', self.__class__.__name__, key, stats[DROP_COUNT], now - stats[PERIOD_START], cooldown, periodLength, errorThreshold)
            else:
                stats[LAST_CALL] = now
                return func(*args, **kwargs)
            return

        return _wrapper

    return _decorator
