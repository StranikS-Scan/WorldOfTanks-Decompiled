# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/battle_royale/scheduler.py
from gui.impl import backport
from gui.impl.gen import R
from gui import SystemMessages
from gui.prb_control.entities.base.pre_queue.ctx import LeavePreQueueCtx
from gui.prb_control.entities.base.scheduler import BaseScheduler
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.ranked_battles.constants import PrimeTimeStatus
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController

class RoyaleScheduler(BaseScheduler):
    __royaleController = dependency.descriptor(IBattleRoyaleController)

    def __init__(self, entity):
        super(RoyaleScheduler, self).__init__(entity)
        self.__isPrimeTime = False

    def init(self):
        status, _, _ = self.__royaleController.getPrimeTimeStatus()
        self.__isPrimeTime = status == PrimeTimeStatus.AVAILABLE
        self.__royaleController.onGameModeStatusUpdated += self.__update
        self.__show()

    def fini(self):
        self.__royaleController.onGameModeStatusUpdated -= self.__update

    def __update(self, status):
        if not self.__royaleController.isEnabled():
            self._entity.leave(LeavePreQueueCtx(waitingID='prebattle/leave'))
            return
        isPrimeTime = status == PrimeTimeStatus.AVAILABLE
        if isPrimeTime != self.__isPrimeTime:
            self.__isPrimeTime = isPrimeTime
            self.__show()
            g_eventDispatcher.updateUI()

    def __show(self):
        if not self.__isPrimeTime and not self.__royaleController.hasAvailablePrimeTimeServers():
            SystemMessages.pushMessage(backport.text(R.strings.system_messages.royale.notification.primeTime()), type=SystemMessages.SM_TYPE.PrimeTime)
