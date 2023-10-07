# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/prb_control/entities/pre_queue/sheduler.py
import adisp
from shared_utils import nextTick
from gui.prb_control.entities.base.pre_queue.ctx import LeavePreQueueCtx
from gui.prb_control.entities.base.scheduler import BaseScheduler
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.prb_control import prbDispatcherProperty
from gui.periodic_battles.models import PrimeTimeStatus
from helpers import dependency
from skeletons.gui.game_control import IHalloweenController

class HalloweenScheduler(BaseScheduler):
    __eventBattlesCtrl = dependency.descriptor(IHalloweenController)

    def __init__(self, entity):
        super(HalloweenScheduler, self).__init__(entity)
        self.__isPrimeTime = False
        self.__isConfigured = False

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    def init(self):
        status, _, _ = self.__eventBattlesCtrl.getPrimeTimeStatus()
        self.__isPrimeTime = status == PrimeTimeStatus.AVAILABLE
        self.__isConfigured = status != PrimeTimeStatus.NOT_SET
        self.__eventBattlesCtrl.onPrimeTimeStatusUpdated += self.__update
        self.__eventBattlesCtrl.onEventDisabled += self.__onEventDisabled
        self.__eventBattlesCtrl.onCompleteActivePhase += self.__onCompleteActivePhase
        self.__show(status, isInit=True)

    def fini(self):
        self.__eventBattlesCtrl.onPrimeTimeStatusUpdated -= self.__update
        self.__eventBattlesCtrl.onEventDisabled -= self.__onEventDisabled
        self.__eventBattlesCtrl.onCompleteActivePhase -= self.__onCompleteActivePhase

    def __update(self, status):
        isPrimeTime = status == PrimeTimeStatus.AVAILABLE
        isConfigured = status != PrimeTimeStatus.NOT_SET
        if isPrimeTime != self.__isPrimeTime or isConfigured != self.__isConfigured:
            self.__isPrimeTime = isPrimeTime
            self.__isConfigured = isConfigured
            self.__show(status)
            g_eventDispatcher.updateUI()

    def _doLeave(self):
        self._entity.leave(LeavePreQueueCtx(waitingID='prebattle/leave'))
        self._showRandomHangar()

    @adisp.adisp_process
    def _showRandomHangar(self):
        yield self.prbDispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.RANDOM))
        g_eventDispatcher.loadHangar()

    def __show(self, status, isInit=False):
        pass

    def __onEventDisabled(self):
        nextTick(self._doLeave)()

    def __onCompleteActivePhase(self):
        if self.__eventBattlesCtrl.isPostPhase():
            nextTick(self._doLeave)()
