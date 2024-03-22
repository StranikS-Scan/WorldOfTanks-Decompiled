# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/pub/notification_commands.py
import typing
from frameworks.wulf import WindowStatus
from gui.Scaleform.framework.entities.sf_window import SFWindow
from gui.impl.pub.lobby_window import LobbyNotificationWindow

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
    isPersistent = True

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
        return False if not isinstance(other, WindowNotificationCommand) else self.__window == other.getWindow()

    def init(self):
        pass

    def fini(self):
        self.__window.destroy()

    def execute(self):
        self.__window.load()

    def getWindow(self):
        return self.__window


class EventNotificationCommand(NotificationCommand):
    __slots__ = ('__event',)

    def __init__(self, event):
        super(EventNotificationCommand, self).__init__()
        self.__event = event

    def __eq__(self, other):
        return False if not isinstance(other, EventNotificationCommand) else self.__event == other.getEvent()

    def init(self):
        pass

    def fini(self):
        pass

    def execute(self):
        self.__event()

    def getWindow(self):
        return None

    def getEvent(self):
        return self.__event


class NonPersistentEventNotificationCommand(EventNotificationCommand):
    __slots__ = ()
    isPersistent = False
