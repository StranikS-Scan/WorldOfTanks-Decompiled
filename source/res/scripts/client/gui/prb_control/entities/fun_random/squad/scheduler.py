# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/fun_random/squad/scheduler.py
from gui.prb_control.entities.fun_random.pre_queue.scheduler import FunRandomScheduler
from helpers import dependency
from skeletons.gui.game_control import IPlatoonController

class FunRandomSquadScheduler(FunRandomScheduler):
    __platoonCtrl = dependency.descriptor(IPlatoonController)

    def _doLeave(self):
        if self._entity.getFlags().isInQueue():
            if self._entity.getPlayerInfo().isCommander():
                self._entity.exitFromQueue()
        else:
            self.__platoonCtrl.leavePlatoon(ignoreConfirmation=True)

    def _update(self, status):
        if not self._controller.isInPrimeTime() or not self._controller.isAvailable():
            self._doLeave()
