# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/fort/unit/fort_battle/scheduler.py
from gui.prb_control import prb_getters
from gui.prb_control.entities.base.scheduler import BaseScheduler
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.shared.fortifications.fort_listener import FortListener
from gui.shared.fortifications.settings import CLIENT_FORT_STATE
from gui.shared.utils.scheduled_notifications import DeltaNotifier

class FortBattleScheduler(BaseScheduler, FortListener):
    """
    Class that process schedules for unit functionality
    """

    def init(self):
        self.startFortListening()
        self.addNotificator(DeltaNotifier(self._getFortBattleTimer, self._showWindow, 10))
        self.startNotification()

    def fini(self):
        self.stopFortListening()
        self.clearNotification()

    def onClientStateChanged(self, state):
        if state.getStateID() == CLIENT_FORT_STATE.HAS_FORT:
            self.startNotification()
        elif self.fortState.getStateID() in CLIENT_FORT_STATE.NOT_AVAILABLE_FORT:
            self.stopNotification()

    def onFortBattleChanged(self, cache, item, battleItem):
        if prb_getters.getBattleID() == battleItem.getID():
            self.startNotification()

    def _getFortBattleTimer(self):
        """
        Gets the fort battle start time left
        """
        if self.fortState.getStateID() == CLIENT_FORT_STATE.HAS_FORT:
            fortBattle = self.fortCtrl.getFort().getBattle(prb_getters.getBattleID())
            if fortBattle is not None:
                return fortBattle.getRoundStartTimeLeft()
        return 0

    def _showWindow(self):
        """
        Shows fort battle unit window
        """
        pInfo = self._entity.getPlayerInfo()
        if pInfo.isInSlot and not pInfo.isReady:
            g_eventDispatcher.showFortWindow()
