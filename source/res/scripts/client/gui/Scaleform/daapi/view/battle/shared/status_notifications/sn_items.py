# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/status_notifications/sn_items.py
import typing
import BigWorld
from AvatarInputHandler import AvatarInputHandler
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from constants import VEHICLE_MISC_STATUS
from constants import StunTypes
from gui.Scaleform.daapi.view.battle.shared.status_notifications.components import StatusNotificationItem
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_TYPES import BATTLE_NOTIFICATIONS_TIMER_TYPES
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, TIMER_VIEW_STATE
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from gui.battle_control.battle_constants import DestroyTimerViewState, DeathZoneTimerViewState

class LocalizationProvider(object):

    @property
    def _stringResource(self):
        raise NotImplementedError


class TimeSnapshotHandler(object):

    def __init__(self, updateHandler):
        self._updateHandler = updateHandler
        self._startTime = 0

    def setTimeParams(self, totalTime, finishTime):
        if finishTime:
            self._startTime = finishTime - totalTime
        else:
            self._startTime = BigWorld.serverTime()

    def setCallback(self, delay, updateFunc):
        pass

    def stopCallback(self):
        pass

    def getCurrentTimeSnapshot(self):
        return BigWorld.serverTime() - self._startTime

    def destroy(self):
        self._updateHandler = None
        return


class SimpleSnapshotHandler(TimeSnapshotHandler):

    def setTimeParams(self, totalTime, finishTime):
        super(SimpleSnapshotHandler, self).setTimeParams(totalTime, finishTime)
        self._updateHandler(self.getCurrentTimeSnapshot(), totalTime)


class _VehicleStateSN(StatusNotificationItem):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _HIDE_STATES_TRIGGERS = (VEHICLE_VIEW_STATE.DESTROYED, VEHICLE_VIEW_STATE.CREW_DEACTIVATED, VEHICLE_VIEW_STATE.SWITCHING)

    def start(self):
        super(_VehicleStateSN, self).start()
        ctrl = self._sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
            contextID = self._getEquipmentName()
            if contextID:
                ctrl.onEquipmentComponentUpdated.subscribe(self.__onEquipmentComponentUpdated, contextID)
        handler = avatar_getter.getInputHandler()
        if handler is not None:
            if isinstance(handler, AvatarInputHandler):
                handler.onCameraChanged += self.__onCameraChanged
        return

    def _subscribeOnVehControlling(self):
        ctrl = self._sessionProvider.shared.vehicleState
        if ctrl is not None:
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
            ctrl.onEquipmentComponentUpdated.unsubscribe(self.__onEquipmentComponentUpdated)
        handler = avatar_getter.getInputHandler()
        if handler is not None:
            if isinstance(handler, AvatarInputHandler):
                handler.onCameraChanged -= self.__onCameraChanged
        super(_VehicleStateSN, self).destroy()
        return

    def _getTitle(self, value):
        pass

    def _getDescription(self, value):
        pass

    def _getEquipmentName(self):
        pass

    def _onVehicleControlling(self, vehicle):
        ctrl = self._sessionProvider.shared.vehicleState
        stateValue = ctrl.getStateValue(self.getItemID())
        if stateValue:
            self.__update(stateValue)

    def _updateText(self, value):
        self._vo['title'] = self._getTitle(value)
        self._vo['description'] = self._getDescription(value)

    def _update(self, value):
        pass

    def __onCameraChanged(self, ctrlMode, vehicleID=None):
        if ctrlMode == 'video':
            self._hide()

    def __onVehicleStateUpdated(self, state, value):
        if state in self._HIDE_STATES_TRIGGERS:
            self._hide()
        elif state == self.getItemID():
            self.__update(value)

    def __onEquipmentComponentUpdated(self, _, vehicleID, equipmentInfo):
        if vehicleID == BigWorld.player().getObservedVehicleID():
            self._update(equipmentInfo)

    def __update(self, value):
        self._updateText(value)
        self._update(value)


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

    def getVO(self):
        vo = super(TimerSN, self).getVO()
        self._vo['currentTime'] = self.__timeHandler.getCurrentTimeSnapshot()
        return vo

    def _updateTimeParams(self, totalTime, finishTime):
        self.__timeHandler.setTimeParams(totalTime, finishTime)

    def __applySnapshot(self, currTime, totalTime, isUpdateRequired=False):
        self._vo['currentTime'] = currTime
        self._vo['totalTime'] = totalTime
        if isUpdateRequired:
            self._sendUpdate()

    def _setCallback(self, delay, updateFunc):
        self.__timeHandler.setCallback(delay, updateFunc)

    def _stopCallback(self):
        self.__timeHandler.stopCallback()

    def __destroyHandler(self):
        if self.__timeHandler:
            self.__timeHandler.destroy()
        self.__timeHandler = None
        return


class _DestroyTimerSN(TimerSN):
    _ANY_SUPPORTED_LEVEL = 'anySupportedLevel'

    def start(self):
        super(_DestroyTimerSN, self).start()
        self._subscribeOnVehControlling()

    def _getSupportedLevel(self):
        raise NotImplementedError


class _DeathZoneSN(LocalizationProvider, _DestroyTimerSN):

    def getItemID(self):
        return VEHICLE_VIEW_STATE.DEATHZONE_TIMER

    def _getDescription(self, value):
        return backport.text(self._stringResource.deathZone())

    def _canBeShown(self, value):
        return self._getSupportedLevel() == value.level

    def _update(self, value):
        if self._canBeShown(value):
            self._isVisible = True
            self._updateTimeParams(value.totalTime, value.finishTime)
            self._sendUpdate()
            return
        self._setVisible(False)


class StaticDeathZoneSN(_DestroyTimerSN):

    def getItemID(self):
        return VEHICLE_VIEW_STATE.DEATHZONE

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.SECTOR_AIRSTRIKE

    def _getDescription(self, value):
        return backport.text(R.strings.ingame_gui.statusNotificationTimers.staticDeathZone())

    def _update(self, value):
        visible, playerEntering, strikeTime, waveDuration = value
        self._isVisible = visible
        if playerEntering:
            self._updateTimeParams(waveDuration, strikeTime)
        else:
            self._updateTimeParams(0, 0)
        self._sendUpdate()

    def _getSupportedLevel(self):
        return None


class DeathZoneDamagingSN(_DeathZoneSN):

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

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.DEATH_ZONE

    def _canBeShown(self, value):
        return value.needToShow() if super(DeathZoneDangerSN, self)._canBeShown(value) else False

    def _getSupportedLevel(self):
        return TIMER_VIEW_STATE.CRITICAL


class DeathZoneWarningSN(_DeathZoneSN):

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.ORANGE_ZONE

    def _canBeShown(self, value):
        return value.needToShow() if super(DeathZoneWarningSN, self)._canBeShown(value) else False

    def _getSupportedLevel(self):
        return TIMER_VIEW_STATE.WARNING


class DestroyMiscTimerSN(_DestroyTimerSN):

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


class _OverturnedBaseSN(LocalizationProvider, DestroyMiscTimerSN):

    def __init__(self, updateCallback):
        super(_OverturnedBaseSN, self).__init__(updateCallback)
        self._vo['description'] = self._getDescription()

    def _getSupportedMiscStatus(self):
        return VEHICLE_MISC_STATUS.VEHICLE_IS_OVERTURNED

    def _getDescription(self, value=None):
        liftOverEnabled = ARENA_BONUS_TYPE_CAPS.checkAny(BigWorld.player().arenaBonusType, ARENA_BONUS_TYPE_CAPS.LIFT_OVER)
        return backport.text(R.strings.ingame_gui.destroyTimer.liftOver()) if liftOverEnabled else ''


class OverturnedSN(_OverturnedBaseSN):

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.OVERTURNED

    def _getSupportedLevel(self):
        return TIMER_VIEW_STATE.CRITICAL


class HalfOverturnedSN(_OverturnedBaseSN):

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.HALF_OVERTURNED

    def _getSupportedLevel(self):
        return TIMER_VIEW_STATE.WARNING


class DrownSN(DestroyMiscTimerSN):

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.DROWN

    def _getSupportedLevel(self):
        return self._ANY_SUPPORTED_LEVEL

    def _getSupportedMiscStatus(self):
        return VEHICLE_MISC_STATUS.VEHICLE_DROWN_WARNING


class UnderFireSN(_VehicleStateSN):

    def start(self):
        super(UnderFireSN, self).start()
        self._subscribeOnVehControlling()

    def getItemID(self):
        return VEHICLE_VIEW_STATE.UNDER_FIRE

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.UNDER_FIRE

    def _update(self, isUnderFire):
        self._setVisible(isUnderFire)


class FireSN(_VehicleStateSN):

    def start(self):
        super(FireSN, self).start()
        self._subscribeOnVehControlling()

    def getItemID(self):
        return VEHICLE_VIEW_STATE.FIRE

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.FIRE

    def _update(self, isInFire):
        self._setVisible(isInFire)


class StunSN(TimerSN):

    def __init__(self, updateCallback):
        super(StunSN, self).__init__(updateCallback)
        self._vo['title'] = backport.text(R.strings.ingame_gui.stun.indicator())

    def start(self):
        super(StunSN, self).start()
        self._subscribeOnVehControlling()

    def getItemID(self):
        return VEHICLE_VIEW_STATE.STUN

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.STUN

    def _update(self, value):
        if value.duration > 0.0 and value.stunType == self._getStunType():
            self._updateTimeParams(value.totalTime, value.endTime)
            self._isVisible = True
            self._sendUpdate()
        else:
            self._setVisible(False)

    def _getTitle(self, value):
        return backport.text(R.strings.ingame_gui.stun.indicator())

    def _getStunType(self):
        return StunTypes.DEFAULT.value


class StunFlameSN(StunSN):

    def __init__(self, updateCallback):
        super(StunFlameSN, self).__init__(updateCallback)
        self._vo['title'] = backport.text(R.strings.ingame_gui.stunFlame.indicator())

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.STUN_FLAME

    def _getTitle(self, value):
        return backport.text(R.strings.ingame_gui.stunFlame.indicator())

    def _getStunType(self):
        return StunTypes.FLAME.value


class _SmokeBase(LocalizationProvider, TimerSN):

    def start(self):
        super(_SmokeBase, self).start()
        self._subscribeOnVehControlling()

    def getItemID(self):
        return VEHICLE_VIEW_STATE.SMOKE

    def _update(self, smokesInfo):
        endTime, equipment = self._getSmokeData(smokesInfo)
        if endTime is None:
            if self._isVisible:
                self._setVisible(False)
            return
        else:
            self._updateTimeParams(equipment.expireDelay if smokesInfo['expiring'] else equipment.totalDuration, endTime)
            self._isVisible = True
            self._sendUpdate()
            return

    def _getSmokeData(self, smokesInfo):
        raise NotImplementedError


class SmokeSN(_SmokeBase):

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.SMOKE

    def _getTitle(self, value):
        return backport.text(self._stringResource.smoke.ally())


class EnemySmokeSN(_SmokeBase):

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.DAMAGING_SMOKE

    def _getTitle(self, value):
        return backport.text(self._stringResource.smoke.enemy())


class DamagingSmokeSN(_SmokeBase):

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.DAMAGING_SMOKE

    def _getTitle(self, value):
        return backport.text(self._stringResource.smoke.damaging())


class BuffSN(LocalizationProvider, TimerSN):

    def _getInActivationState(self):
        raise NotImplementedError

    def _updateTimeValues(self, value):
        self._updateTimeParams(value.get('duration'), value.get('endTime'))

    def _isValidForUpdateVisibility(self, value):
        isInactivation = value.get('isInactivation')
        return isInactivation is not None and self._getInActivationState() == isInactivation

    def _update(self, value):
        if self._isValidForUpdateVisibility(value):
            self._isVisible = True
            self._updateTimeValues(value)
            self._sendUpdate()
            return
        self._setVisible(False)


class _BaseHealingSN(BuffSN):

    def getItemID(self):
        return VEHICLE_VIEW_STATE.HEALING


class HealingSN(_BaseHealingSN):

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.HEALING

    def _getInActivationState(self):
        return False

    def _getTitle(self, value):
        healingString = self._stringResource.healPoint.healing
        beingHealedString = self._stringResource.healPoint.healed
        isSourceVehicle = value.get('isSourceVehicle', False)
        return backport.text(healingString()) if isSourceVehicle else backport.text(beingHealedString())


class HealingCooldownSN(_BaseHealingSN):

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.HEALING_CD

    def _getInActivationState(self):
        return True

    def _getTitle(self, value):
        return backport.text(self._stringResource.healPoint.healed())


class _BaseRepairingSN(BuffSN):

    def getItemID(self):
        return VEHICLE_VIEW_STATE.REPAIR_POINT

    def _getTitle(self, value):
        return backport.text(self._stringResource.repairPoint())


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


class _InspireBaseSN(BuffSN):

    def start(self):
        super(_InspireBaseSN, self).start()
        self._subscribeOnVehControlling()

    def getItemID(self):
        return VEHICLE_VIEW_STATE.INSPIRE

    def _shouldProcessInspireSource(self):
        return False

    def _isValidForUpdateVisibility(self, value):
        isValidForUpdateVisibility = super(_InspireBaseSN, self)._isValidForUpdateVisibility(value)
        primary = bool(value.get('primary', 1))
        isSourceVehicle = bool(value.get('isSourceVehicle', 0))
        isValidSource = isSourceVehicle is self._shouldProcessInspireSource()
        return isValidForUpdateVisibility and primary and isValidSource

    def _getTitle(self, value):
        return backport.text(self._stringResource.inspire.inspired())


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

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.INSPIRE_SOURCE

    def _getTitle(self, value):
        return backport.text(self._stringResource.inspire.inspiring())

    def _shouldProcessInspireSource(self):
        return True

    def _getInActivationState(self):
        return False


class InspireInactivationSourceSN(InspireSourceSN):

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.INSPIRE_INACTIVATION_SOURCE

    def _getInActivationState(self):
        return True
