# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/states/StateResultScreen.py
from copy import deepcopy
from adisp import process
from bootcamp.BootCampEvents import g_bootcampEvents
from bootcamp.BootcampConstants import BOOTCAMP_BATTLE_RESULT_MESSAGE
from bootcamp.states import STATE
from bootcamp.states.AbstractState import AbstractState
from gui.app_loader import settings
from gui.impl.gen import R
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from gui.shared.items_cache import CACHE_SYNC_REASON
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache

class StateResultScreen(AbstractState):
    battleResults = dependency.descriptor(IBattleResultsService)
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, lessonResults):
        super(StateResultScreen, self).__init__(STATE.RESULT_SCREEN)
        self.__lessonResults = deepcopy(lessonResults)
        self.__storedArenaUniqueID = 0

    def handleKeyEvent(self, event):
        pass

    @process
    def _doActivate(self):
        from bootcamp.Bootcamp import g_bootcamp
        g_bootcamp.showBattleResultTransition()
        yield self.itemsCache.update(CACHE_SYNC_REASON.SHOW_GUI)
        resultType = g_bootcamp.getBattleResults().type
        if resultType == BOOTCAMP_BATTLE_RESULT_MESSAGE.FAILURE:
            g_bootcampEvents.onResultScreenFinished()
            g_bootcamp.hideBattleResultTransition()
            return
        else:
            battleCtx = self.sessionProvider.getCtx()
            if battleCtx.lastArenaUniqueID:
                app = self.appLoader.getApp(settings.APP_NAME_SPACE.SF_LOBBY)
                self.appLoader.getWaitingWorker().hide(R.strings.waiting.exit_battle())
                if app is not None and app.initialized:
                    self.__requestBattleResults(battleCtx.lastArenaUniqueID)
                else:
                    self.__storedArenaUniqueID = battleCtx.lastArenaUniqueID
                    g_eventBus.addListener(events.AppLifeCycleEvent.INITIALIZED, self.__onAppInitialized, EVENT_BUS_SCOPE.GLOBAL)
                battleCtx.lastArenaUniqueID = None
            return

    def _doDeactivate(self):
        g_eventBus.removeListener(events.AppLifeCycleEvent.INITIALIZED, self.__onAppInitialized, EVENT_BUS_SCOPE.GLOBAL)
        from bootcamp.Bootcamp import g_bootcamp
        g_bootcamp.hideBattleResultTransition()

    def __onAppInitialized(self, event):
        if event.ns == settings.APP_NAME_SPACE.SF_LOBBY and self.__storedArenaUniqueID:
            self.__requestBattleResults(self.__storedArenaUniqueID)

    @process
    def __requestBattleResults(self, arenaUniqueID):
        from gui.battle_results import RequestResultsContext
        yield self.battleResults.requestResults(RequestResultsContext(arenaUniqueID))
