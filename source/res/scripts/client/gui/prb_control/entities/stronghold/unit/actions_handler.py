# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/stronghold/unit/actions_handler.py
from debug_utils import LOG_DEBUG
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.base.unit.actions_handler import UnitActionsHandler
from gui.prb_control.settings import FUNCTIONAL_FLAG
from gui.prb_control.entities.base.unit.ctx import BattleQueueUnitCtx

class StrongholdActionsHandler(UnitActionsHandler):
    """
    Strongholds actions handler class
    """

    def showGUI(self):
        g_eventDispatcher.showStrongholdsWindow()

    def executeInit(self, ctx):
        prbType = self._entity.getEntityType()
        flags = self._entity.getFlags()
        g_eventDispatcher.loadStrongholds(prbType)
        if flags.isInIdle():
            g_eventDispatcher.setUnitProgressInCarousel(prbType, True)
        return FUNCTIONAL_FLAG.LOAD_WINDOW

    def executeFini(self):
        super(StrongholdActionsHandler, self).executeFini()

    def _canDoAutoSearch(self, unit, stats):
        return False

    def _sendBattleQueueRequest(self, vInvID=0, action=1):
        """
        Sends enqueue or dequeue request for unit entity.
        Args:
            vInvID: vehicle inventory id
            action: action type where 1 is start and 0 is stop
        """
        ctx = BattleQueueUnitCtx('prebattle/battle_queue', action=action)
        ctx.selectVehInvID = vInvID
        self._entity.request(ctx)
