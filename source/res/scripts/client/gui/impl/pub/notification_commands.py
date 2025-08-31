# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/pub/notification_commands.py
import typing
from frameworks.wulf import WindowStatus
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.framework.entities.sf_window import SFWindow
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from th_async import th_await, th_async

class NotificationEvent(object):
    __slots__ = ('_args', '_kwargs', '_method')

    def __init__(self, method, *args, **kwargs):
        self._method = method
        self._args = args
        self._kwargs = kwargs

    def __call__(self):
        self._method(*self._args, **self._kwargs)

    def isEventSet(self):
        return self._method is not None and callable(self._method)


class NotificationCommand(object):
    __slots__ = ()

    def __eq__(self, other):
        return False

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError

    def execute(self):
        raise NotImplementedError

    def getWindow(self):
        raise NotImplementedError


class WindowNotificationCommand(NotificationCommand):
    __slots__ = ('__window',)

    def __init__(self, window):
        super(WindowNotificationCommand, self).__init__()
        self.__window = window

    def __eq__(self, other):
        return self.__window == other

    def init(self):
        pass

    def fini(self):
        self.__window.destroy()

    def execute(self):
        self.__window.load()

    def getWindow(self):
        return self.__window


class WindowNotificationWithWaitingCommand(NotificationCommand):
    __slots__ = ('__window', '__waitingMessage', '__timeout')

    def __init__(self, window, waitingMessage, timeout):
        super(WindowNotificationWithWaitingCommand, self).__init__()
        self.__window = window
        self.__waitingMessage = waitingMessage
        self.__timeout = timeout

    def __eq__(self, other):
        return self.__window == other

    def init(self):
        pass

    def fini(self):
        self.__window.destroy()

    @th_async
    def execute(self):
        Waiting.show(self.__waitingMessage)
        try:
            show = yield th_await(self.__window.waitData(self.__timeout))
        finally:
            Waiting.hide(self.__waitingMessage)

        if show:
            self.__window.load()

    def getWindow(self):
        return self.__window


class EventNotificationCommand(NotificationCommand):
    __slots__ = ('__event',)

    def __init__(self, event):
        super(EventNotificationCommand, self).__init__()
        self.__event = event

    def __eq__(self, other):
        return self.__event == other

    def init(self):
        pass

    def fini(self):
        pass

    def execute(self):
        self.__event()

    def getWindow(self):
        return None
