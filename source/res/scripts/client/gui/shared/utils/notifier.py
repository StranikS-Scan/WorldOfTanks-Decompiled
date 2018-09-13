# Embedded file name: scripts/client/gui/shared/utils/Notifier.py
from types import MethodType
from debug_utils import LOG_DEBUG, LOG_ERROR

class Notifier(object):

    class skipable(object):

        def __init__(self, func):
            self.__listerner = func

        def __call__(self, *args, **kwargs):
            instance = args[0]
            if instance.skip(self.__listerner):
                LOG_DEBUG('Notification skipped: ', instance, self.__listerner)
                return
            self.__listerner(*args, **kwargs)

        def __get__(self, obj, objtype = None):
            return MethodType(self, obj, objtype)

        @property
        def listener(self):
            return self.__listerner

    def __init__(self):
        self._listenersToSkip = []

    def skipListenerNotification(self, wrapper):
        self._listenersToSkip.append(wrapper.listener)

    def isSkipable(self, listener):
        return listener in self._listenersToSkip

    def skip(self, listener):
        if self.isSkipable(listener):
            self._listenersToSkip.remove(listener)
            return True
        return False
