# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/prb_control/entities/squad/scheduler.py
from grinch.gui.prb_control.entities.pre_queue.scheduler import GrinchScheduler
from grinch.skeletons.battle_controller import IGrinchController
from helpers import dependency
from shared_utils import nextTick

class GrinchSquadScheduler(GrinchScheduler):
    __grinchCtrl = dependency.descriptor(IGrinchController)

    def _doLeave(self):
        if self._entity and self._entity.getFlags().isInQueue():
            if self._entity.getPlayerInfo().isCommander() and not self._isLeaveRequestSent:
                self._entity.exitFromQueue()
                self._isLeaveRequestSent = True
            nextTick(self._doLeave)()
        else:
            self.__grinchCtrl.selectRandomMode()
            self._isLeaveRequestSent = False
