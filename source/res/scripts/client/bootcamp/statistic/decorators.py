# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/statistic/decorators.py
from functools import wraps
from .loggers import BootcampUILogger, BaseLogger, isSPAAttributeExists
__all__ = ('loggerTarget', 'loggerEntry', 'simpleLog', 'logOnMatch', 'logOnCondition')

def loggerTarget(logKey, loggerCls=BootcampUILogger):

    def configureLogging(cls):
        cls.__bases__ += (loggerCls,)
        cls.setLogKey(logKey)
        return cls

    return configureLogging


def loggerEntry(method):

    @wraps(method)
    def _impl(self, *methodArgs, **methodKwargs):
        if issubclass(self.__class__, BaseLogger):
            self.initLogger()
        return method(self, *methodArgs, **methodKwargs)

    _impl.__name__ = method.__name__
    return _impl


def simpleLog(action=None, resetTime=True, logOnce=False, argKey=None, argMap=None):

    def wrapper(method):

        @wraps(method)
        def _impl(self, *methodArgs, **methodKwargs):
            if issubclass(self.__class__, BaseLogger) and isSPAAttributeExists():
                parameter = methodKwargs.get(argKey, None) or next(iter(methodArgs), None)
                actionValue = action or parameter
                if argMap and actionValue in argMap:
                    actionValue = argMap[actionValue]
                self.logStatistic(action=actionValue, resetTime=resetTime, logOnce=logOnce)
            return method(self, *methodArgs, **methodKwargs)

        _impl.__name__ = method.__name__
        return _impl

    return wrapper


def logOnMatch(resetTime=True, logOnce=False, objProperty=None, matches=None):

    def wrapper(method):

        @wraps(method)
        def _impl(self, *method_args, **method_kwargs):
            if issubclass(self.__class__, BaseLogger) and isSPAAttributeExists():
                if objProperty and matches:
                    actionValue = getattr(self, objProperty)
                    if actionValue in matches:
                        self.logStatistic(action=matches[actionValue], resetTime=resetTime, logOnce=logOnce)
            return method(self, *method_args, **method_kwargs)

        _impl.__name__ = method.__name__
        return _impl

    return wrapper


def logOnCondition(action=None, resetTime=True, logOnce=False, instanceMethod=None, valueToCheck=None):

    def wrapper(method):

        @wraps(method)
        def _impl(self, *method_args, **method_kwargs):
            if issubclass(self.__class__, BaseLogger) and isSPAAttributeExists():
                if instanceMethod and valueToCheck is not None:
                    if getattr(self, instanceMethod)(valueToCheck):
                        self.logStatistic(action=action, resetTime=resetTime, logOnce=logOnce)
            return method(self, *method_args, **method_kwargs)

        _impl.__name__ = method.__name__
        return _impl

    return wrapper
