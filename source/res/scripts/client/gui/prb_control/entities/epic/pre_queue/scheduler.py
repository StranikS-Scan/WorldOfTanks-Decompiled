# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/epic/pre_queue/scheduler.py
from gui.prb_control.entities.base.pre_queue.ctx import LeavePreQueueCtx
from gui.prb_control.entities.base.scheduler import BaseScheduler
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.ranked_battles.constants import PrimeTimeStatus
from helpers import dependency, time_utils
from skeletons.gui.game_control import IEpicBattleMetaGameController

class EpicMetaScheduler(BaseScheduler):
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)

    def __init__(self, entity):
        super(EpicMetaScheduler, self).__init__(entity)
        self.__isPrimeTime = False
        self.__isCycle = False
        self.__validVehicleLevels = None
        self.__unlockableInBattleVehicleLevels = None
        return

    def init(self):
        status, _, _ = self.__epicController.getPrimeTimeStatus()
        self.__isPrimeTime = status == PrimeTimeStatus.AVAILABLE
        season = self.__epicController.getCurrentSeason()
        if season is not None:
            self.__isCycle = season.hasActiveCycle(time_utils.getCurrentLocalServerTimestamp())
        modeSettings = self.__epicController.getModeSettings()
        self.__validVehicleLevels = modeSettings.validVehicleLevels
        self.__unlockableInBattleVehicleLevels = modeSettings.unlockableInBattleVehLevels
        self.__epicController.onPrimeTimeStatusUpdated += self.__onPrimeTimeUpdated
        self.__epicController.onEventEnded += self.__checkEpicIsEnabled
        self.__epicController.onUpdated += self.__onEpicSettingsUpdated
        return

    def fini(self):
        self.__epicController.onPrimeTimeStatusUpdated -= self.__onPrimeTimeUpdated
        self.__epicController.onEventEnded -= self.__checkEpicIsEnabled
        self.__epicController.onUpdated -= self.__onEpicSettingsUpdated

    def __onPrimeTimeUpdated(self, status):
        if not self.__checkEpicIsEnabled():
            return
        isPrimeTime = status == PrimeTimeStatus.AVAILABLE
        time = time_utils.getCurrentLocalServerTimestamp()
        isCycle = self.__epicController.getCurrentSeason().hasActiveCycle(time)
        if isPrimeTime != self.__isPrimeTime or isCycle != self.__isCycle:
            self.__isPrimeTime = isPrimeTime
            self.__isCycle = isCycle
            g_eventDispatcher.updateUI()

    def __onEpicSettingsUpdated(self, diff):
        validVehicleLevels = diff.get('validVehicleLevels', self.__validVehicleLevels)
        unlockableInBattleVehicleLevels = diff.get('unlockableInBattleVehicleLevels', self.__unlockableInBattleVehicleLevels)
        if validVehicleLevels != self.__validVehicleLevels or unlockableInBattleVehicleLevels != self.__unlockableInBattleVehicleLevels:
            self.__validVehicleLevels = validVehicleLevels
            self.__unlockableInBattleVehicleLevels = unlockableInBattleVehicleLevels
            self.__doLeave()

    def __checkEpicIsEnabled(self):
        hasCurrentSeason = self.__epicController.getCurrentSeason() is not None
        if not self.__epicController.isEnabled() or self.__epicController.isFrozen() or not hasCurrentSeason:
            self.__doLeave()
            return False
        else:
            return True

    def __doLeave(self):
        self._entity.leave(LeavePreQueueCtx(waitingID='prebattle/leave'))
