# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/prb_control/entities/squad/scheduler.py
from __future__ import absolute_import
from shared_utils import nextTick
from halloween.gui.prb_control.entities.pre_queue.scheduler import HalloweenBattleScheduler

class HalloweenSquadScheduler(HalloweenBattleScheduler):

    def _doLeave(self):
        if self._entity and self._entity.getFlags().isInQueue():
            if self._entity.getPlayerInfo().isCommander() and not self._isLeaveRequestSent:
                self._entity.exitFromQueue()
                self._isLeaveRequestSent = True
            nextTick(self._doLeave)()
        else:
            self._showRandomHangar()
            self._isLeaveRequestSent = False
