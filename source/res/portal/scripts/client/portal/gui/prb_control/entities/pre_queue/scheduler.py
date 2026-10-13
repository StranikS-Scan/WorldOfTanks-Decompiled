# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/prb_control/entities/pre_queue/scheduler.py
from gui.prb_control import prbDispatcherProperty
from gui.prb_control.entities.base.scheduler import BaseScheduler
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.periodic_battles.models import PrimeTimeStatus
from helpers import dependency
from portal.skeletons.portal_event_controller import IPortalEventController
from adisp import adisp_process
from gui.prb_control.entities.base.ctx import LeavePrbAction

class PortalBattleScheduler(BaseScheduler):
    __portalBattlesCtrl = dependency.descriptor(IPortalEventController)

    def __init__(self, entity):
        super(PortalBattleScheduler, self).__init__(entity)
        self.__isPrimeTime = False
        self.__isConfigured = False

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    def init(self):
        status, _, _ = self.__portalBattlesCtrl.getPrimeTimeStatus()
        self.__isPrimeTime = status == PrimeTimeStatus.AVAILABLE
        self.__isConfigured = status != PrimeTimeStatus.NOT_SET
        self.__portalBattlesCtrl.onPrimeTimeStatusUpdated += self.__update
        self.__show(status, isInit=True)

    def fini(self):
        self.__portalBattlesCtrl.onPrimeTimeStatusUpdated -= self.__update

    @adisp_process
    def __doLeave(self, isExit=True):
        yield self.prbDispatcher.doLeaveAction(LeavePrbAction(isExit))
        self.__portalBattlesCtrl.selectRandomBattle()

    def __update(self, status):
        if not self.__portalBattlesCtrl.isEnabled():
            self.__doLeave()
            return
        isPrimeTime = status == PrimeTimeStatus.AVAILABLE
        isConfigured = status != PrimeTimeStatus.NOT_SET
        if isPrimeTime != self.__isPrimeTime or isConfigured != self.__isConfigured:
            self.__isPrimeTime = isPrimeTime
            self.__isConfigured = isConfigured
            self.__show(status)
            g_eventDispatcher.updateUI()

    def __show(self, status, isInit=False):
        pass
