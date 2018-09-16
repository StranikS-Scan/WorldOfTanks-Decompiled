# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/stronghold/unit/actions_handler.py
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.base.unit.actions_handler import UnitActionsHandler
from gui.prb_control.settings import FUNCTIONAL_FLAG
from gui.prb_control.entities.base.unit.ctx import BattleQueueUnitCtx

class StrongholdActionsHandler(UnitActionsHandler):

    def showGUI(self):
        g_eventDispatcher.showStrongholdsWindow()

    def executeInit(self, ctx):
        prbType = self._entity.getEntityType()
        flags = self._entity.getFlags()
        g_eventDispatcher.loadStrongholds(prbType)
        if flags.isInIdle():
            g_eventDispatcher.setUnitProgressInCarousel(prbType, True)
        return FUNCTIONAL_FLAG.LOAD_WINDOW

    def _canDoAutoSearch(self, unit, stats):
        return False

    def _sendBattleQueueRequest(self, vInvID=0, action=1):
        ctx = BattleQueueUnitCtx('prebattle/battle_queue', action=action)
        ctx.selectVehInvID = vInvID
        self._entity.request(ctx)
