# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/weekend_brawl/scheduler.py
from adisp import process
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control import prbDispatcherProperty
from gui.prb_control.entities.base.ctx import LeavePrbAction
from gui.prb_control.entities.base.scheduler import BaseScheduler
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.ranked_battles.constants import PrimeTimeStatus
from helpers import dependency
from skeletons.gui.game_control import IWeekendBrawlController

class WeekendBrawlScheduler(BaseScheduler):
    wBrawlController = dependency.descriptor(IWeekendBrawlController)

    def __init__(self, entity):
        super(WeekendBrawlScheduler, self).__init__(entity)
        self.__isPrimeTime = False

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    def init(self):
        status, _, _ = self.wBrawlController.getPrimeTimeStatus()
        self.__isPrimeTime = status == PrimeTimeStatus.AVAILABLE
        self.wBrawlController.onPrimeTimeStatusUpdated += self.__update
        self.wBrawlController.onUpdated += self.__updateMode
        self.__show(isInit=True)

    def fini(self):
        self.wBrawlController.onUpdated -= self.__updateMode
        self.wBrawlController.onPrimeTimeStatusUpdated -= self.__update

    @process
    def __doLeave(self, isExit=True):
        yield self.prbDispatcher.doLeaveAction(LeavePrbAction(isExit))

    def __updateMode(self):
        if not self.wBrawlController.isModeActive():
            self.__doLeave()
            SystemMessages.pushMessage(backport.text(R.strings.weekend_brawl.systemMessage.notAvailable()), type=SystemMessages.SM_TYPE.Warning)

    def __update(self, status):
        if not self.wBrawlController.isAvailable():
            self.__doLeave()
            return
        isPrimeTime = status == PrimeTimeStatus.AVAILABLE
        if isPrimeTime != self.__isPrimeTime:
            self.__isPrimeTime = isPrimeTime
            self.__show()
            g_eventDispatcher.updateUI()

    def __show(self, isInit=False):
        if not self.__isPrimeTime:
            SystemMessages.pushMessage(backport.text(R.strings.weekend_brawl.systemMessage.primeTime.battlesUnavailable()), type=SystemMessages.SM_TYPE.PrimeTime)
        elif not isInit:
            SystemMessages.pushMessage(backport.text(R.strings.weekend_brawl.systemMessage.primeTime.battlesAvailable()), type=SystemMessages.SM_TYPE.WeekendBrawlAvailable)
