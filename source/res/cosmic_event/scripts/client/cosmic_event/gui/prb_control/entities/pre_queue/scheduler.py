# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/prb_control/entities/pre_queue/scheduler.py
from adisp import adisp_process
from gui.prb_control import prbDispatcherProperty
from gui.prb_control.entities.base.ctx import LeavePrbAction
from gui.prb_control.entities.base.scheduler import BaseScheduler
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.periodic_battles.models import PrimeTimeStatus
from helpers import dependency
from cosmic_event.skeletons.battle_controller import ICosmicEventBattleController
from skeletons.gui.shared import IItemsCache

class CosmicEventBattleScheduler(BaseScheduler):
    __cosmicCtrl = dependency.descriptor(ICosmicEventBattleController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, entity):
        super(CosmicEventBattleScheduler, self).__init__(entity)
        self.__isPrimeTime = False
        self.__isConfigured = False
        self.__isEnabled = False

    def init(self):
        status, _, _ = self.__cosmicCtrl.getPrimeTimeStatus()
        self.__isPrimeTime = status == PrimeTimeStatus.AVAILABLE
        self.__isConfigured = status != PrimeTimeStatus.NOT_SET
        self.__isEnabled = self.__cosmicCtrl.isEnabled
        self.__cosmicCtrl.onCosmicConfigChanged += self.__onConfigChanged
        self.__cosmicCtrl.onPrimeTimeStatusUpdated += self.__update
        self.__itemsCache.onSyncCompleted += self.__onItemSync
        self.__show(status, isInit=True)

    def fini(self):
        self.__cosmicCtrl.onCosmicConfigChanged -= self.__onConfigChanged
        self.__cosmicCtrl.onPrimeTimeStatusUpdated -= self.__update
        self.__itemsCache.onSyncCompleted -= self.__onItemSync

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    def __update(self, status):
        isPrimeTime = status == PrimeTimeStatus.AVAILABLE
        isConfigured = status != PrimeTimeStatus.NOT_SET
        if isPrimeTime != self.__isPrimeTime or isConfigured != self.__isConfigured:
            self.__isPrimeTime = isPrimeTime
            self.__isConfigured = isConfigured
            self.__show(status)
            g_eventDispatcher.updateUI()

    def __onItemSync(self, *_):
        g_eventDispatcher.updateUI()

    def __onConfigChanged(self):
        if not self.__cosmicCtrl.isEnabled and self.__isEnabled:
            self.__doLeave()
        self.__isEnabled = self.__cosmicCtrl.isEnabled

    def __show(self, status, isInit=False):
        pass

    @adisp_process
    def __doLeave(self, isExit=True):
        yield self.prbDispatcher.doLeaveAction(LeavePrbAction(isExit))
