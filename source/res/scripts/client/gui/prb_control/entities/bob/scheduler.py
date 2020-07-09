# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/bob/scheduler.py
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
from skeletons.gui.game_control import IBobController

class BobScheduler(BaseScheduler):
    bobController = dependency.descriptor(IBobController)

    def __init__(self, entity):
        super(BobScheduler, self).__init__(entity)
        self.__isPrimeTime = False
        self.__isConfigured = False

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    def init(self):
        status, _, _ = self.bobController.getPrimeTimeStatus()
        self.__isPrimeTime = status == PrimeTimeStatus.AVAILABLE
        self.__isConfigured = status != PrimeTimeStatus.NOT_SET
        self.bobController.onPrimeTimeStatusUpdated += self.__update
        self.bobController.onUpdated += self.__updateMode
        self.__show(isInit=True)

    def fini(self):
        self.bobController.onUpdated -= self.__updateMode
        self.bobController.onPrimeTimeStatusUpdated -= self.__update

    @process
    def __doLeave(self, isExit=True):
        yield self.prbDispatcher.doLeaveAction(LeavePrbAction(isExit))

    def __updateMode(self):
        if not self.bobController.isModeActive():
            self.__doLeave()
            SystemMessages.pushMessage(backport.text(R.strings.system_messages.arena_start_errors.join.EVENT_DISABLED()), type=SystemMessages.SM_TYPE.Error)

    def __update(self, status):
        if not self.bobController.isAvailable():
            self.__doLeave()
            return
        isPrimeTime = status == PrimeTimeStatus.AVAILABLE
        isConfigured = status != PrimeTimeStatus.NOT_SET
        if isPrimeTime != self.__isPrimeTime or isConfigured != self.__isConfigured:
            self.__isPrimeTime = isPrimeTime
            self.__isConfigured = isConfigured
            self.__show()
            g_eventDispatcher.updateUI()

    def __show(self, isInit=False):
        if not self.__isConfigured:
            SystemMessages.pushMessage(backport.text(R.strings.bob.systemMessage.notAvailable.primeTimeNotSet()), type=SystemMessages.SM_TYPE.BobBattlesPrimeTimeNotSet)
        elif not self.__isPrimeTime:
            SystemMessages.pushMessage(backport.text(R.strings.bob.systemMessage.primeTime.battlesUnavailable()), type=SystemMessages.SM_TYPE.BobBattlesPrimeTime)
        elif not isInit:
            SystemMessages.pushMessage(backport.text(R.strings.bob.systemMessage.primeTime.battlesAvailable()), type=SystemMessages.SM_TYPE.BobBattlesAvailable)
