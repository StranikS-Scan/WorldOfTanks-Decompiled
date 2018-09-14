# Embedded file name: scripts/client/gui/Scaleform/Waiting.py
import BigWorld
from helpers import i18n

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
        return msg in cls.__waitingStack

    @staticmethod
    def show(message, isSingle = False, interruptCallback = lambda : None):
        BigWorld.Screener.setEnabled(False)
        if not (isSingle and message in Waiting.__waitingStack):
            Waiting.__waitingStack.append(message)
        view = Waiting.getWaitingView()
        if view is not None:
            view.showS(i18n.makeString('#waiting:%s' % message))
            Waiting.__isVisible = True
            view.setCallback(interruptCallback)
            from gui.shared.events import LobbySimpleEvent
            from gui.shared import EVENT_BUS_SCOPE
            view.fireEvent(LobbySimpleEvent(LobbySimpleEvent.WAITING_SHOWN), scope=EVENT_BUS_SCOPE.LOBBY)
        return

    @staticmethod
    def suspend():
        if Waiting.isSuspended():
            return
        Waiting.__suspendStack = list(Waiting.__waitingStack)
        Waiting.close()

    @staticmethod
    def resume():
        if not Waiting.isSuspended():
            return
        for id in Waiting.__suspendStack:
            Waiting.show(id)

        Waiting.__suspendStack = []

    @staticmethod
    def isSuspended():
        return len(Waiting.__suspendStack) > 0

    @staticmethod
    def hide(message):
        stack = Waiting.__suspendStack
        if message in stack:
            stack.remove(message)
        try:
            stack = Waiting.__waitingStack
            if message in stack:
                stack.remove(message)
        except:
            pass

        if len(Waiting.__waitingStack) == 0:
            Waiting.close()

    @staticmethod
    def close():
        BigWorld.Screener.setEnabled(True)
        view = Waiting.getWaitingView()
        if view:
            view.close()
        Waiting.__isVisible = False
        Waiting.__waitingStack = []

    @staticmethod
    def rollback():
        Waiting.__suspendStack = []
        Waiting.close()

    @staticmethod
    def cancelCallback():
        view = Waiting.getWaitingView()
        if view is not None:
            view.cancelCallback()
        return
