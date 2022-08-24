# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/battle/status_notifications/sn_items.py
import BigWorld
from AvatarInputHandler import AvatarInputHandler
from helpers import dependency
from battle_royale.gui.constants import BattleRoyaleEquipments, BattleRoyaleComponents
from battle_royale.gui.Scaleform.daapi.view.battle.status_notifications.components import StatusNotificationItem
from constants import VEHICLE_MISC_STATUS, LootAction, LOOT_TYPE
from gui.Scaleform.daapi.view.common.battle_royale.br_helpers import getSmokeDataByPredicate, getEquipmentById
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_TYPES import BATTLE_NOTIFICATIONS_TIMER_TYPES
from gui.Scaleform.genConsts.BATTLE_ROYAL_CONSTS import BATTLE_ROYAL_CONSTS
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.impl import backport
from gui.impl.gen import R
from items import vehicles
from skeletons.gui.battle_session import IBattleSessionProvider
from battle_royale.gui.battle_control.battle_constants import BrTimerViewState

class _VehicleStateSN(StatusNotificationItem):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _HIDE_STATES_TRIGGERS = (VEHICLE_VIEW_STATE.DESTROYED, VEHICLE_VIEW_STATE.CREW_DEACTIVATED, VEHICLE_VIEW_STATE.SWITCHING)

    def __init__(self, updateCallback):
        super(_VehicleStateSN, self).__init__(updateCallback)
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
        ctrl.onVehicleControlling += self._onVehicleControlling

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

    def _update(self, value):
        pass

    def __onCameraChanged(self, ctrlMode, vehicleID=None):
        if ctrlMode == 'video':
            self._hide()

    def __onEquipmentComponentUpdated(self, _, vehicleID, equipmentInfo):
        if vehicleID == BigWorld.player().getObservedVehicleID():
            self._update(equipmentInfo)

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

    def _getEquipmentName(self):
        pass

    def _getEquipmentComponentName(self):
        pass


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


class DeathZoneDamagingSN(_DeathZoneSN):

    def __init__(self, updateCallback):
        super(DeathZoneDamagingSN, self).__init__(updateCallback)
        self._vo['description'] = backport.text(R.strings.battle_royale.timersPanel.deathZone())

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
        self._vo['description'] = backport.text(R.strings.battle_royale.timersPanel.deathZone())

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.DEATH_ZONE

    def _canBeShown(self, value):
        return value.needToShow() if super(DeathZoneDangerSN, self)._canBeShown(value) else False

    def _getSupportedLevel(self):
        return BrTimerViewState.CRITICAL


class DeathZoneWarningSN(_DeathZoneSN):

    def __init__(self, updateCallback):
        super(DeathZoneWarningSN, self).__init__(updateCallback)
        self._vo['description'] = backport.text(R.strings.battle_royale.timersPanel.orangeZone())

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.ORANGE_ZONE

    def _canBeShown(self, value):
        return value.needToShow() if super(DeathZoneWarningSN, self)._canBeShown(value) else False

    def _getSupportedLevel(self):
        return BrTimerViewState.WARNING


class _DestroyMiscTimerSN(_DestroyTimerSN):

    def getItemID(self):
        return VEHICLE_VIEW_STATE.DESTROY_TIMER

    def _getSupportedMiscStatus(self):
        raise NotImplementedError

    def _update(self, value):
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

    def __init__(self, updateCallback):
        super(HalfOverturnedSN, self).__init__(updateCallback)
        self._vo['description'] = backport.text(R.strings.battle_royale.timersPanel.halfOverturned())

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


class LootPickUpSN(TimerSN):

    def __init__(self, updateCallback):
        super(LootPickUpSN, self).__init__(updateCallback)
        self.__loots = {}
        self.__vehicle = None
        self._subscribeOnVehControlling()
        return

    def destroy(self):
        self.__loots = None
        super(LootPickUpSN, self).destroy()
        return

    def getItemID(self):
        return VEHICLE_VIEW_STATE.LOOT

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.LOOT_PICKUP

    def _update(self, value):
        lootID, lootType, action, serverTime = value
        if action == LootAction.PICKUP_STARTED:
            self.__showLootTimer(lootID, lootType, serverTime)
        else:
            self.__hideLootTimer(lootID)

    def _onVehicleControlling(self, vehicle):
        if self.__vehicle != vehicle:
            self.__vehicle = vehicle
            self.__loots.clear()
            super(LootPickUpSN, self)._onVehicleControlling(vehicle)

    def __showLootTimer(self, lootID, lootTypeID, pickupTime):
        time = BigWorld.serverTime()
        if not self.__loots:
            self._isVisible = True
        self.__loots[lootID] = (lootTypeID, time + pickupTime)
        timeLeft = max((loot_time for _, loot_time in self.__loots.values()))
        timeLeft -= time
        self.__updateText()
        self._updateTimeParams(timeLeft, 0)
        self._sendUpdate()

    def __hideLootTimer(self, lootID):
        if lootID in self.__loots:
            del self.__loots[lootID]
            self.__updateText()
            self._sendUpdate()
        if not self.__loots:
            self._setVisible(False)

    def __updateText(self):
        self._vo['title'] = backport.text(R.strings.battle_royale.timersPanel.lootPickup(), lootType=self.__getLootType())

    def __getLootType(self):
        count = len(self.__loots)
        if count > 1:
            return backport.text(R.strings.battle_royale.loot.multiple(), count=count)
        if count > 0:
            lootType, _ = self.__loots.values()[0]
            if lootType == LOOT_TYPE.BASIC:
                return backport.text(R.strings.battle_royale.loot.basic())
            if lootType == LOOT_TYPE.ADVANCED:
                return backport.text(R.strings.battle_royale.loot.advanced())
            if lootType == LOOT_TYPE.AIRDROP:
                return backport.text(R.strings.battle_royale.loot.airdrop())
            if lootType == LOOT_TYPE.CORPSE:
                return backport.text(R.strings.battle_royale.loot.corpse())


class _BuffSN(TimerSN):

    def _constructTitle(self, value):
        pass

    def _update(self, value):
        duration = value['duration']
        if duration > 0:
            self._isVisible = True
            self._updateTimeParams(duration, value['endTime'])
            self._vo['title'] = self._constructTitle(value)
            self._sendUpdate()
        else:
            self._setVisible(False)


class ShotPassionSN(_BuffSN):

    def __init__(self, updateCallback):
        super(ShotPassionSN, self).__init__(updateCallback)
        eqID = vehicles.g_cache.equipmentIDs().get(self._getEquipmentName())
        self.__eq = vehicles.g_cache.equipments()[eqID]
        self.__maxStage = int(round(self.__eq.maxDamageIncreasePerShot / self.__eq.damageIncreasePerShot))
        self._subscribeOnVehControlling()

    def _update(self, value):
        stage = value.get('stage', 0)
        self._vo['additionalInfo'] = self.__constructCounter(stage)
        self._vo['additionalState'] = self.__getCounterState(stage)
        super(ShotPassionSN, self)._update(value)

    def _constructTitle(self, value):
        return backport.text(R.strings.battle_royale.timersPanel.shotPassion())

    def getItemID(self):
        return VEHICLE_VIEW_STATE.SHOT_PASSION

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.SHOT_PASSION

    def _getEquipmentName(self):
        return BattleRoyaleEquipments.SHOT_PASSION

    def _getEquipmentComponentName(self):
        return BattleRoyaleComponents.SHOT_PASSION

    def __getCounterState(self, stage):
        if stage == 0:
            return BATTLE_ROYAL_CONSTS.COUNTER_STATE_INITIAL
        return BATTLE_ROYAL_CONSTS.COUNTER_STATE_EXTRA if stage < self.__maxStage else BATTLE_ROYAL_CONSTS.COUNTER_STATE_MAX

    def __constructCounter(self, stage):
        return backport.text(R.strings.common.multiplier()) + str(stage)


class _BaseHealingSN(_BuffSN):

    def _getInActivationState(self):
        raise NotImplementedError

    def _update(self, value):
        isInactivation = value.get('isInactivation')
        duration = value.get('duration')
        if isInactivation is not None and self._getInActivationState() == isInactivation and duration > 0.0:
            self._isVisible = True
            self._updateTimeParams(value.get('duration'), value.get('endTime'))
            self._vo['title'] = self._constructTitle(value)
            self._sendUpdate()
            return
        else:
            self._setVisible(False)
            return

    def getItemID(self):
        return VEHICLE_VIEW_STATE.HEALING


class HealingSN(_BaseHealingSN):

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.HEALING

    def _getInActivationState(self):
        return False

    def _constructTitle(self, value):
        healingString = R.strings.battle_royale.equipment.healPoint.healing
        beingHealedString = R.strings.battle_royale.equipment.healPoint.healed
        isSourceVehicle = value.get('isSourceVehicle', False)
        return backport.text(healingString()) if isSourceVehicle else backport.text(beingHealedString())


class HealingCooldownSN(_BaseHealingSN):

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.HEALING_CD

    def _getInActivationState(self):
        return True

    def _constructTitle(self, value):
        return backport.text(R.strings.battle_royale.equipment.healPoint.healed())


class _BaseRepairingSN(_BuffSN):

    def _constructTitle(self, value):
        return backport.text(R.strings.battle_royale.equipment.repairPoint())

    def getItemID(self):
        return VEHICLE_VIEW_STATE.REPAIR_POINT

    def _getInActivationState(self):
        raise NotImplementedError

    def _update(self, value):
        isInactivation = value.get('isInactivation')
        if isInactivation is not None and self._getInActivationState() == isInactivation:
            self._isVisible = True
            self._updateTimeParams(value.get('duration'), value.get('endTime'))
            self._vo['title'] = self._constructTitle(value)
            self._sendUpdate()
            return
        else:
            self._setVisible(False)
            return


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


class InspireSN(_BuffSN):

    def __init__(self, updateCallback):
        super(InspireSN, self).__init__(updateCallback)
        self._subscribeOnVehControlling()

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.INSPIRE

    def _constructTitle(self, value):
        return backport.text(R.strings.battle_royale.timersPanel.inspired())

    def getItemID(self):
        return VEHICLE_VIEW_STATE.INSPIRE


class BerserkerSN(_BuffSN):

    def __init__(self, updateCallback):
        super(BerserkerSN, self).__init__(updateCallback)
        self._vo['title'] = backport.text(R.strings.battle_royale.equipment.berserk.active())

    def getItemID(self):
        return VEHICLE_VIEW_STATE.BERSERKER

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.BERSERKER


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

    def _isFitByEquipmentId(self, equipmentId):
        raise NotImplementedError

    def _update(self, smokesInfo):
        endTime, equipment = getSmokeDataByPredicate(smokesInfo, self._isFitByEquipmentId)
        if endTime is None:
            if self._isVisible:
                self._setVisible(False)
            return
        else:
            self._updateTimeParams(equipment.totalDuration, endTime)
            self._sendUpdate()
            self._setVisible(True)
            return


class SmokeSN(_SmokeBase):

    def __init__(self, updateCallback):
        super(SmokeSN, self).__init__(updateCallback)
        self._vo['title'] = backport.text(R.strings.epic_battle.smoke.In_smoke())

    def _isFitByEquipmentId(self, equipmentId):
        equipment = getEquipmentById(equipmentId)
        return equipment.dotParams is None if equipment else False

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.SMOKE


class DamagingSmokeSN(_SmokeBase):

    def __init__(self, updateCallback):
        super(DamagingSmokeSN, self).__init__(updateCallback)
        self._vo['title'] = backport.text(R.strings.battle_royale.timersPanel.damagingSmoke())

    def _isFitByEquipmentId(self, equipmentId):
        equipment = getEquipmentById(equipmentId)
        return equipment.dotParams is not None if equipment else False

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.DAMAGING_SMOKE


class DamagingCorrodingShotSN(_SmokeBase):

    def _update(self, data):
        duration = data.get('duration', 0)
        if duration > 0.0:
            self._vo['title'] = backport.text(R.strings.battle_royale.timersPanel.damagingCorrodingShot())
            self._setVisible(True)
            self._updateTimeParams(duration, 0.0)
            self._sendUpdate()
        else:
            self._setVisible(False)

    def getItemID(self):
        return VEHICLE_VIEW_STATE.CORRODING_SHOT

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.CORRODING_SHOT


class FireCircleSN(_SmokeBase):

    def _update(self, value):
        duration = value.get('duration', 0.0) if isinstance(value, dict) else value
        if duration > 0.0:
            self._vo['title'] = backport.text(R.strings.battle_royale.timersPanel.fireCircle())
            self._setVisible(True)
            self._updateTimeParams(duration, 0.0)
            self._sendUpdate()
        else:
            self._setVisible(False)

    def getItemID(self):
        return VEHICLE_VIEW_STATE.FIRE_CIRCLE

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.FIRE_CIRCLE


class ThunderStrikeSN(_SmokeBase):

    def _update(self, value):
        duration = value.get('duration', 0.0)
        if duration > 0.0:
            self._vo['title'] = backport.text(R.strings.battle_royale.timersPanel.thunderStrike())
            self._setVisible(True)
            self._updateTimeParams(duration, 0.0)
            self._sendUpdate()
        else:
            self._setVisible(False)

    def getItemID(self):
        return VEHICLE_VIEW_STATE.THUNDER_STRIKE

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.THUNDER_STRIKE


class AdaptationHealthRestoreSN(TimerSN):

    def __init__(self, updateCallback):
        super(AdaptationHealthRestoreSN, self).__init__(updateCallback)
        self._vo['additionalState'] = BATTLE_ROYAL_CONSTS.COUNTER_STATE_INITIAL

    def _update(self, value):
        restoreHealth = value.get('restoreHealth')
        duration = value.get('duration')
        if duration is not None:
            if duration > 0.0:
                self._vo['title'] = backport.text(R.strings.battle_royale.timersPanel.hpRestoreOnDamage())
                self._setVisible(True)
                self._updateTimeParams(duration, 0.0)
                self._sendUpdate()
            else:
                self._setVisible(False)
                self._vo['additionalState'] = BATTLE_ROYAL_CONSTS.COUNTER_STATE_INITIAL
                self._sendUpdate()
            return
        else:
            if restoreHealth is not None:
                self._vo['additionalInfo'] = ''.join(('+', str(restoreHealth)))
                if restoreHealth > 0:
                    self._vo['additionalState'] = BATTLE_ROYAL_CONSTS.COUNTER_STATE_EXTRA
                self._sendUpdate()
            return

    def getItemID(self):
        return VEHICLE_VIEW_STATE.ADAPTATION_HEALTH_RESTORE

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.HP_RESTORE_ON_DAMAGE
