# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/prb_control/entities/squad/actions_handler.py
from gui.prb_control.entities.base.squad.actions_handler import SquadActionsHandler
from historical_battles.gui.shared.event_dispatcher import showHistoricalBattleQueueView, showHBHangar
from wg_async import wg_async, wg_await
from BWUtil import AsyncReturn

class HistoricalBattleSquadActionsHandler(SquadActionsHandler):

    def _showBattleQueueGUI(self):
        showHistoricalBattleQueueView()

    def _setCreatorReady(self):
        self._sendBattleQueueRequest()

    def setUnitChanged(self, loadHangar=False):
        flags = self._entity.getFlags()
        if self._entity.getPlayerInfo().isReady and flags.isInQueue():
            self._showBattleQueueGUI()
        elif loadHangar:
            showHBHangar()

    @wg_async
    def _validateUnitState(self, entity):
        result = yield wg_await(super(HistoricalBattleSquadActionsHandler, self)._validateUnitState(entity, checkAmmo=False))
        if not result:
            raise AsyncReturn(result)
        raise AsyncReturn(True)
