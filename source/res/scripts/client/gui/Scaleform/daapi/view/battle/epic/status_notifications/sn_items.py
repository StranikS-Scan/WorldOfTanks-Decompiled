# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic/status_notifications/sn_items.py
import typing
import BigWorld
from AvatarInputHandler import AvatarInputHandler
from gui.Scaleform.genConsts.EPIC_CONSTS import EPIC_CONSTS
from helpers import dependency
from constants import VEHICLE_MISC_STATUS
from gui.Scaleform.daapi.view.battle.epic.status_notifications.components import StatusNotificationItem
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_TYPES import BATTLE_NOTIFICATIONS_TIMER_TYPES
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, PROGRESS_CIRCLE_TYPE
from gui.impl import backport
from gui.impl.gen import R
from skeletons.gui.battle_session import IBattleSessionProvider
from items import vehicles
if typing.TYPE_CHECKING:
    from gui.battle_control.battle_constants import DestroyTimerViewState, DeathZoneTimerViewState

def getEquipmentById(equipmentId):
    return vehicles.g_cache.equipments()[equipmentId]


def getSmokeDataByPredicate(smokesInfo, predicate):
    if smokesInfo is None or not predicate:
        return (None, None)
    else:
        activeSmokes = list(((sInfo['endTime'], sInfo['equipmentID']) for sInfo in smokesInfo if predicate(sInfo['team'])))
        if activeSmokes:
            maxEndTime, maxEndTimeEquipmentId = max(activeSmokes)
            return (maxEndTime, getEquipmentById(maxEndTimeEquipmentId))
        return (None, None)


class _VehicleStateSN(StatusNotificationItem):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _HIDE_STATES_TRIGGERS = (VEHICLE_VIEW_STATE.DESTROYED, VEHICLE_VIEW_STATE.CREW_DEACTIVATED, VEHICLE_VIEW_STATE.SWITCHING)

    def __init__(self, updateCallback):
        super(_VehicleStateSN, self).__init__(updateCallback)
        ctrl = self._sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
        handler = avatar_getter.getInputHandler()
        if handler is not None:
            if isinstance(handler, AvatarInputHandler):
                handler.onCameraChanged += self.__onCameraChanged
        return

    def _subscribeOnVehControlling(self):
        ctrl = self._sessionProvider.shared.vehicleState
        ctrl.onVehicleControlling += self._onVehicleControlling
        vehicle = ctrl.getControllingVehicle()
        if vehicle is not None:
            self._onVehicleControlling(vehicle)
        return

    def destroy(self):
        ctrl = self._sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
            ctrl.onVehicleControlling -= self._onVehicleControlling
        handler = avatar_getter.getInputHandler()
        if handler is not None:
            if isinstance(handler, AvatarInputHandler):
                handler.onCameraChanged -= self.__onCameraChanged
        super(_VehicleStateSN, self).destroy()
        return

    def _update(self, value):
        pass

    def __onCameraChanged(self, ctrlMode, vehicleID=None):
        if ctrlMode == 'video':
            self._hide()

    def __onVehicleStateUpdated(self, state, value):
        if state in self._HIDE_STATES_TRIGGERS:
            self._hide()
        elif state == self.getItemID():
            self._update(value)

    def _onVehicleControlling(self, vehicle):
        ctrl = self._sessionProvider.shared.vehicleState
        stateValue = ctrl.getStateValue(self.getItemID())
        if stateValue:
            self._update(stateValue)


class FireSN(_VehicleStateSN):

    def __init__(self, updateCallback):
        super(FireSN, self).__init__(updateCallback)
        self._subscribeOnVehControlling()

    def getItemID(self):
        return VEHICLE_VIEW_STATE.FIRE

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.FIRE

    def _update(self, isInFire):
        self._setVisible(isInFire)


class TimeSnapshotHandler(object):

    def __init__(self, updateHandler):
        self._updateHandler = updateHandler
        self._startTime = 0

    def setTimeParams(self, totalTime, finishTime):
        if finishTime:
            self._startTime = finishTime - totalTime
        else:
            self._startTime = BigWorld.serverTime()

    def getCurrentTimeSnapshot(self):
        return BigWorld.serverTime() - self._startTime

    def destroy(self):
        self._updateHandler = None
        return


class SimpleSnapshotHandler(TimeSnapshotHandler):

    def setTimeParams(self, totalTime, finishTime):
        super(SimpleSnapshotHandler, self).setTimeParams(totalTime, finishTime)
        self._updateHandler(self.getCurrentTimeSnapshot(), totalTime)


class TimerSN(_VehicleStateSN):

    def __init__(self, updateCallback):
        super(TimerSN, self).__init__(updateCallback)
        self.__timeHandler = SimpleSnapshotHandler(self.__applySnapshot)

    def setTimeHandler(self, clazz):
        self.__destroyHandler()
        self.__timeHandler = clazz(self.__applySnapshot)

    def destroy(self):
        self.__destroyHandler()
        super(TimerSN, self).destroy()

    def _updateTimeParams(self, totalTime, finishTime):
        self.__timeHandler.setTimeParams(totalTime, finishTime)

    def __applySnapshot(self, currTime, totalTime, isVisible=None, isUpdateRequired=False):
        self._vo['currentTime'] = currTime
        self._vo['totalTime'] = totalTime
        if isVisible is not None:
            pass
        if isUpdateRequired:
            self._sendUpdate()
        return

    def getVO(self):
        vo = super(TimerSN, self).getVO()
        self._vo['currentTime'] = self.__timeHandler.getCurrentTimeSnapshot()
        return vo

    def __destroyHandler(self):
        if self.__timeHandler:
            self.__timeHandler.destroy()
        self.__timeHandler = None
        return


class StunSN(TimerSN):

    def __init__(self, updateCallback):
        super(StunSN, self).__init__(updateCallback)
        self._vo['title'] = backport.text(R.strings.ingame_gui.stun.indicator())
        self._subscribeOnVehControlling()

    def getItemID(self):
        return VEHICLE_VIEW_STATE.STUN

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.STUN

    def _update(self, value):
        if value.duration > 0.0:
            self._updateTimeParams(value.totalTime, value.endTime)
            self._isVisible = True
            self._sendUpdate()
        else:
            self._setVisible(False)


class CaptureBlockSN(TimerSN):

    def __init__(self, updateCallback):
        super(CaptureBlockSN, self).__init__(updateCallback)
        self._vo['title'] = backport.text(R.strings.epic_battle.progress_timers.blocked())
        self._subscribeOnVehControlling()

    def getItemID(self):
        return VEHICLE_VIEW_STATE.CAPTURE_BLOCKED

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.CAPTURE_BLOCK

    def _update(self, duration):
        if duration:
            self._updateTimeParams(duration, 0)
            self._isVisible = True
            self._sendUpdate()
        else:
            self._setVisible(False)


class _DestroyTimerSN(TimerSN):
    _ANY_SUPPORTED_LEVEL = 'anySupportedLevel'

    def __init__(self, updateCallback):
        super(_DestroyTimerSN, self).__init__(updateCallback)
        self._subscribeOnVehControlling()

    def _getSupportedLevel(self):
        raise NotImplementedError


class _DeathZoneSN(_DestroyTimerSN):

    def getItemID(self):
        return VEHICLE_VIEW_STATE.DEATHZONE_TIMER

    def _canBeShown(self, value):
        return self._getSupportedLevel() == value.level

    def _update(self, value):
        if self._canBeShown(value):
            self._isVisible = True
            self._updateTimeParams(value.totalTime, value.finishTime)
            self._sendUpdate()
            return
        self._setVisible(False)


class ResupplyTimerSN(TimerSN):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, updateCallback):
        super(ResupplyTimerSN, self).__init__(updateCallback)
        self.__curPointIdx = -1
        ctrl = self._sessionProvider.dynamic.progressTimer
        if ctrl:
            ctrl.onTimerUpdated += self.__onTimerUpdated
            ctrl.onVehicleEntered += self.__onVehicleEntered
            ctrl.onVehicleLeft += self.__onVehicleLeft
            ctrl.onCircleStatusChanged += self.__onCircleStatusChanged
            ctrl.onProgressUpdate += self.__onProgressUpdate

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.RESUPPLY

    def getItemID(self):
        return VEHICLE_VIEW_STATE.PROGRESS_CIRCLE

    def destroy(self):
        super(ResupplyTimerSN, self).destroy()
        ctrl = self._sessionProvider.dynamic.progressTimer
        if ctrl:
            ctrl.onTimerUpdated -= self.__onTimerUpdated
            ctrl.onVehicleEntered -= self.__onVehicleEntered
            ctrl.onVehicleLeft -= self.__onVehicleLeft
            ctrl.onCircleStatusChanged -= self.__onCircleStatusChanged
            ctrl.onProgressUpdate -= self.__onProgressUpdate
        self.__curPointIdx = -1

    def _update(self, value):
        circleType, isVisible = value
        if circleType is not PROGRESS_CIRCLE_TYPE.RESUPPLY_CIRCLE:
            return
        self._setVisible(isVisible)

    def __onVehicleEntered(self, circleType, pointIdx, state):
        if circleType is not PROGRESS_CIRCLE_TYPE.RESUPPLY_CIRCLE:
            return
        self.__curPointIdx = pointIdx
        self.__updateAdditionalState(state)

    def __onVehicleLeft(self, circleType, _):
        if circleType is not PROGRESS_CIRCLE_TYPE.RESUPPLY_CIRCLE:
            return
        self.__curPointIdx = -1

    def __onCircleStatusChanged(self, circleType, pointIdx, state):
        if circleType is not PROGRESS_CIRCLE_TYPE.RESUPPLY_CIRCLE:
            return
        if self.__curPointIdx != pointIdx:
            return
        if state == EPIC_CONSTS.RESUPPLY_FULL:
            self._updateTimeParams(0, 0)
        elif state == EPIC_CONSTS.RESUPPLY_BLOCKED:
            self._updateTimeParams(0, 0)
        self.__updateAdditionalState(state)

    def __updateAdditionalState(self, state):
        if 'additionalState' in self._vo and self._vo['additionalState'] == state:
            return
        self._vo['additionalState'] = state
        if self._isVisible:
            self._sendUpdate()

    def __onTimerUpdated(self, circleType, pointIdx, timeLeft):
        if circleType is not PROGRESS_CIRCLE_TYPE.RESUPPLY_CIRCLE:
            return
        if pointIdx != self.__curPointIdx:
            return
        self._updateTimeParams(timeLeft, 0)
        if self._isVisible:
            self._sendUpdate()

    def __onProgressUpdate(self, circleType, _, value):
        if circleType is not PROGRESS_CIRCLE_TYPE.RESUPPLY_CIRCLE:
            return
        if 'additionalInfo' in self._vo and self._vo['additionalInfo'] == value:
            return
        self._vo['additionalInfo'] = value
        if self._isVisible:
            self._sendUpdate()


class DeathZoneDamagingSN(_DeathZoneSN):

    def __init__(self, updateCallback):
        super(DeathZoneDamagingSN, self).__init__(updateCallback)
        self._vo['description'] = backport.text(R.strings.epic_battle.destroy_timers.airstrike_txt())

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.DAMAGING_ZONE

    def _canBeShown(self, value):
        if super(DeathZoneDamagingSN, self)._canBeShown(value):
            vehicle = self._sessionProvider.shared.vehicleState.getControllingVehicle()
            isAlive = vehicle is not None and vehicle.isAlive()
            return value.isCausingDamage and isAlive
        else:
            return False

    def _getSupportedLevel(self):
        return None


class DeathZoneDangerSN(_DeathZoneSN):

    def __init__(self, updateCallback):
        super(DeathZoneDangerSN, self).__init__(updateCallback)
        self._vo['description'] = backport.text(R.strings.epic_battle.destroy_timers.airstrike_txt())

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.DEATH_ZONE

    def _canBeShown(self, value):
        return value.needToShow() if super(DeathZoneDangerSN, self)._canBeShown(value) else False

    def _getSupportedLevel(self):
        pass


class DeathZoneWarningSN(_DeathZoneSN):

    def __init__(self, updateCallback):
        super(DeathZoneWarningSN, self).__init__(updateCallback)
        self._vo['description'] = backport.text(R.strings.epic_battle.destroy_timers.airstrike_txt())

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.ORANGE_ZONE

    def _canBeShown(self, value):
        return value.needToShow() if super(DeathZoneWarningSN, self)._canBeShown(value) else False

    def _getSupportedLevel(self):
        pass


class UnderFireSN(_VehicleStateSN):

    def __init__(self, updateCallback):
        super(UnderFireSN, self).__init__(updateCallback)
        self._subscribeOnVehControlling()

    def getItemID(self):
        return VEHICLE_VIEW_STATE.UNDER_FIRE

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.UNDER_FIRE

    def _update(self, isUnderFire):
        self._setVisible(isUnderFire)


class _DestroyMiscTimerSN(_DestroyTimerSN):

    def getItemID(self):
        return VEHICLE_VIEW_STATE.DESTROY_TIMER

    def _getSupportedMiscStatus(self):
        raise NotImplementedError

    def _update(self, value):
        if value.needToCloseAll():
            self._setVisible(False)
            return
        level = value.level
        supportedLevel = self._getSupportedLevel()
        if self._getSupportedMiscStatus() == value.code:
            if value.needToCloseTimer():
                self._setVisible(False)
            elif supportedLevel == self._ANY_SUPPORTED_LEVEL or supportedLevel == level:
                if not value.needToCloseTimer():
                    self._isVisible = True
                    self._updateTimeParams(value.totalTime, 0)
                    self._sendUpdate()
                    return
                self._setVisible(False)


class _OverturnedBaseSN(_DestroyMiscTimerSN):

    def _getSupportedMiscStatus(self):
        return VEHICLE_MISC_STATUS.VEHICLE_IS_OVERTURNED


class OverturnedSN(_OverturnedBaseSN):

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.OVERTURNED

    def _getSupportedLevel(self):
        pass


class HalfOverturnedSN(_OverturnedBaseSN):

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.HALF_OVERTURNED

    def _getSupportedLevel(self):
        pass


class DrownSN(_DestroyMiscTimerSN):

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.DROWN

    def _getSupportedLevel(self):
        return self._ANY_SUPPORTED_LEVEL

    def _getSupportedMiscStatus(self):
        return VEHICLE_MISC_STATUS.VEHICLE_DROWN_WARNING


class RecoverySN(_DestroyMiscTimerSN):

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.RECOVERY

    def getItemID(self):
        return VEHICLE_VIEW_STATE.RECOVERY

    def _getSupportedLevel(self):
        return self._ANY_SUPPORTED_LEVEL

    def _getSupportedMiscStatus(self):
        return VEHICLE_VIEW_STATE.RECOVERY

    def _update(self, value):
        isRecovery, totalTime, _ = value
        if not isRecovery:
            self._setVisible(False)
        else:
            self._isVisible = True
            self._updateTimeParams(totalTime, 0)
            self._sendUpdate()


class SectorAirstrikeSN(_DestroyMiscTimerSN):

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.SECTOR_AIRSTRIKE

    def _getSupportedLevel(self):
        return self._ANY_SUPPORTED_LEVEL

    def _getSupportedMiscStatus(self):
        return VEHICLE_MISC_STATUS.IN_DEATH_ZONE


class _BuffSN(TimerSN):

    def _getInActivationState(self):
        raise NotImplementedError

    def _constructTitle(self, value):
        pass

    def _updateTimeValues(self, value):
        self._updateTimeParams(value.get('duration'), value.get('endTime'))

    def _isValidForUpdateVisibility(self, value):
        isInactivation = value.get('isInactivation')
        return isInactivation is not None and self._getInActivationState() == isInactivation

    def _update(self, value):
        if self._isValidForUpdateVisibility(value):
            self._isVisible = True
            self._updateTimeValues(value)
            self._vo['title'] = self._constructTitle(value)
            self._sendUpdate()
            return
        self._setVisible(False)


class _BaseHealingSN(_BuffSN):

    def getItemID(self):
        return VEHICLE_VIEW_STATE.HEALING


class HealingSN(_BaseHealingSN):

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.HEALING

    def _getInActivationState(self):
        return False

    def _constructTitle(self, value):
        healingString = R.strings.epic_battle.equipment.healPoint.healing
        beingHealedString = R.strings.epic_battle.equipment.healPoint.healed
        isSourceVehicle = value.get('isSourceVehicle', False)
        return backport.text(healingString()) if isSourceVehicle else backport.text(beingHealedString())


class HealingCooldownSN(_BaseHealingSN):

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.HEALING_CD

    def _getInActivationState(self):
        return True

    def _constructTitle(self, value):
        return backport.text(R.strings.epic_battle.equipment.healPoint.healed())


class _BaseRepairingSN(_BuffSN):

    def _constructTitle(self, value):
        return backport.text(R.strings.epic_battle.progress_timers.resupply())

    def getItemID(self):
        return VEHICLE_VIEW_STATE.REPAIR_POINT


class RepairingSN(_BaseRepairingSN):

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.REPAIRING

    def _getInActivationState(self):
        return False


class RepairingCooldownSN(_BaseRepairingSN):

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.REPAIRING_CD

    def _getInActivationState(self):
        return True


class _InspireBaseSN(_BuffSN):

    def __init__(self, updateCallback):
        super(_InspireBaseSN, self).__init__(updateCallback)
        self._subscribeOnVehControlling()

    def _constructTitle(self, value):
        return backport.text(R.strings.epic_battle.inspire.inspired())

    def getItemID(self):
        return VEHICLE_VIEW_STATE.INSPIRE

    def _shouldProcessInspireSource(self):
        return False

    def _isValidForUpdateVisibility(self, value):
        isSourceVehicle = value.get('isSourceVehicle', False)
        isInactivation = value.get('isInactivation')
        primary = value.get('primary', True)
        return isInactivation is not None and primary and self._getInActivationState() == isInactivation and isSourceVehicle == self._shouldProcessInspireSource()


class InspireSN(_InspireBaseSN):

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.INSPIRE

    def _getInActivationState(self):
        return False


class InspireCooldownSN(_InspireBaseSN):

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.INSPIRE_CD

    def _getInActivationState(self):
        return True


class InspireSourceSN(_InspireBaseSN):

    def _constructTitle(self, value):
        return backport.text(R.strings.epic_battle.inspire.inspiring())

    def _shouldProcessInspireSource(self):
        return True

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.INSPIRE_SOURCE

    def _getInActivationState(self):
        return False


class InspireInactivationSourceSN(InspireSourceSN):

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.INSPIRE_INACTIVATION_SOURCE

    def _getInActivationState(self):
        return True


class _SmokeBase(TimerSN):

    def __init__(self, updateCallback):
        super(_SmokeBase, self).__init__(updateCallback)
        self._subscribeOnVehControlling()

    def destroy(self):
        self._smokeEquipment = None
        super(_SmokeBase, self).destroy()
        return

    def getItemID(self):
        return VEHICLE_VIEW_STATE.SMOKE

    def _isFitByTeam(self, teamID):
        raise NotImplementedError

    def _update(self, smokesInfo):
        endTime, equipment = getSmokeDataByPredicate(smokesInfo, self._isFitByTeam)
        if endTime is None:
            if self._isVisible:
                self._setVisible(False)
            return
        else:
            self._updateTimeParams(equipment.totalDuration, endTime)
            self._isVisible = True
            self._sendUpdate()
            return


class SmokeSN(_SmokeBase):

    def __init__(self, updateCallback):
        super(SmokeSN, self).__init__(updateCallback)
        self._vo['title'] = backport.text(R.strings.epic_battle.smoke.InAllySmoke())

    def _isFitByTeam(self, teamID):
        return teamID == avatar_getter.getPlayerTeam()

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.SMOKE


class EnemySmokeSN(_SmokeBase):

    def __init__(self, updateCallback):
        super(EnemySmokeSN, self).__init__(updateCallback)
        self._vo['title'] = backport.text(R.strings.epic_battle.smoke.InEnemySmoke())

    def _isFitByTeam(self, teamID):
        return teamID != avatar_getter.getPlayerTeam()

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.DAMAGING_SMOKE


class _StealthBaseSN(_BuffSN):

    def __init__(self, updateCallback):
        super(_StealthBaseSN, self).__init__(updateCallback)
        self._subscribeOnVehControlling()

    def _updateTimeValues(self, value):
        self._updateTimeParams(value.duration, value.endTime)

    def _isValidForUpdateVisibility(self, value):
        return value.duration > 0.0 and value.isActive == self._getInActivationState()

    def getItemID(self):
        return VEHICLE_VIEW_STATE.STEALTH_RADAR


class StealthSN(_StealthBaseSN):

    def _constructTitle(self, value):
        return backport.text(R.strings.epic_battle.stealthRadar.active())

    def _getInActivationState(self):
        return True

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.STEALTH_RADAR


class StealthInactiveSN(_StealthBaseSN):

    def _constructTitle(self, value):
        equipment = getEquipmentById(value['equipmentID'])
        return backport.text(R.strings.epic_battle.stealthRadar.inactive(), activationDelay=int(equipment.inactivationDelay))

    def _getInActivationState(self):
        return False

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.STEALTH_RADAR_INACTIVE
