# Embedded file name: scripts/client/gui/shared/utils/MethodsRules.py
from collections import defaultdict
from types import MethodType
from debug_utils import LOG_DEBUG

class MethodsRules(object):
    __slots__ = ('__listenersToSkip', '__notificationToDelay', '__delayersProcessed')

    class skipable(object):

        def __init__(self, func):
            self.__listerner = func

        def __call__(self, *args, **kwargs):
            instance = args[0]
            if not isinstance(instance, MethodsRules):
                raise AssertionError('Wrong inheritance.')
                instance.skip(self.__listerner) and LOG_DEBUG('Notification skipped: ', instance, self.__listerner)
                return
            self.__listerner(*args, **kwargs)

        def __get__(self, obj, objtype = None):
            return MethodType(self, obj, objtype)

    class delayable(object):

        def __init__(self, delayerName = None):
            self.__delayerName = delayerName

        def __call__(self, listener):

            def wrapper(*args, **kwargs):
                instance = args[0]
                if not isinstance(instance, MethodsRules):
                    raise AssertionError('Wrong inheritance.')
                    instance.delay(self.__delayerName, listener, *args, **kwargs) and LOG_DEBUG('Notification delayed: ', listener, *args, **kwargs)
                    return
                result = listener(*args, **kwargs)
                instance.processDelayer(listener.__name__)
                return result

            return wrapper

        def __get__(self, obj, objtype = None):
            return MethodType(self, obj, objtype)

    def __init__(self):
        super(MethodsRules, self).__init__()
        self.__listenersToSkip = []
        self.__notificationToDelay = defaultdict(list)
        self.__delayersProcessed = set()

    def clear(self):
        self.__listenersToSkip = []
        self.__notificationToDelay.clear()
        self.__delayersProcessed.clear()

    def skipListenerNotification(self, wrapper):
        self.__listenersToSkip.append(wrapper.listener)

    def isSkipable(self, listener):
        return listener in self.__listenersToSkip

    def isDelayerProcessed(self, delayerName):
        return delayerName in self.__delayersProcessed

    def skip(self, listener):
        if self.isSkipable(listener):
            self.__listenersToSkip.remove(listener)
            return True
        return False

    def delay(self, delayerName, notification, *args, **kwargs):
        if delayerName is not None and not self.isDelayerProcessed(delayerName):
            self.__notificationToDelay[delayerName].append((notification, args, kwargs))
            return True
        else:
            return False

    def processDelayer(self, delayerName):
        LOG_DEBUG('Delayer processed: ', delayerName)
        self.__delayersProcessed.add(delayerName)
        pending = self.__notificationToDelay.pop(delayerName, ())
        delayers = set()
        for notification, args, kwargs in pending:
            LOG_DEBUG('Notification processed: ', notification, args, kwargs)
            notification(*args, **kwargs)
            delayers.add(notification.__name__)

        for delayerName in delayers:
            self.processDelayer(delayerName)
