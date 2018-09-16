# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/Waiting.py
import BigWorld
from helpers import i18n

class _WaitingEntity(object):

    def __init__(self, message, interruptCallback=None):
        super(_WaitingEntity, self).__init__()
        self.__message = message
        if interruptCallback is not None:
            self.__interruptCallbacks = [interruptCallback]
        else:
            self.__interruptCallbacks = []
        return

    def __repr__(self):
        return '{}: message={}, interruptCallbacks={}'.format(super(_WaitingEntity, self).__repr__(), self.__message, self.__interruptCallbacks)

    @property
    def message(self):
        return self.__message

    def clear(self):
        self.__interruptCallbacks = []

    def addInterruptCallback(self, interruptCallback):
        if interruptCallback is not None and interruptCallback not in self.__interruptCallbacks:
            self.__interruptCallbacks.append(interruptCallback)
        return

    def interrupt(self):
        for c in self.__interruptCallbacks:
            c()

        self.clear()


class Waiting(object):
    __wainingViewGetter = None
    __waitingStack = []
    __suspendStack = []
    __isVisible = False

    @classmethod
    def setWainingViewGetter(cls, getter):
        cls.__wainingViewGetter = getter

    @classmethod
    def getWaitingView(cls):
        view = None
        if callable(cls.__wainingViewGetter):
            view = cls.__wainingViewGetter()
        return view

    @classmethod
    def isVisible(cls):
        return cls.__isVisible

    @classmethod
    def isOpened(cls, msg):
        return cls.getWaiting(msg) is not None

    @classmethod
    def getWaiting(cls, msg):
        for w in cls.__waitingStack:
            if w.message == msg:
                return w

        return None

    @classmethod
    def getSuspendedWaiting(cls, msg):
        for w in cls.__suspendStack:
            if w.message == msg:
                return w

        return None

    @classmethod
    def show(cls, message, isSingle=False, interruptCallback=None):
        BigWorld.Screener.setEnabled(False)
        w = cls.getWaiting(message)
        if w is not None:
            if isSingle:
                w.addInterruptCallback(interruptCallback)
            else:
                w = _WaitingEntity(message, interruptCallback)
                Waiting.__waitingStack.append(w)
        else:
            w = _WaitingEntity(message, interruptCallback)
            Waiting.__waitingStack.append(w)
        Waiting._showWaiting(w)
        return

    @classmethod
    def hide(cls, message):
        w = Waiting.getSuspendedWaiting(message)
        if w is not None:
            w.clear()
            Waiting.__suspendStack.remove(w)
        w = Waiting.getWaiting(message)
        if w is not None:
            w.clear()
            Waiting.__waitingStack.remove(w)
        if Waiting.__waitingStack:
            Waiting._showWaiting(Waiting.__waitingStack[-1])
        else:
            Waiting.close()
        return

    @classmethod
    def suspend(cls):
        if Waiting.isSuspended():
            return
        Waiting.__suspendStack = Waiting.__waitingStack[:]
        Waiting.close()

    @classmethod
    def resume(cls):
        if not Waiting.isSuspended():
            return
        for w in Waiting.__suspendStack:
            Waiting._showWaiting(w)

        Waiting.__suspendStack = []

    @classmethod
    def isSuspended(cls):
        return len(Waiting.__suspendStack) > 0

    @classmethod
    def close(cls):
        BigWorld.Screener.setEnabled(True)
        view = Waiting.getWaitingView()
        if view:
            view.close()
        Waiting.__isVisible = False
        for w in Waiting.__waitingStack:
            w.clear()

        Waiting.__waitingStack = []

    @classmethod
    def rollback(cls):
        for w in Waiting.__suspendStack:
            w.clear()

        Waiting.__suspendStack = []
        Waiting.close()

    @classmethod
    def cancelCallback(cls):
        view = Waiting.getWaitingView()
        if view is not None:
            view.cancelCallback()
        return

    @classmethod
    def _showWaiting(cls, waiting):
        view = Waiting.getWaitingView()
        if view is not None:
            view.showS(i18n.makeString('#waiting:%s' % waiting.message))
            Waiting.__isVisible = True
            view.setCallback(waiting.interrupt)
            from gui.shared.events import LobbySimpleEvent
            from gui.shared import EVENT_BUS_SCOPE
            view.fireEvent(LobbySimpleEvent(LobbySimpleEvent.WAITING_SHOWN), scope=EVENT_BUS_SCOPE.LOBBY)
        return
