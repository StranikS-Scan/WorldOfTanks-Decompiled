# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/prb_control/entities/squad/scheduler.py
from shared_utils import nextTick
from last_stand.gui.prb_control.entities.pre_queue.scheduler import LastStandBattleScheduler

class LastStandSquadScheduler(LastStandBattleScheduler):

    def _doLeave(self):
        if self._entity and self._entity.getFlags().isInQueue():
            if self._entity.getPlayerInfo().isCommander() and not self._isLeaveRequestSent:
                self._entity.exitFromQueue()
                self._isLeaveRequestSent = True
            nextTick(self._doLeave)()
        else:
            self._showRandomHangar()
            self._isLeaveRequestSent = False
