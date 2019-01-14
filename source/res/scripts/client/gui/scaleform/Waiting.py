# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/Waiting.py
import BigWorld
from helpers import i18n

class _WaitingEntity(object):

    def __init__(self, message, interruptCallback=None, overlapsUI=True):
        super(_WaitingEntity, self).__init__()
        self.__message = message
        self.__overlapsUI = overlapsUI
        if interruptCallback is not None:
            self.__interruptCallbacks = [interruptCallback]
        else:
            self.__interruptCallbacks = []
        return

    def __repr__(self):
        return '{}: message={}, interruptCallbacks={}, isOnTop={}'.format(super(_WaitingEntity, self).__repr__(), self.__message, self.__interruptCallbacks, self.__overlapsUI)

    @property
    def overlapsUI(self):
        return self.__overlapsUI

    @property
    def message(self):
        return self.__message

    def updateOverlapsUI(self, overlapsUI):
        self.__overlapsUI = overlapsUI

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
    __waitingViewGetter = None
    __lobbyPageWaitingKeeper = None
    __waitingStack = []
    __suspendStack = []
    __isVisible = False

    @classmethod
    def setWaitingViewGetter(cls, getter):
        cls.__waitingViewGetter = getter

    @classmethod
    def setLobbyPageWaitingKeeper(cls, waitingKeeper):
        cls.__lobbyPageWaitingKeeper = waitingKeeper

    @classmethod
    def getWaitingView(cls, overlapsUI):
        view = None
        if overlapsUI:
            if callable(cls.__waitingViewGetter):
                view = cls.__waitingViewGetter()
        elif cls.__lobbyPageWaitingKeeper is not None:
            view = cls.__lobbyPageWaitingKeeper
        return view

    @classmethod
    def isVisible(cls):
        return cls.__isVisible

    @classmethod
    def isOpened(cls, msg):
        return cls.getWaiting(msg) is not None

    @classmethod
    def _hasOverlapsUIWaiting(cls):
        for w in cls.__waitingStack:
            if w.overlapsUI:
                return True

        return False

    @classmethod
    def _addToStack(cls, message, interruptCallback, overlapsUI):
        overlapsUI = overlapsUI or cls._hasOverlapsUIWaiting()
        w = _WaitingEntity(message, interruptCallback, overlapsUI)
        cls.__waitingStack.append(w)
        return w

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
    def show(cls, message, isSingle=False, interruptCallback=None, overlapsUI=True):
        BigWorld.Screener.setEnabled(False)
        w = cls.getWaiting(message)
        if w is not None:
            if isSingle:
                w.addInterruptCallback(interruptCallback)
            else:
                w = cls._addToStack(message, interruptCallback, overlapsUI)
        else:
            w = cls._addToStack(message, interruptCallback, overlapsUI)
        cls._showWaiting(w)
        return

    @classmethod
    def hide(cls, message):
        w = cls.getSuspendedWaiting(message)
        if w is not None:
            w.clear()
            view = cls.getWaitingView(w.overlapsUI)
            if view:
                view.waitingHide()
            cls.__suspendStack.remove(w)
        w = cls.getWaiting(message)
        if w is not None:
            w.clear()
            view = cls.getWaitingView(w.overlapsUI)
            if view:
                view.waitingHide()
            cls.__waitingStack.remove(w)
        if cls.__waitingStack:
            cls._showWaiting(cls.__waitingStack[-1])
        else:
            cls.close()
        return

    @classmethod
    def suspend(cls):
        if cls.isSuspended():
            return
        cls.__suspendStack = cls.__waitingStack[:]
        cls.close()

    @classmethod
    def resume(cls):
        if not cls.isSuspended():
            return
        if cls.__suspendStack:
            cls._showWaiting(cls.__suspendStack[-1])
            cls.__waitingStack = cls.__suspendStack[:]
        cls.__suspendStack = []

    @classmethod
    def isSuspended(cls):
        return len(cls.__suspendStack) > 0

    @classmethod
    def close(cls):
        BigWorld.Screener.setEnabled(True)
        cls.__isVisible = False
        for w in cls.__waitingStack:
            w.clear()
            view = cls.getWaitingView(w.overlapsUI)
            if view:
                view.waitingHide()

        cls.__waitingStack = []

    @classmethod
    def rollback(cls):
        for w in cls.__suspendStack:
            w.clear()

        cls.__suspendStack = []
        cls.close()

    @classmethod
    def cancelCallback(cls):
        view = cls.getWaitingView(True)
        if view is not None:
            view.cancelCallback()
        return

    @classmethod
    def _showWaiting(cls, w):
        view = cls.getWaitingView(w.overlapsUI)
        if view is None and w.overlapsUI is False:
            view = cls.getWaitingView(True)
            if view is not None:
                w.updateOverlapsUI(True)
        if view is not None:
            view.waitingShow(i18n.makeString('#waiting:%s' % w.message))
            cls.__isVisible = True
            if w.overlapsUI:
                view.setCallback(w.interrupt)
                from gui.shared.events import LobbySimpleEvent
                from gui.shared import EVENT_BUS_SCOPE
                view.fireEvent(LobbySimpleEvent(LobbySimpleEvent.WAITING_SHOWN), scope=EVENT_BUS_SCOPE.LOBBY)
        return
