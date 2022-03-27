# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/actions_per_minute.py
import typing
import time
import math
from collections import deque
import BigWorld
from PlayerEvents import g_playerEvents
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from constants import IS_DEVELOPMENT, ARENA_PERIOD
from debug_utils import LOG_DEBUG
from helpers import isPlayerAvatar
from skeletons.helpers.statistics import IActionsPerMinute
if typing.TYPE_CHECKING:
    from ClientArena import ClientArena
_ONE_MINUTE = 60.0
_ALLOWED_EVENT_TIME = 0.01
_WATCHER_NAME_TOTAL_APM = 'Statistics/APM/total'
_WATCHER_NAME_AVG_APM = 'Statistics/APM/average'
_WATCHER_NAME_PEAK_APM = 'Statistics/APM/peak'

class ActionsPerMinute(IActionsPerMinute):
    SUPPORTED_BONUS_CAPS = (ARENA_BONUS_TYPE_CAPS.RTS_COMPONENT,)

    def __init__(self):
        self.__actionsHistory = deque()
        self.__totalActionsCount = 0
        self.__peakAPM = 0
        self.__trackingStartTime = None
        self.__arenaUniqueID = None
        self.__nextAllowedActionTime = 0
        self.__keyMaps = {}
        return

    def start(self):
        if isPlayerAvatar():
            arena = BigWorld.player().arena
            arena.onPeriodChange += self.__onArenaPeriodChange
            arena.onVehicleKilled += self.__onVehicleKilled
            if arena.period == ARENA_PERIOD.BATTLE:
                self.__startApmTracking()
            g_playerEvents.onRoundFinished += self.__onRoundFinished

    def reset(self):
        self.__trackingStartTime = None
        self.__totalActionsCount = 0
        self.__peakAPM = 0
        self.__actionsHistory.clear()
        return

    def stop(self):
        self.__finalizeApmTracking()
        if isPlayerAvatar():
            arena = BigWorld.player().arena
            arena.onPeriodChange -= self.__onArenaPeriodChange
        g_playerEvents.onRoundFinished -= self.__onRoundFinished

    def recordAction(self, keyInfo=None):
        if self.__trackingStartTime is None:
            return
        else:
            now = time.time()
            if now < self.__nextAllowedActionTime:
                return
            self.__nextAllowedActionTime = now + _ALLOWED_EVENT_TIME
            if keyInfo is not None:
                isDown, key = keyInfo
                wasDown = self.__keyMaps.get(key, None)
                self.__keyMaps[key] = isDown
                if wasDown and not isDown:
                    LOG_DEBUG('recordAction: skip isUpEvent', keyInfo)
                    return
            self.__totalActionsCount += 1
            history = self.__actionsHistory
            expireTime = now + _ONE_MINUTE
            history.append(expireTime)
            while history and history[0] < now:
                history.popleft()

            apm = len(history)
            if apm > self.__peakAPM:
                self.__peakAPM = apm
            return

    def __sendReportAPM(self):
        if isPlayerAvatar() and self.__arenaUniqueID is not None and self.__totalActionsCount > 0:
            averageAPM = self.__getAverageAPM()
            avatar = BigWorld.player()
            if avatar.isPlayer:
                avatar.base.reportAPM(self.__arenaUniqueID, averageAPM, self.__peakAPM)
        return

    def __onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo):
        if period == ARENA_PERIOD.BATTLE:
            self.__startApmTracking()
        elif period == ARENA_PERIOD.AFTERBATTLE:
            self.__finalizeApmTracking()

    def __onRoundFinished(self, *args, **kwargs):
        self.__finalizeApmTracking()

    def __onVehicleKilled(self, *args, **kwargs):
        self.__sendReportAPM()

    def __startApmTracking(self):
        if self.__trackingStartTime is not None:
            return
        else:
            self.reset()
            if not isPlayerAvatar():
                return
            arena = BigWorld.player().arena
            if not ARENA_BONUS_TYPE_CAPS.checkAny(arena.bonusType, *ActionsPerMinute.SUPPORTED_BONUS_CAPS):
                return
            self.__trackingStartTime = time.time()
            self.__arenaUniqueID = arena.arenaUniqueID
            if IS_DEVELOPMENT:
                BigWorld.addWatcher(_WATCHER_NAME_TOTAL_APM, self.__getTotalActionsCount)
                BigWorld.addWatcher(_WATCHER_NAME_AVG_APM, self.__getAverageAPM)
                BigWorld.addWatcher(_WATCHER_NAME_PEAK_APM, self.__getCurrentPeakAPM)
            return

    def __finalizeApmTracking(self):
        if self.__trackingStartTime is None:
            return
        else:
            self.__sendReportAPM()
            self.__trackingStartTime = None
            if IS_DEVELOPMENT:
                BigWorld.delWatcher(_WATCHER_NAME_TOTAL_APM)
                BigWorld.delWatcher(_WATCHER_NAME_AVG_APM)
                BigWorld.delWatcher(_WATCHER_NAME_PEAK_APM)
            return

    def __getAverageAPM(self):
        now = time.time()
        if self.__trackingStartTime is not None and self.__totalActionsCount > 0:
            durationInSec = now - self.__trackingStartTime
            if durationInSec > 0.0:
                battleMinutes = float(max(math.ceil(durationInSec / _ONE_MINUTE), 1.0))
                return int(math.floor(self.__totalActionsCount / battleMinutes))
        return 0

    def __getCurrentPeakAPM(self):
        return self.__peakAPM

    def __getTotalActionsCount(self):
        return self.__totalActionsCount
