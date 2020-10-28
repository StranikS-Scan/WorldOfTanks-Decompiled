# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/game_event/award_window_controller.py
from weakref import proxy
import gui.shared
from constants import QUEUE_TYPE
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.app_loader import sf_lobby
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.shared.events import GUICommonEvent
from gui.shared.utils import isPopupsWindowsOpenDisabled
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from gui.prb_control.entities.listener import IGlobalListener

class GameEventAwardWindowController(CallbackDelayer, IGlobalListener):
    settingsCore = dependency.descriptor(ISettingsCore)
    eventsCache = dependency.descriptor(IEventsCache)
    itemsCache = dependency.descriptor(IItemsCache)
    _CALLBACK_SHOW_AWARD_WAIT_TIME = 2

    def __init__(self, gameEventController):
        super(GameEventAwardWindowController, self).__init__()
        self._lobbyInited = False
        self._inEventHangar = False
        self._gameEventController = proxy(gameEventController)

    @property
    def isInQueue(self):
        return self.prbEntity and self.prbEntity.isInQueue()

    def start(self):
        self._lobbyInited = False
        self._inEventHangar = False
        self._gameEventController.onProgressChanged += self._onProgressChanged
        self.eventsCache.onSyncCompleted += self._onProgressChanged
        gui.shared.g_eventBus.addListener(GUICommonEvent.LOBBY_VIEW_LOADED, self._onLobbyInited)

    def stop(self):
        self.clearCallbacks()
        self.stopGlobalListening()
        self._lobbyInited = False
        self._inEventHangar = False
        self._gameEventController.onProgressChanged -= self._onProgressChanged
        self.eventsCache.onSyncCompleted -= self._onProgressChanged
        gui.shared.g_eventBus.removeListener(GUICommonEvent.LOBBY_VIEW_LOADED, self._onLobbyInited)
        self.destroy()

    def _onLobbyInited(self, _):
        self.startGlobalListening()
        self._lobbyInited = True
        self.onPrbEntitySwitched()

    def onPrbEntitySwitched(self):
        self._inEventHangar = self.prbEntity.getQueueType() == QUEUE_TYPE.EVENT_BATTLES
        if self._inEventHangar:
            self.delayCallback(self._CALLBACK_SHOW_AWARD_WAIT_TIME, self._onProgressChanged, delayStarted=True)
        else:
            self.clearCallbacks()

    def _onProgressChanged(self, delayStarted=False):
        if self._lobbyInited and self._inEventHangar:
            if delayStarted and not self.isInQueue and not self.isBattleResultsOpen and not isPopupsWindowsOpenDisabled():
                self.__showAwardWindow()
            else:
                self.delayCallback(self._CALLBACK_SHOW_AWARD_WAIT_TIME, self._onProgressChanged, delayStarted=True)

    def __showAwardWindow(self):
        difficultyCtrl = self._gameEventController.getDifficultyController()
        for item in difficultyCtrl.getItems():
            level = item.getDifficultyLevel()
            if level == 1:
                continue
            if item.isCompleted() and not difficultyCtrl.isDifficultyLevelShown(level):
                g_eventDispatcher.loadDifficultyLevelUnlocked()
                return

    @property
    def isBattleResultsOpen(self):
        if self.__app is not None:
            if self.__app.containerManager is not None:
                lobbySubContainer = self.__app.containerManager.getContainer(WindowLayer.SUB_VIEW)
                if lobbySubContainer is not None:
                    if lobbySubContainer.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.EVENT_BATTLE_RESULTS}):
                        return True
        return False

    @sf_lobby
    def __app(self):
        return None
