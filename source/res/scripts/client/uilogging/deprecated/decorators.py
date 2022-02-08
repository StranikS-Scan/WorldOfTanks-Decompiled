# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/deprecated/decorators.py
from functools import wraps
from uilogging.deprecated.base.loggers import BaseLogger, isUILoggingEnabled
from uilogging.deprecated.logging_constants import KEYS_MAPPING
__all__ = ('loggerTarget', 'loggerEntry', 'simpleLog', 'logOnMatch', 'logOnCondition', 'settingsLog')

def loggerTarget(logKey, loggerCls):

    def configureLogging(cls):
        finalCls = cls
        if issubclass(cls, BaseLogger):
            finalCls = type(cls.__name__, tuple([ base for base in cls.__bases__ if not issubclass(base, BaseLogger) ]), dict(cls.__dict__))
        finalCls.__bases__ += (loggerCls,)
        finalCls.setLogKey(logKey)
        return finalCls

    return configureLogging


def loggerEntry(method):

    @wraps(method)
    def _impl(self, *methodArgs, **methodKwargs):
        if issubclass(self.__class__, BaseLogger):
            self.initLogger()
        return method(self, *methodArgs, **methodKwargs)

    _impl.__name__ = method.__name__
    return _impl


def simpleLog(action=None, resetTime=True, logOnce=False, kwargsKey=None, argsIndex=None, argMap=None, argMapSection=None, restrictions=None, validate=True, preProcessAction=lambda x: x):

    def wrapper(method):

        @wraps(method)
        def _impl(self, *methodArgs, **methodKwargs):
            if issubclass(self.__class__, BaseLogger) and isUILoggingEnabled(self.feature):
                parameter = None
                if argsIndex is not None:
                    parameter = methodArgs[argsIndex]
                if kwargsKey:
                    parameter = methodKwargs.get(kwargsKey, None)
                actionValue = action or parameter
                actionValue = preProcessAction(actionValue)
                valuesMap = argMap
                if argMapSection:
                    key = argMapSection() if callable(argMapSection) else argMapSection
                    valuesMap = argMap[key]
                if valuesMap:
                    if actionValue in valuesMap:
                        actionValue = valuesMap[actionValue]
                    else:
                        return method(self, *methodArgs, **methodKwargs)
                self.logStatistic(action=actionValue, resetTime=resetTime, logOnce=logOnce, restrictions=restrictions, validate=validate)
            return method(self, *methodArgs, **methodKwargs)

        _impl.__name__ = method.__name__
        return _impl

    return wrapper


def logOnMatch(resetTime=True, logOnce=False, objProperty=None, matches=None, matchesKey=None, restrictions=None, validate=True):

    def wrapper(method):

        @wraps(method)
        def _impl(self, *method_args, **method_kwargs):
            if issubclass(self.__class__, BaseLogger) and isUILoggingEnabled(self.feature):
                valuesMap = matches
                if matchesKey:
                    key = matchesKey() if callable(matchesKey) else matchesKey
                    valuesMap = matches[key]
                if objProperty and valuesMap:
                    actionValue = getattr(self, objProperty)
                    if actionValue in matches:
                        self.logStatistic(action=matches[actionValue], resetTime=resetTime, logOnce=logOnce, restrictions=restrictions, validate=validate)
            return method(self, *method_args, **method_kwargs)

        _impl.__name__ = method.__name__
        return _impl

    return wrapper


def logOnCondition(action=None, resetTime=True, logOnce=False, instanceMethod=None, valueToCheck=None, restrictions=None, validate=True):

    def wrapper(method):

        @wraps(method)
        def _impl(self, *method_args, **method_kwargs):
            if issubclass(self.__class__, BaseLogger) and isUILoggingEnabled(self.feature):
                if instanceMethod and valueToCheck is not None:
                    if getattr(self, instanceMethod)(valueToCheck):
                        self.logStatistic(action=action, resetTime=resetTime, logOnce=logOnce, restrictions=restrictions, validate=validate)
            return method(self, *method_args, **method_kwargs)

        _impl.__name__ = method.__name__
        return _impl

    return wrapper


def settingsLog(argsIndex, argMap, preProcessAction):

    def wrapper(method):

        @wraps(method)
        def _impl(self, *methodArgs, **methodKwargs):
            if issubclass(self.__class__, BaseLogger) and isUILoggingEnabled(self.feature):
                parameter = methodArgs[argsIndex]
                setting = preProcessAction(parameter)
                try:
                    name, value = setting.items()[0]
                except AttributeError:
                    return method(self, *methodArgs, **methodKwargs)

                if name not in argMap:
                    return method(self, *methodArgs, **methodKwargs)
                self.logStatistic(action=name, resetTime=False, logOnce=False, restrictions=None, validate=False, action_value=KEYS_MAPPING.get(value, value))
            return method(self, *methodArgs, **methodKwargs)

        _impl.__name__ = method.__name__
        return _impl

    return wrapper
