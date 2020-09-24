# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/pub/notification_window_controller.py
import logging
import typing
import BigWorld
import Event
from PlayerEvents import g_playerEvents
from bootcamp.BootCampEvents import g_bootcampEvents
from frameworks.wulf import WindowStatus, WindowLayer
from gui.Scaleform.framework.entities.sf_window import SFWindow
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import LobbySimpleEvent
from helpers import dependency
from skeletons.gameplay import IGameplayLogic
from skeletons.gui.game_control import IBootcampController
from skeletons.gui.impl import IGuiLoader, INotificationWindowController
if typing.TYPE_CHECKING:
    from frameworks.wulf import Window
_logger = logging.getLogger(__name__)

class NotificationWindowController(INotificationWindowController, IGlobalListener):
    __slots__ = ('__accountID', '__activeQueue', '__postponedQueue', '__currentWindow', '__callbackID', '__isWaitingShown', '__processAfterWaiting', '__isInBootcamp', '__isLobbyLoaded')
    __gui = dependency.descriptor(IGuiLoader)
    __gameplay = dependency.descriptor(IGameplayLogic)
    __bootcamp = dependency.descriptor(IBootcampController)

    def __init__(self):
        super(NotificationWindowController, self).__init__()
        self.__activeQueue = []
        self.__postponedQueue = []
        self.__currentWindow = None
        self.__callbackID = None
        self.__isWaitingShown = False
        self.__processAfterWaiting = False
        self.__isLobbyLoaded = False
        self.__accountID = 0
        self.__isInBootcamp = False
        self.onPostponedQueueUpdated = Event.Event()
        return

    @property
    def postponedCount(self):
        return len(self.__postponedQueue)

    def init(self):
        self.__gui.windowsManager.onWindowStatusChanged += self.__onWindowStatusChanged
        g_eventBus.addListener(LobbySimpleEvent.WAITING_SHOWN, self.__showWaiting, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(LobbySimpleEvent.WAITING_HIDDEN, self.__hideWaiting, EVENT_BUS_SCOPE.LOBBY)
        g_bootcampEvents.onBootcampStarted += self.__onEnterBootcamp
        g_bootcampEvents.onBootcampFinished += self.__onExitBootcamp
        g_playerEvents.onAccountShowGUI += self.__onAccountShowGUI

    def fini(self):
        self.stopGlobalListening()
        self.clear()
        self.__gui.windowsManager.onWindowStatusChanged -= self.__onWindowStatusChanged
        g_eventBus.removeListener(LobbySimpleEvent.WAITING_SHOWN, self.__showWaiting, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(LobbySimpleEvent.WAITING_HIDDEN, self.__hideWaiting, EVENT_BUS_SCOPE.LOBBY)
        self.onPostponedQueueUpdated.clear()
        g_bootcampEvents.onBootcampStarted -= self.__onEnterBootcamp
        g_bootcampEvents.onBootcampFinished -= self.__onExitBootcamp
        g_playerEvents.onAccountShowGUI -= self.__onAccountShowGUI

    def __onAccountShowGUI(self, ctx):
        dbID = ctx['databaseID']
        if self.__accountID != dbID:
            self.__accountID = dbID
            self.clear()

    def onLobbyInited(self, event):
        self.startGlobalListening()
        self.__isLobbyLoaded = True
        self.__isInBootcamp = self.__bootcamp.isInBootcamp()
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
        for window in self.__activeQueue:
            window.destroy()

        for window in self.__postponedQueue:
            window.destroy()

        del self.__activeQueue[:]
        del self.__postponedQueue[:]

    def append(self, window):
        _logger.debug('Append %r', window)
        self.__removeWindowInstance(window)
        self.__activeQueue.append(window)
        if self.isEnabled():
            self.__processNext()
        elif self.__isLobbyLoaded:
            self.postponeActive()

    def releasePostponed(self):
        _logger.debug('Releasing the postponed queue.')
        if self.isEnabled():
            self.__activeQueue.extend(self.__postponedQueue)
            del self.__postponedQueue[:]
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
        return False if not self.__isLobbyLoaded or self.__isInBootcamp else not self.prbDispatcher.getFunctionalState().isNavigationDisabled()

    def hasWindow(self, window):
        return window == self.__currentWindow or window in self.__activeQueue or window in self.__postponedQueue

    def __onEnterBootcamp(self):
        self.__isInBootcamp = True
        self.__updateEnabled()
        self.__notifyWithPostponedQueueCount()

    def __onExitBootcamp(self):
        self.__isInBootcamp = False
        self.__updateEnabled()
        self.__notifyWithPostponedQueueCount()

    def __updateEnabled(self):
        if not self.isEnabled():
            self.postponeActive()
            self.__destroyCurrentWindow()
            self.__clearCallback()
            self.__processAfterWaiting = False

    def __notifyWithPostponedQueueCount(self):
        self.onPostponedQueueUpdated(self.postponedCount, self.__isInBootcamp)

    def __onWindowStatusChanged(self, uniqueID, newState):
        window = self.__gui.windowsManager.getWindow(uniqueID)
        if newState == WindowStatus.LOADING:
            self.__removeWindowInstance(window)
        elif newState == WindowStatus.DESTROYING:
            if self.__currentWindow == window:
                self.__currentWindow = None
        elif newState == WindowStatus.DESTROYED:
            self.__processNext()
        return

    def __processNext(self):
        self.__processAfterWaiting = True
        if self.__callbackID is None:
            self.__callbackID = BigWorld.callback(0, self.__processNextCallback)
        return

    def __processNextCallback(self):
        self.__callbackID = None
        if not self.__activeQueue or self.__isWaitingShown:
            return
        else:
            self.__processAfterWaiting = False
            if self.isEnabled() and not self.__gui.windowsManager.findWindows(self.__overlappingWindowsPredicate):
                nextWindow = self.__activeQueue.pop(0)
                _logger.debug('Loading next window: %r', nextWindow)
                self.__currentWindow = nextWindow
                nextWindow.load()
            return

    def __destroyCurrentWindow(self):
        if self.__currentWindow is not None:
            self.__currentWindow.destroy()
        return

    def __removeWindowInstance(self, window):
        if window in self.__activeQueue:
            self.__activeQueue.remove(window)
        if window in self.__postponedQueue:
            self.__postponedQueue.remove(window)

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
