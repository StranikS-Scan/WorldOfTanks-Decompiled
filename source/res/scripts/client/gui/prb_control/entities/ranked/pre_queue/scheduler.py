# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/ranked/pre_queue/scheduler.py
import constants
from gui import SystemMessages
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.prb_control.entities.base.pre_queue.ctx import LeavePreQueueCtx
from gui.prb_control.entities.base.scheduler import BaseScheduler
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.formatters.windows import SwitchPeripheryRankedCtx
from gui.ranked_battles.constants import PRIME_TIME_STATUS
from helpers import dependency, i18n
from skeletons.gui.game_control import IRankedBattlesController

class RankedScheduler(BaseScheduler):
    rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self, entity):
        super(RankedScheduler, self).__init__(entity)
        self.__isPrimeTime = False

    def init(self):
        status, _, _ = self.rankedController.getPrimeTimeStatus()
        self.__isPrimeTime = status == PRIME_TIME_STATUS.AVAILABLE
        self.rankedController.onPrimeTimeStatusUpdated += self.__update
        self.__show(isInit=True)

    def fini(self):
        self.rankedController.onPrimeTimeStatusUpdated -= self.__update

    def __update(self, status):
        if not self.rankedController.isAvailable():
            self._entity.leave(LeavePreQueueCtx(waitingID='prebattle/leave'))
            return
        isPrimeTime = status == PRIME_TIME_STATUS.AVAILABLE
        if isPrimeTime != self.__isPrimeTime:
            self.__isPrimeTime = isPrimeTime
            self.__show()
            g_eventDispatcher.updateUI()

    def __show(self, isInit=False):
        if not self.__isPrimeTime:
            SystemMessages.pushMessage(i18n.makeString(SYSTEM_MESSAGES.RANKED_NOTIFICATION_PRIMETIME), type=SystemMessages.SM_TYPE.PrimeTime)
            if self.rankedController.hasAnyPeripheryWithPrimeTime() and not constants.IS_CHINA:
                g_eventDispatcher.showSwitchPeripheryWindow(ctx=SwitchPeripheryRankedCtx(), isModal=False)
        elif not isInit:
            SystemMessages.pushMessage(i18n.makeString(SYSTEM_MESSAGES.RANKED_NOTIFICATION_AVAILABLE), type=SystemMessages.SM_TYPE.RankedBattlesAvailable)
