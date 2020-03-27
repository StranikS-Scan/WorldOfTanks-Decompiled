# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/stronghold/unit/actions_handler.py
from gui.prb_control.entities.base.external_battle_unit.base_external_battle_ctx import StopPlayersMatchingBaseExternalUnitCtx
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.base.unit.actions_handler import UnitActionsHandler
from gui.prb_control.entities.base.unit.ctx import BattleQueueUnitCtx

class StrongholdActionsHandler(UnitActionsHandler):

    def showGUI(self):
        g_eventDispatcher.showStrongholdsWindow()

    def exitFromQueue(self):
        self._sendBattleQueueRequest(action=0)

    def _canDoAutoSearch(self, unit, stats):
        return False

    def _sendBattleQueueRequest(self, vInvID=0, action=1):
        self._entity.request(BattleQueueUnitCtx(action=action))

    def exitFromPlayersMatchingMode(self):
        self._entity.request(StopPlayersMatchingBaseExternalUnitCtx())
