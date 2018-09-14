# Embedded file name: scripts/client/gui/shared/utils/scheduled_notifications.py
import operator
import BigWorld
from helpers import time_utils
from shared_utils import forEach, findFirst

class Notifiable(object):

    def __init__(self, *args, **kwargs):
        super(Notifiable, self).__init__()
        self.__notificators = []

    def addNotificator(self, notificator):
        self.__notificators.append(notificator)

    def addNotificators(self, *notificators):
        self.__notificators.extend(notificators)

    def startNotification(self):
        forEach(operator.methodcaller('startNotification'), self.__notificators)

    def stopNotification(self):
        forEach(operator.methodcaller('stopNotification'), self.__notificators)

    def clearNotification(self):
        self.stopNotification()
        forEach(operator.methodcaller('clear'), self.__notificators)
        self.__notificators = []


class _Notifier(object):

    def __init__(self, deltaFunc, updateFunc):
        self.__deltaFunc = deltaFunc
        self._updateFunc = updateFunc
        self._notificationCallbackID = None
        return

    def clear(self):
        self.__deltaFunc = None
        self._updateFunc = None
        return

    def startNotification(self):
        self.__cancelNotification()
        self.__processNotification()

    def stopNotification(self):
        self.__cancelNotification()

    def _getNextNotificationDelta(self, delta):
        raise NotImplementedError

    def _registerCallback(self, nextNotification, notificationHandler):
        return BigWorld.callback(nextNotification, notificationHandler)

    def _cancelCallback(self):
        return BigWorld.cancelCallback(self._notificationCallbackID)

    def _onNotification(self):
        self._notificationCallbackID = None
        self._updateFunc()
        self.__processNotification()
        return

    def __processNotification(self):
        delta = self.__deltaFunc()
        if not delta:
            return
        nextNotification = self._getNextNotificationDelta(delta)
        if not nextNotification:
            return
        self._notificationCallbackID = self._registerCallback(nextNotification, self._onNotification)

    def __cancelNotification(self):
        if self._notificationCallbackID is not None:
            self._cancelCallback()
            self._notificationCallbackID = None
        return


class PeriodicNotifier(_Notifier):

    def __init__(self, deltaFunc, updateFunc, periods = None):
        super(PeriodicNotifier, self).__init__(deltaFunc, updateFunc)
        self.__periods = periods or (time_utils.ONE_DAY, time_utils.ONE_HOUR, time_utils.ONE_MINUTE)

    def _getNextNotificationDelta(self, delta):
        period = findFirst(lambda p: delta >= p, self.__periods, delta)
        return delta % period or period


class DeltaNotifier(_Notifier):

    def __init__(self, deltaFunc, updateFunc, delta):
        super(DeltaNotifier, self).__init__(deltaFunc, updateFunc)
        self.__delta = delta

    def _getNextNotificationDelta(self, delta):
        if delta >= self.__delta:
            return delta - self.__delta
        return 0


class SimpleNotifier(_Notifier):

    def _getNextNotificationDelta(self, delta):
        return delta


class AcyclicNotifier(SimpleNotifier):

    def _onNotification(self):
        self._notificationCallbackID = None
        self._updateFunc()
        return
