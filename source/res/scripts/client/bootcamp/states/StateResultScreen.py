# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/states/StateResultScreen.py
from copy import deepcopy
from adisp import process
from bootcamp.BootCampEvents import g_bootcampEvents
from bootcamp.BootcampConstants import BOOTCAMP_BATTLE_RESULT_MESSAGE
from bootcamp.states import STATE
from bootcamp.states.AbstractState import AbstractState
from gui.shared.items_cache import CACHE_SYNC_REASON
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.battle_results import IBattleResultsService

class StateResultScreen(AbstractState):

    def __init__(self, lessonResults):
        super(StateResultScreen, self).__init__(STATE.RESULT_SCREEN)
        self.__lessonResults = deepcopy(lessonResults)

    def handleKeyEvent(self, event):
        pass

    @process
    def _doActivate(self):
        from bootcamp.Bootcamp import g_bootcamp
        from gui.battle_results.context import RequestResultsContext
        from bootcamp.BattleResultTransition import BattleResultTransition
        from gui.shared.personality import ServicesLocator
        sessionProvider = dependency.instance(IBattleSessionProvider)
        battleResultProvider = dependency.instance(IBattleResultsService)
        battleCtx = sessionProvider.getCtx()
        if g_bootcamp.transitionFlash is not None:
            g_bootcamp.transitionFlash.close()
        g_bootcamp.transitionFlash = BattleResultTransition()
        g_bootcamp.transitionFlash.active(True)
        yield ServicesLocator.itemsCache.update(CACHE_SYNC_REASON.SHOW_GUI)
        resultType = g_bootcamp.getBattleResults().type
        if resultType == BOOTCAMP_BATTLE_RESULT_MESSAGE.FAILURE:
            g_bootcampEvents.onResultScreenFinished()
            g_bootcamp.transitionFlash.active(False)
            g_bootcamp.transitionFlash.close()
            g_bootcamp.transitionFlash = None
            return
        else:
            if battleCtx.lastArenaUniqueID:
                yield battleResultProvider.requestResults(RequestResultsContext(battleCtx.lastArenaUniqueID))
                battleCtx.lastArenaUniqueID = None
            return

    def _doDeactivate(self):
        pass
