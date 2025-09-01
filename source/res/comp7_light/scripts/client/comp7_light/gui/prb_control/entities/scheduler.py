# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/prb_control/entities/scheduler.py
import BigWorld
from adisp import adisp_process
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.periodic_battles.models import PrimeTimeStatus
from gui.prb_control import prbDispatcherProperty
from gui.prb_control.entities.base.ctx import LeavePrbAction
from gui.prb_control.entities.base.scheduler import BaseScheduler
from gui.prb_control.events_dispatcher import g_eventDispatcher
from helpers import dependency
from skeletons.gui.game_control import IComp7LightController

class Comp7LightScheduler(BaseScheduler):
    __comp7LightController = dependency.descriptor(IComp7LightController)

    def __init__(self, entity):
        super(Comp7LightScheduler, self).__init__(entity)
        self.__isPrimeTime = False
        self.__hasPrimeTimePeripheries = False

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    def init(self):
        status, _, _ = self.__comp7LightController.getPrimeTimeStatus()
        self.__isPrimeTime = status == PrimeTimeStatus.AVAILABLE
        self.__hasPrimeTimePeripheries = self.__comp7LightController.hasAvailablePrimeTimeServers()
        self.__comp7LightController.onStatusUpdated += self.__update

    def fini(self):
        self.__comp7LightController.onStatusUpdated -= self.__update

    def __checkLeave(self):
        if not self.__comp7LightController.isEnabled() or self.__comp7LightController.isFrozen():
            BigWorld.callback(0.0, self.__doLeave)
            return True
        return False

    @adisp_process
    def __doLeave(self):
        yield self.prbDispatcher.doLeaveAction(LeavePrbAction(True))

    def __update(self, status):
        if self.__checkLeave():
            return
        else:
            isPrimeTime = status == PrimeTimeStatus.AVAILABLE
            hasPrimeTimePeripheries = self.__comp7LightController.hasAvailablePrimeTimeServers()
            if isPrimeTime != self.__isPrimeTime:
                self.__isPrimeTime = isPrimeTime
                if self.__comp7LightController.getCurrentCycleID() is not None:
                    if self.__isPrimeTime and not self.__hasPrimeTimePeripheries:
                        SystemMessages.pushMessage(text=backport.text(R.strings.comp7_light.system_messages.primeTime.start.body()), type=SystemMessages.SM_TYPE.PrimeTime, messageData={'title': backport.text(R.strings.comp7_light.system_messages.primeTime.start.title())})
                    elif not hasPrimeTimePeripheries:
                        SystemMessages.pushMessage(text=backport.text(R.strings.comp7_light.system_messages.primeTime.end.body()), type=SystemMessages.SM_TYPE.PrimeTime, messageData={'title': backport.text(R.strings.comp7_light.system_messages.primeTime.end.title())})
                g_eventDispatcher.updateUI()
            self.__hasPrimeTimePeripheries = hasPrimeTimePeripheries
            return
