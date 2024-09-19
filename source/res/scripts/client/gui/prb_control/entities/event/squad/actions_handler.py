# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/event/squad/actions_handler.py
from BWUtil import AsyncReturn
from gui.impl.gen import R
from gui.prb_control.entities.base.squad.actions_handler import SquadActionsHandler
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.shared.event_dispatcher import showPlatoonInfoDialog, showPlatoonWarningDialog
from wg_async import wg_async, wg_await

class EventBattleSquadActionsHandler(SquadActionsHandler):

    @classmethod
    def _loadBattleQueue(cls):
        g_eventDispatcher.loadEventBattleQueue()

    @wg_async
    def _validateUnitState(self, entity):
        fullData = entity.getUnitFullData(unitMgrID=entity.getID())
        if entity.isCommander():
            notReadyCount = 0
            for slot in fullData.slotsIterator:
                slotPlayer = slot.player
                if slotPlayer:
                    if self._isSquadHavePlayersInBattle(slotPlayer, fullData.playerInfo):
                        yield wg_await(showPlatoonInfoDialog(R.strings.dialogs.squadHavePlayersInBattle))
                        raise AsyncReturn(False)
                    if not slotPlayer.isReady:
                        notReadyCount += 1

            if not fullData.playerInfo.isReady:
                notReadyCount -= 1
            result = True
            if fullData.stats.occupiedSlotsCount == 1:
                result = yield wg_await(showPlatoonWarningDialog(R.strings.dialogs.squadHaveNoPlayers))
            elif notReadyCount > 0:
                result = yield wg_await(showPlatoonWarningDialog(R.strings.dialogs.squadHaveNotReadyPlayer))
            if not result:
                raise AsyncReturn(result)
        raise AsyncReturn(True)
