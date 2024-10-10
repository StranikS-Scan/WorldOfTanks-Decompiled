# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/prb_control/entities/pre_queue/scheduler.py
from gui.prb_control import prbDispatcherProperty
from gui.prb_control.entities.base.scheduler import BaseScheduler
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.periodic_battles.models import PrimeTimeStatus
from helpers import dependency
from skeletons.gui.game_control import IWhiteTigerController

class WhiteTigerScheduler(BaseScheduler):
    __wtController = dependency.descriptor(IWhiteTigerController)

    def __init__(self, entity):
        super(WhiteTigerScheduler, self).__init__(entity)
        self.__isPrimeTime = False
        self.__isConfigured = False

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    def init(self):
        status, _, _ = self.__wtController.getPrimeTimeStatus()
        self.__isPrimeTime = status == PrimeTimeStatus.AVAILABLE
        self.__isConfigured = status != PrimeTimeStatus.NOT_SET
        self.__wtController.onPrimeTimeStatusUpdated += self.__update

    def fini(self):
        self.__wtController.onPrimeTimeStatusUpdated -= self.__update

    def __update(self, status):
        isPrimeTime = status == PrimeTimeStatus.AVAILABLE
        isConfigured = status != PrimeTimeStatus.NOT_SET
        if isPrimeTime != self.__isPrimeTime or isConfigured != self.__isConfigured:
            self.__isPrimeTime = isPrimeTime
            self.__isConfigured = isConfigured
            g_eventDispatcher.updateUI()
