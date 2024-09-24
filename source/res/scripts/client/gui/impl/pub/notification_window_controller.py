# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/pub/notification_window_controller.py
import logging
import types
import typing
import BigWorld
import Event
from PlayerEvents import g_playerEvents
from frameworks.wulf import WindowStatus, WindowLayer
from gui.impl.pub.notification_commands import WindowNotificationCommand
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import LobbySimpleEvent
from helpers import dependency
from skeletons.gameplay import IGameplayLogic
from skeletons.gui.impl import IGuiLoader, INotificationWindowController
if typing.TYPE_CHECKING:
    from frameworks.wulf import Window
    from gui.impl.pub.notification_commands import NotificationCommand
_logger = logging.getLogger(__name__)

class NotificationWindowController(INotificationWindowController, IGlobalListener):
    __slots__ = ('__accountID', '__activeQueue', '__postponedQueue', '__currentWindow', '__callbackID', '__isWaitingShown', '__processAfterWaiting', '__isLobbyLoaded', '__locks', '__isExecuting', '__predicate')
    __gui = dependency.descriptor(IGuiLoader)
    __gameplay = dependency.descriptor(IGameplayLogic)

    def __init__(self):
        super(NotificationWindowController, self).__init__()
        self.__activeQueue = []
        self.__postponedQueue = []
        self.__locks = set()
        self.__currentWindow = None
        self.__predicate = None
        self.__callbackID = None
        self.__isWaitingShown = False
        self.__processAfterWaiting = False
        self.__isLobbyLoaded = False
        self.__accountID = 0
        self.__isExecuting = False
        self.onPostponedQueueUpdated = Event.Event()
        return

    @property
    def postponedCount(self):
        return len(self.__postponedQueue)

    @property
    def activeQueueLength(self):
        return len(self.__activeQueue)

    def init(self):
        self.__gui.windowsManager.onWindowStatusChanged += self.__onWindowStatusChanged
        g_eventBus.addListener(LobbySimpleEvent.WAITING_SHOWN, self.__showWaiting, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(LobbySimpleEvent.WAITING_HIDDEN, self.__hideWaiting, EVENT_BUS_SCOPE.LOBBY)
        g_playerEvents.onAccountShowGUI += self.__onAccountShowGUI

    def fini(self):
        self.stopGlobalListening()
        self.clear()
        self.__gui.windowsManager.onWindowStatusChanged -= self.__onWindowStatusChanged
        g_eventBus.removeListener(LobbySimpleEvent.WAITING_SHOWN, self.__showWaiting, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(LobbySimpleEvent.WAITING_HIDDEN, self.__hideWaiting, EVENT_BUS_SCOPE.LOBBY)
        self.onPostponedQueueUpdated.clear()
        g_playerEvents.onAccountShowGUI -= self.__onAccountShowGUI

    def __onAccountShowGUI(self, ctx):
        dbID = ctx['databaseID']
        if self.__accountID != dbID:
            self.__accountID = dbID
            self.clear()

    def onLobbyInited(self, event):
        self.startGlobalListening()
        self.__isLobbyLoaded = True
        self.__updateEnabled()
        self.__notifyWithPostponedQueueCount()
        if self.isEnabled():
            self.__processNext()

    def onAvatarBecomePlayer(self):
        self.__isLobbyLoaded = False
        self.stopGlobalListening()
        self.__updateEnabled()

    def onDisconnected(self):
        self.__isLobbyLoaded = False
        self.stopGlobalListening()
        self.__updateEnabled()
        self.__activeQueue = self.__discardNonPersistentCommands(self.__activeQueue)
        self.__postponedQueue = self.__discardNonPersistentCommands(self.__postponedQueue)

    def onPrbEntitySwitched(self):
        self.__updateEnabled()

    def onEnqueued(self, queueType, *args):
        self.__updateEnabled()

    def onDequeued(self, queueType, *args):
        self.__updateEnabled()

    def onPlayerStateChanged(self, *args):
        self.__updateEnabled()

    def onUnitFlagsChanged(self, *args):
        self.__updateEnabled()

    def clear(self):
        _logger.debug('Clear queues.')
        self.__clearCallback()
        self.__processAfterWaiting = False
        for command in self.__activeQueue:
            command.fini()

        for command in self.__postponedQueue:
            command.fini()

        del self.__activeQueue[:]
        del self.__postponedQueue[:]
        self.__locks.clear()
        self.__predicate = None
        return

    def append(self, command):
        if self.__predicate is None or self.__predicate(command):
            _logger.debug('Append %r', command)
            command.init()
            self.__removeSameInstance(command)
            self.__activeQueue.append(command)
            self.__tryProcess()
        return

    def releasePostponed(self, fireReleased=True):
        _logger.debug('Releasing the postponed queue.')
        if self.isEnabled():
            self.__activeQueue.extend(self.__postponedQueue)
            del self.__postponedQueue[:]
            if fireReleased:
                self.__destroyCurrentWindow()
                self.__processNext()
            self.__notifyWithPostponedQueueCount()
        else:
            _logger.error('Queue is currently disabled.')

    def postponeActive(self):
        _logger.debug('Postpone the active queue.')
        self.__clearCallback()
        if not self.__activeQueue:
            return
        self.__postponedQueue.extend(self.__activeQueue)
        del self.__activeQueue[:]
        self.__notifyWithPostponedQueueCount()

    def isEnabled(self):
        return False if not self.__isLobbyLoaded or self.prbDispatcher is None else not self.prbDispatcher.getFunctionalState().isNavigationDisabled()

    def isExecuting(self):
        return self.__isExecuting

    def hasWindow(self, window):
        command = WindowNotificationCommand(window)
        return window == self.__currentWindow or command in self.__activeQueue or command in self.__postponedQueue

    def lock(self, key):
        _logger.info('Notifications locked, key = %s', key)
        self.__locks.add(key)

    def unlock(self, key):
        _logger.info('Notifications unlocked, key = %s', key)
        self.__locks.remove(key)
        self.__tryProcess()

    def hasLock(self, key):
        return key in self.__locks

    def setFilterPredicate(self, predicate):
        self.__predicate = predicate

    def getFilterPredicate(self):
        return self.__predicate

    @staticmethod
    def __discardNonPersistentCommands(queue):
        result = []
        for cmd in queue:
            if cmd.isPersistent:
                result.append(cmd)
            _logger.debug('Throwing away non-persistent notification command: %s', cmd)
            cmd.fini()

        return result

    def __tryProcess(self):
        if not self.__locks:
            if self.isEnabled():
                self.__processNext()
            elif self.__isLobbyLoaded:
                self.postponeActive()

    def __updateEnabled(self):
        if not self.isEnabled() and not self.__locks:
            self.postponeActive()
            self.__destroyCurrentWindow()
            self.__clearCallback()
            self.__processAfterWaiting = False

    def __notifyWithPostponedQueueCount(self):
        self.onPostponedQueueUpdated(self.postponedCount)

    def __onWindowStatusChanged(self, uniqueID, newState):
        window = self.__gui.windowsManager.getWindow(uniqueID)
        if newState in (WindowStatus.LOADING, WindowStatus.DESTROYING):
            self.__removeSameInstance(WindowNotificationCommand(window))
        if newState == WindowStatus.DESTROYING and self.__currentWindow == window:
            self.__currentWindow = None
        elif newState == WindowStatus.DESTROYED:
            self.__processNext()
        return

    def __processNext(self):
        self.__processAfterWaiting = True
        if self.__callbackID is None and self.__activeQueue and not self.__isWaitingShown and not self.__locks:
            self.__callbackID = BigWorld.callback(0, self.__processNextCallback)
        return

    def __processNextCallback(self):
        self.__callbackID = None
        if not self.__activeQueue or self.__isWaitingShown:
            return
        else:
            self.__processAfterWaiting = False
            if self.isEnabled() and not self.__locks and not self.__gui.windowsManager.findWindows(self.__overlappingWindowsPredicate):
                command = self.__activeQueue.pop(0)
                _logger.debug('Executing next command: %r', command)
                self.__currentWindow = command.getWindow()
                self.__isExecuting = True
                command.execute()
                self.__isExecuting = False
            return

    def __destroyCurrentWindow(self):
        if self.__currentWindow is not None:
            self.__currentWindow.destroy()
        return

    def __removeSameInstance(self, command):
        if command in self.__activeQueue:
            self.__activeQueue.remove(command)
        if command in self.__postponedQueue:
            self.__postponedQueue.remove(command)

    def __showWaiting(self, _):
        self.__isWaitingShown = True
        self.__clearCallback()

    def __hideWaiting(self, _):
        self.__isWaitingShown = False
        if self.__processAfterWaiting:
            self.__processNext()

    def __clearCallback(self):
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
        return

    @staticmethod
    def __overlappingWindowsPredicate(window):
        return window.windowStatus in (WindowStatus.LOADING, WindowStatus.LOADED) and window.layer in (WindowLayer.OVERLAY, WindowLayer.TOP_WINDOW, WindowLayer.FULLSCREEN_WINDOW)
