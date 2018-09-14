# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/e_sport/unit/actions_handler.py
from PlayerEvents import g_playerEvents
from constants import PREBATTLE_TYPE
from debug_utils import LOG_DEBUG
from gui import DialogsInterface, SystemMessages
from gui.Scaleform.daapi.view.dialogs import rally_dialog_meta
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.formatters import messages
from gui.prb_control.entities.base import vehicleAmmoCheck
from gui.prb_control.entities.base.unit.actions_handler import UnitActionsHandler
from gui.prb_control.entities.base.unit.ctx import BattleQueueUnitCtx, AutoSearchUnitCtx
from gui.prb_control.settings import FUNCTIONAL_FLAG

class ESportActionsHandler(UnitActionsHandler):
    """
    Base ESport actions handler
    """

    def __init__(self, entity):
        super(ESportActionsHandler, self).__init__(entity)
        g_playerEvents.onKickedFromUnitsQueue += self.__onKickedFromQueue

    def executeInit(self, ctx):
        prbType = self._entity.getEntityType()
        flags = self._entity.getFlags()
        g_eventDispatcher.loadUnit(prbType)
        if flags.isInIdle():
            g_eventDispatcher.setUnitProgressInCarousel(prbType, True)
        return FUNCTIONAL_FLAG.LOAD_WINDOW

    def executeFini(self):
        super(ESportActionsHandler, self).executeFini()

    @vehicleAmmoCheck
    def execute(self):
        pInfo = self._entity.getPlayerInfo()
        if pInfo.isCommander():
            stats = self._entity.getStats()
            _, unit = self._entity.getUnit()
            if self._canDoAutoSearch(unit, stats):
                if self._entity.isParentControlActivated():
                    return
                if self._entity.getFlags().isDevMode():
                    DialogsInterface.showDialog(rally_dialog_meta.UnitConfirmDialogMeta(PREBATTLE_TYPE.UNIT, 'startBattle'), lambda result: self._entity.doBattleQueue(BattleQueueUnitCtx('prebattle/battle_queue')) if result else None)
                else:
                    ctx = AutoSearchUnitCtx('prebattle/auto_search')
                    LOG_DEBUG('Unit request', ctx)
                    self._entity.doAutoSearch(ctx)
            else:
                self._sendBattleQueueRequest()
        else:
            self._entity.togglePlayerReadyAction()

    def clear(self):
        g_playerEvents.onKickedFromUnitsQueue -= self.__onKickedFromQueue
        super(ESportActionsHandler, self).clear()

    def showGUI(self):
        g_eventDispatcher.showUnitWindow(self._entity.getEntityType())

    def __onKickedFromQueue(self):
        """
        Listener for queue kick event. Is fix for for WOTD-43677
        """
        SystemMessages.pushMessage(messages.getKickReasonMessage('timeout'), type=SystemMessages.SM_TYPE.Warning)
