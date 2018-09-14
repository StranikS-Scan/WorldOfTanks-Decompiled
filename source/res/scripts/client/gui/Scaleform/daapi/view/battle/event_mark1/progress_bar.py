# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event_mark1/progress_bar.py
import BigWorld
from Math import Vector3
from gui.shared.lock import Lock
from gui.battle_control.battle_constants import BATTLE_SYNC_LOCKS
from gui.Scaleform.daapi.view.battle.event_mark1.common import playMark1AtBaseWarningSound
from gui.Scaleform.daapi.view.meta.EventProgressPanelMeta import EventProgressPanelMeta
from gui.battle_control.arena_info.interfaces import IVehiclesPositionsTeamBasesController
from gui.battle_control import g_sessionProvider
from constants import MARK1_TEAM_NUMBER
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID
from CTFManager import g_ctfManager
from constants import FLAG_TYPES, FLAG_STATE
from account_helpers.settings_core.settings_constants import GRAPHICS
from account_helpers.settings_core import g_settingsCore
from debug_utils import LOG_WARNING
_UPDATE_INTERVAL = 3
_START_POINT = Vector3(339.77, 0, -275.338)
_END_POINT_OFFSET = 35
_BATTLE_END_WARNING_DISTANCE_THRESHOLD = 70

class _MARK1_STATES(object):
    MOVING = 'moving'
    STOPPED = 'stopped'


class Mark1ProgressBarPanel(EventProgressPanelMeta, IVehiclesPositionsTeamBasesController):

    def __init__(self):
        super(Mark1ProgressBarPanel, self).__init__()
        self.__mark1VehicleID = None
        self.__timerCallbackID = None
        self.__currentHealth = 0
        self.__currentProgress = 0
        self.__endPoint = None
        self.__totalDistance = 0
        self.__isInitialized = False
        self.__soundLock = Lock(BATTLE_SYNC_LOCKS.BATTLE_MARK1_AT_BASE_SOUND_LOCK)
        self.__eventsViewLock = Lock(BATTLE_SYNC_LOCKS.MARK1_EVENT_NOTIFICATIONS)
        return

    def invalidateArenaInfo(self):
        self.invalidateVehiclesInfo(g_sessionProvider.getArenaDP())

    def invalidateVehiclesInfo(self, arenaDP):
        if not self.__isInitialized:
            for vInfo in arenaDP.getVehiclesInfoIterator():
                vTypeInfoVO = vInfo.vehicleType
                if vTypeInfoVO.isMark1:
                    self.__initializePanel(vInfo, arenaDP.getNumberOfTeam())
                    self.__isInitialized = True
                    break

    def invalidateTeamBaseCaptured(self, baseTeam, baseID):
        self.__updateProgress(100)

    def invalidateTeamBasePoints(self, baseTeam, baseID, points, timeLeft, invadersCnt, capturingStopped):
        self.__eventsViewLock.tryLock()

    def _populate(self):
        super(Mark1ProgressBarPanel, self)._populate()
        g_ctfManager.onFlagSpawnedAtBase += self.__onFlagSpawnedAtBase
        g_settingsCore.onSettingsChanged += self.__onSettingsChanged
        g_sessionProvider.addArenaCtrl(self)
        bonusCtrl = g_sessionProvider.dynamic.mark1Bonus
        if bonusCtrl is not None:
            bonusCtrl.onBombExploded += self.__onBombExploded
            bonusCtrl.onMark1Killed += self.__onMark1Killed
        feedbackCtrl = g_sessionProvider.shared.feedback
        if feedbackCtrl is not None:
            feedbackCtrl.onVehicleFeedbackReceived += self.__onVehicleFeedbackReceived
        return

    def _dispose(self):
        g_ctfManager.onFlagSpawnedAtBase -= self.__onFlagSpawnedAtBase
        g_settingsCore.onSettingsChanged -= self.__onSettingsChanged
        g_sessionProvider.removeArenaCtrl(self)
        bonusCtrl = g_sessionProvider.dynamic.mark1Bonus
        if bonusCtrl is not None:
            bonusCtrl.onBombExploded -= self.__onBombExploded
            bonusCtrl.onMark1Killed -= self.__onMark1Killed
        feedbackCtrl = g_sessionProvider.shared.feedback
        if feedbackCtrl is not None:
            feedbackCtrl.onVehicleFeedbackReceived -= self.__onVehicleFeedbackReceived
        self.__stopUpdateTimer()
        self.__soundLock.dispose()
        self.__eventsViewLock.dispose()
        super(Mark1ProgressBarPanel, self)._dispose()
        return

    def __initializePanel(self, vInfo, teamNumber):
        self.__mark1VehicleID = vInfo.vehicleID
        vTypeInfoVO = vInfo.vehicleType
        basePositions = g_sessionProvider.arenaVisitor.type.getTeamBasePositionsIterator()
        _, position, _ = basePositions.next()
        self.__endPoint = Vector3(position)
        self.__totalDistance = _START_POINT.distTo(self.__endPoint) - _END_POINT_OFFSET
        isAllyMark = MARK1_TEAM_NUMBER == teamNumber
        self.__currentHealth, self.__currentProgress = self.__getHealthAndProgress(vTypeInfoVO.maxHealth, self.__currentProgress)
        state = self.__getMark1InitialState()
        isColorBlind = g_settingsCore.getSetting(GRAPHICS.COLOR_BLIND)
        self.as_initS(isAllyMark, self.__currentProgress, self.__currentHealth, vTypeInfoVO.maxHealth, state, vTypeInfoVO.shortName, isColorBlind)
        self.__startUpdateTimer()

    @staticmethod
    def __getMark1InitialState():
        state = _MARK1_STATES.MOVING
        repairKitInEffect = (FLAG_STATE.ON_GROUND, FLAG_STATE.ON_SPAWN, FLAG_STATE.ON_VEHICLE)
        for flagID, flagInfo in g_ctfManager.getFlags():
            flagType = flagInfo['flagType']
            flagState = flagInfo['state']
            if flagType == FLAG_TYPES.REPAIR_KIT and flagState in repairKitInEffect:
                state = _MARK1_STATES.STOPPED
                break

        return state

    def __onFlagSpawnedAtBase(self, flagID, flagTeam, flagPos):
        flagType = g_ctfManager.getFlagType(flagID)
        if flagType == FLAG_TYPES.EXPLOSIVE:
            self.as_updateStateS(_MARK1_STATES.MOVING)

    def __onBombExploded(self):
        self.as_updateStateS(_MARK1_STATES.STOPPED)

    def __onMark1Killed(self):
        self.__updateHealth(0)

    def __onVehicleFeedbackReceived(self, eventID, vehicleID, value):
        if eventID == FEEDBACK_EVENT_ID.VEHICLE_HEALTH:
            if vehicleID == self.__mark1VehicleID:
                self.__updateTimerCallback()

    def __onSettingsChanged(self, diff):
        if GRAPHICS.COLOR_BLIND in diff:
            val = diff[GRAPHICS.COLOR_BLIND]
            self.as_updateSettingsS(val)

    def __getHealthAndProgress(self, defaultHealth, defaultProgress):
        vehicle = BigWorld.entities.get(self.__mark1VehicleID)
        if vehicle is not None:
            mark1Position = Vector3(vehicle.position.x, 0, vehicle.position.z)
            resultProgress = self.__calculateProgress(mark1Position)
            if vehicle.health < 0:
                resultHealth = 0
            else:
                resultHealth = vehicle.health
        else:
            resultHealth = defaultHealth
            positions = g_sessionProvider.arenaVisitor.getArenaPositions()
            if self.__mark1VehicleID in positions:
                mark1ArenaPosition = positions[self.__mark1VehicleID]
                resultProgress = self.__calculateProgress(mark1ArenaPosition)
            else:
                resultProgress = defaultProgress
        return (resultHealth, resultProgress)

    def __calculateProgress(self, mark1Position):
        if self.__totalDistance != 0:
            distToTarget = self.__endPoint.distTo(mark1Position) - _END_POINT_OFFSET
            progress = int((1 - distToTarget / self.__totalDistance) * 100)
            if progress > 100:
                progress = 100
        else:
            progress = 0
            LOG_WARNING('Something went wrong... total distance is 0.')
        return progress

    def __updateHealthAndProgress(self):
        health, progress = self.__getHealthAndProgress(self.__currentHealth, self.__currentProgress)
        self.__updateHealth(health)
        self.__updateProgress(progress)

    def __updateHealth(self, health):
        if health != self.__currentHealth:
            self.__currentHealth = health
            self.as_updateHealthS(health)

    def __updateProgress(self, progress):
        if progress != self.__currentProgress and progress > self.__currentProgress:
            self.__currentProgress = progress
            self.as_updateProgressS(progress)
            if self.__currentProgress >= _BATTLE_END_WARNING_DISTANCE_THRESHOLD:
                playMark1AtBaseWarningSound(self.__soundLock)

    def __startUpdateTimer(self):
        self.__stopUpdateTimer()
        self.__timerCallbackID = BigWorld.callback(_UPDATE_INTERVAL, self.__updateTimerCallback)

    def __stopUpdateTimer(self):
        if self.__timerCallbackID is not None:
            BigWorld.cancelCallback(self.__timerCallbackID)
            self.__timerCallbackID = None
        return

    def __updateTimerCallback(self):
        self.__updateHealthAndProgress()
        self.__startUpdateTimer()
