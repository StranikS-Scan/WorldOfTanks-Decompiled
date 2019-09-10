# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/waiting_worker.py
import logging
import typing
import BigWorld
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.common.waiting_transitions import WaitingTransition, TransitionMode
from gui.app_loader.settings import APP_NAME_SPACE
from gui.impl.gen import R
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from shared_utils import findFirst
from skeletons.gui.app_loader import IWaitingWidget, IAppFactory, IWaitingWorker
_logger = logging.getLogger(__name__)

class _WaitingTask(object):
    __slots__ = ('__messageID', '__isBlocking', '__interruptCallbacks')

    def __init__(self, messageID, interruptCallback=None, isBlocking=True):
        super(_WaitingTask, self).__init__()
        self.__messageID = messageID
        self.__isBlocking = isBlocking
        if interruptCallback is not None:
            self.__interruptCallbacks = [interruptCallback]
        else:
            self.__interruptCallbacks = []
        return

    def __repr__(self):
        return '_WaitingTask({}): message={}, interruptCallbacks={}, isBlocking={}'.format(id(self), self.__messageID, self.__interruptCallbacks, self.__isBlocking)

    @property
    def messageID(self):
        return self.__messageID

    @property
    def isBlocking(self):
        return self.__isBlocking

    @isBlocking.setter
    def isBlocking(self, flag):
        self.__isBlocking = flag

    def clear(self):
        del self.__interruptCallbacks[:]

    def addInterruptCallback(self, interruptCallback):
        if interruptCallback is not None and interruptCallback not in self.__interruptCallbacks:
            self.__interruptCallbacks.append(interruptCallback)
        return

    def interrupt(self):
        for callback in self.__interruptCallbacks:
            callback()

        self.clear()


class WaitingWorker(IWaitingWorker):
    __slots__ = ('__appFactory', '__blocking', '__nonBlocking', '__waitingStack', '__suspendStack', '__isShown', '__transition', '__transitionMessageID')

    def __init__(self):
        super(WaitingWorker, self).__init__()
        self.__appFactory = None
        self.__blocking = None
        self.__nonBlocking = None
        self.__waitingStack = []
        self.__suspendStack = []
        self.__isShown = False
        self.__transition = None
        self.__transitionMessageID = R.invalid()
        return

    def start(self, appFactory):
        self.__appFactory = appFactory
        self.__transition = WaitingTransition()
        add = g_eventBus.addListener
        appEvent = events.AppLifeCycleEvent
        add(appEvent.INITIALIZED, self.__onAppInitialized)
        add(appEvent.DESTROYED, self.__onAppDestroyed)

    def stop(self):
        remove = g_eventBus.removeListener
        appEvent = events.AppLifeCycleEvent
        remove(appEvent.INITIALIZED, self.__onAppInitialized)
        remove(appEvent.DESTROYED, self.__onAppDestroyed)
        if self.__transition is not None:
            self.__transition.close()
            self.__transition = None
        if self.__appFactory is not None:
            lobby = self.__appFactory.getApp(APP_NAME_SPACE.SF_LOBBY)
            if lobby is not None and lobby.loaderManager is not None:
                lobby.loaderManager.onViewLoaded += self.__onViewLoaded
            self.__appFactory = None
        if self.__nonBlocking is not None:
            self.__nonBlocking.onDispose -= self.__onNonBlockingWaitingDisposed
            self.__nonBlocking = None
        if self.__blocking is not None:
            self.__blocking.onDispose -= self.__onBlockingWaitingDisposed
            self.__blocking = None
        if self.__blocking is not None:
            self.__blocking.destroy()
            self.__blocking = None
        del self.__waitingStack[:]
        del self.__suspendStack[:]
        self.__isShown = False
        return

    def getWaitingView(self, isBlocking):
        if self.__transition.isInTransitionMode():
            return self.__transition
        return self.__blocking if isBlocking else self.__nonBlocking

    def isWaitingShown(self, messageID=None):
        return self.__isShown if messageID is None else self.getWaitingTask(messageID) is not None

    def getWaitingTask(self, messageID):
        return findFirst(lambda task: task.messageID == messageID, self.__waitingStack)

    def getSuspendedWaitingTask(self, messageID):
        return findFirst(lambda task: task.messageID == messageID, self.__suspendStack)

    def show(self, messageID, isSingle=False, interruptCallback=None, isBlocking=True):
        BigWorld.Screener.setEnabled(False)
        task = self.getWaitingTask(messageID)
        if task is not None:
            if isSingle:
                task.addInterruptCallback(interruptCallback)
            else:
                task = self._addToStack(messageID, interruptCallback, isBlocking)
        else:
            task = self._addToStack(messageID, interruptCallback, isBlocking)
        self._showWaiting(task)
        return

    def hide(self, messageID):
        task = self.getSuspendedWaitingTask(messageID)
        if task is not None:
            task.clear()
            view = self.getWaitingView(task.isBlocking)
            if view is not None:
                view.hideWaiting()
            self.__suspendStack.remove(task)
        task = self.getWaitingTask(messageID)
        if task is not None:
            task.clear()
            view = self.getWaitingView(task.isBlocking)
            if view is not None:
                view.hideWaiting()
            self.__waitingStack.remove(task)
        if self.__waitingStack:
            self._showWaiting(self.__waitingStack[-1])
        else:
            self.close()
        return

    def suspend(self):
        if self.isSuspended():
            return
        self.__suspendStack = self.__waitingStack[:]
        self.close()

    def resume(self):
        if not self.isSuspended():
            return
        if self.__suspendStack:
            self._showWaiting(self.__suspendStack[-1])
            self.__waitingStack += self.__suspendStack[:]
        del self.__suspendStack[:]

    def isSuspended(self):
        return len(self.__suspendStack) > 0

    def close(self):
        BigWorld.Screener.setEnabled(True)
        self.__isShown = False
        for task in self.__waitingStack:
            task.clear()
            view = self.getWaitingView(task.isBlocking)
            if view:
                view.hideWaiting()

        del self.__waitingStack[:]

    def rollback(self):
        for task in self.__suspendStack:
            task.clear()

        del self.__suspendStack[:]
        self.close()

    def cancelCallback(self):
        view = self.getWaitingView(True)
        if view is not None:
            view.setCallback(None)
        return

    def snapshort(self):
        return {'waiting': self.__waitingStack[:],
         'suspend': self.__suspendStack[:]}

    def _hasBlockingWaiting(self):
        found = findFirst(lambda task: task.isBlocking, self.__waitingStack)
        return found is not None or self.__transition.isInTransitionMode()

    def _addToStack(self, message, interruptCallback, isBlocking):
        isBlocking = isBlocking or self._hasBlockingWaiting()
        self.__waitingStack.append(_WaitingTask(message, interruptCallback, isBlocking))
        return self.__waitingStack[-1]

    def _showWaiting(self, task):
        view = self.getWaitingView(task.isBlocking)
        if view is None and not task.isBlocking:
            view = self.getWaitingView(True)
            if view is not None:
                task.isBlocking = True
        if view is not None:
            view.showWaiting(task.messageID)
            self.__isShown = True
            if task.isBlocking:
                view.setCallback(task.interrupt)
                g_eventBus.handleEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.WAITING_SHOWN), scope=EVENT_BUS_SCOPE.LOBBY)
        return

    def __closeTransitionInLobby(self, nonBlocking, blocking):
        if nonBlocking is not None and blocking is not None:
            self.__swtichTransitionToTriggerMode()
        return

    def __swtichTransitionToTriggerMode(self):
        if self.__transition.isInTransitionMode():
            self.__transition.setTransitionMode(TransitionMode.TRIGGER)
        self.hide(self.__transitionMessageID)
        self.__transitionMessageID = R.invalid()

    def __onAppInitialized(self, event):
        if event.ns == APP_NAME_SPACE.SF_LOBBY:
            lobby = self.__appFactory.getApp(APP_NAME_SPACE.SF_LOBBY)
            lobby.loaderManager.onViewLoaded += self.__onViewLoaded
        if event.ns == APP_NAME_SPACE.SF_BATTLE:
            self.close()
            self.__transition.setTransitionMode(TransitionMode.DISABLED)
            self.__transitionMessageID = R.invalid()

    def __onAppDestroyed(self, event):
        if event.ns == APP_NAME_SPACE.SF_LOBBY:
            self.__transition.setTransitionMode(TransitionMode.ENABLED)
            self.__transitionMessageID = R.strings.waiting.loadPage()
            self.show(self.__transitionMessageID)
        elif event.ns == APP_NAME_SPACE.SF_BATTLE:
            self.__transition.setTransitionMode(TransitionMode.ENABLED | TransitionMode.SHOW_BACKGROUND | TransitionMode.PERMANENT_MESSAGE)
            self.__transitionMessageID = R.strings.waiting.exit_battle()
            self.show(self.__transitionMessageID)

    def __onViewLoaded(self, pyView, _):
        alias = pyView.alias
        if alias == VIEW_ALIAS.LOBBY:
            if not isinstance(pyView, IWaitingWidget):
                _logger.error('Non blocking waiting is not available. View does not inherit IWaitingComponent: %r', pyView)
                return
            self.__closeTransitionInLobby(pyView, self.__blocking)
            self.__nonBlocking = pyView
            self.__nonBlocking.onDispose += self.__onNonBlockingWaitingDisposed
        elif alias == VIEW_ALIAS.WAITING:
            if not isinstance(pyView, IWaitingWidget):
                _logger.error('Blocking waiting is not available. View does not inherit IWaitingComponent: %r', pyView)
                return
            self.__closeTransitionInLobby(self.__nonBlocking, pyView)
            self.__blocking = pyView
            self.__blocking.onDispose += self.__onBlockingWaitingDisposed
        elif alias == VIEW_ALIAS.LOGIN:
            self.__swtichTransitionToTriggerMode()

    def __onNonBlockingWaitingDisposed(self, pyEntity):
        pyEntity.onDispose -= self.__onNonBlockingWaitingDisposed
        self.__nonBlocking = None
        return

    def __onBlockingWaitingDisposed(self, pyEntity):
        pyEntity.onDispose -= self.__onBlockingWaitingDisposed
        self.__blocking = None
        return
