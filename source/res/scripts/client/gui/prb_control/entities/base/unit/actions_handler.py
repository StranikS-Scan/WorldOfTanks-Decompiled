# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/unit/actions_handler.py
import weakref
from constants import PREBATTLE_TYPE
from debug_utils import LOG_DEBUG
from gui import DialogsInterface
from gui.Scaleform.daapi.view.dialogs import rally_dialog_meta
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.base.unit.ctx import BattleQueueUnitCtx, AutoSearchUnitCtx
from gui.prb_control.settings import FUNCTIONAL_FLAG

class AbstractActionsHandler(object):

    def __init__(self, entity):
        self._entity = weakref.proxy(entity)

    def showGUI(self):
        pass

    def setPlayerInfoChanged(self):
        pass

    def setPlayersChanged(self):
        pass

    def setUnitChanged(self):
        pass

    def executeInit(self, ctx):
        return FUNCTIONAL_FLAG.UNDEFINED

    def executeFini(self):
        pass

    def executeRestore(self):
        pass

    def execute(self):
        pass

    def clear(self):
        self._entity = None
        return

    def exitFromQueue(self):
        pass

    def _sendBattleQueueRequest(self, vInvID=0, action=1):
        ctx = BattleQueueUnitCtx('prebattle/battle_queue', action=action)
        ctx.selectVehInvID = vInvID
        LOG_DEBUG('Unit request', ctx)
        self._entity.doBattleQueue(ctx)


class UnitActionsHandler(AbstractActionsHandler):

    def executeFini(self):
        prbType = self._entity.getEntityType()
        g_eventDispatcher.removeUnitFromCarousel(prbType)
        g_eventDispatcher.loadHangar()

    def execute(self):
        pInfo = self._entity.getPlayerInfo()
        if pInfo.isCommander():
            stats = self._entity.getStats()
            _, unit = self._entity.getUnit()
            if self._canDoAutoSearch(unit, stats):
                if self._entity.isParentControlActivated():
                    return
                if self._entity.getFlags().isDevMode():
                    DialogsInterface.showDialog(rally_dialog_meta.UnitConfirmDialogMeta(PREBATTLE_TYPE.UNIT, 'startBattle'), lambda result: self._sendBattleQueueRequest() if result else None)
                else:
                    ctx = AutoSearchUnitCtx('prebattle/auto_search')
                    LOG_DEBUG('Unit request', ctx)
                    self._entity.doAutoSearch(ctx)
            else:
                self._sendBattleQueueRequest()
        else:
            self._entity.togglePlayerReadyAction()

    def _canDoAutoSearch(self, unit, stats):
        return stats.freeSlotsCount > 0
