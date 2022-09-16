# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/battle/status_notifications/sn_items.py
import BigWorld
from constants import LootAction, LOOT_TYPE
from gui.Scaleform.daapi.view.battle.shared.status_notifications import sn_items
from gui.Scaleform.daapi.view.common.battle_royale.br_helpers import getSmokeDataByPredicate, getEquipmentById
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_TYPES import BATTLE_NOTIFICATIONS_TIMER_TYPES
from gui.Scaleform.genConsts.BATTLE_ROYAL_CONSTS import BATTLE_ROYAL_CONSTS
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.impl import backport
from gui.impl.gen import R
from items import vehicles
from battle_royale.gui.constants import BattleRoyaleEquipments

class _BRLocalizationProvider(sn_items.LocalizationProvider):

    @property
    def _stringResource(self):
        return R.strings.battle_royale.statusNotificationTimers


class BRHalfOverturnedSN(_BRLocalizationProvider, sn_items.HalfOverturnedSN):

    def _getIsPulseVisible(self):
        return True

    def _getDescription(self, *args):
        return backport.text(self._stringResource.halfOverturned())


class BRDeathZoneDamagingSN(_BRLocalizationProvider, sn_items.DeathZoneDamagingSN):
    pass


class BRDeathZoneDangerSN(_BRLocalizationProvider, sn_items.DeathZoneDangerSN):
    pass


class BRDeathZoneWarningSN(_BRLocalizationProvider, sn_items.DeathZoneWarningSN):
    pass


class LootPickUpSN(_BRLocalizationProvider, sn_items.TimerSN):

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
        self._vo['title'] = backport.text(self._stringResource.loot.pickup(), lootType=self.__getLootType())

    def __getLootType(self):
        count = len(self.__loots)
        if count > 1:
            return backport.text(self._stringResource.loot.multiple(), count=count)
        if count > 0:
            lootType, _ = self.__loots.values()[0]
            if lootType == LOOT_TYPE.BASIC:
                return backport.text(self._stringResource.loot.basic())
            if lootType == LOOT_TYPE.ADVANCED:
                return backport.text(self._stringResource.loot.advanced())
            if lootType == LOOT_TYPE.AIRDROP:
                return backport.text(self._stringResource.loot.airdrop())
            if lootType == LOOT_TYPE.CORPSE:
                return backport.text(self._stringResource.loot.corpse())


class BRBuffSN(_BRLocalizationProvider, sn_items.BuffSN):

    def _updateTimeValues(self, value):
        self._updateTimeParams(value['duration'], value['endTime'])

    def _isValidForUpdateVisibility(self, value):
        return value['duration'] > 0


class ShotPassionSN(BRBuffSN):

    def __init__(self, updateCallback):
        super(ShotPassionSN, self).__init__(updateCallback)
        eqID = vehicles.g_cache.equipmentIDs().get(self._getEquipmentName())
        self.__eq = vehicles.g_cache.equipments()[eqID]
        self.__maxStage = int(round(self.__eq.maxDamageIncreasePerShot / self.__eq.damageIncreasePerShot))
        self._subscribeOnVehControlling()

    def getItemID(self):
        return VEHICLE_VIEW_STATE.SHOT_PASSION

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.SHOT_PASSION

    def _update(self, value):
        stage = value.get('stage', 0)
        self._vo['additionalInfo'] = self.__constructCounter(stage)
        self._vo['additionalState'] = self.__getCounterState(stage)
        super(ShotPassionSN, self)._update(value)

    def _getTitle(self, value):
        return backport.text(self._stringResource.shotPassion())

    def _getEquipmentName(self):
        return BattleRoyaleEquipments.SHOT_PASSION

    def __getCounterState(self, stage):
        if stage == 0:
            return BATTLE_ROYAL_CONSTS.COUNTER_STATE_INITIAL
        return BATTLE_ROYAL_CONSTS.COUNTER_STATE_EXTRA if stage < self.__maxStage else BATTLE_ROYAL_CONSTS.COUNTER_STATE_MAX

    def __constructCounter(self, stage):
        return backport.text(R.strings.common.multiplier()) + str(stage)


class BRHealingSN(_BRLocalizationProvider, sn_items.HealingSN):

    def _isValidForUpdateVisibility(self, value):
        return value.get('duration', 0) > 0.0 and super(BRHealingSN, self)._isValidForUpdateVisibility(value)


class BRHealingCooldownSN(_BRLocalizationProvider, sn_items.HealingCooldownSN):

    def _isValidForUpdateVisibility(self, value):
        return value.get('duration', 0) > 0.0 and super(BRHealingCooldownSN, self)._isValidForUpdateVisibility(value)


class BRRepairingSN(_BRLocalizationProvider, sn_items.RepairingSN):
    pass


class BRRepairingCooldownSN(_BRLocalizationProvider, sn_items.RepairingCooldownSN):
    pass


class BRInspireSN(BRBuffSN):

    def __init__(self, updateCallback):
        super(BRInspireSN, self).__init__(updateCallback)
        self._subscribeOnVehControlling()

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.INSPIRE

    def getItemID(self):
        return VEHICLE_VIEW_STATE.INSPIRE

    def _getTitle(self, value):
        return backport.text(self._stringResource.inspire.inspired())

    def _getIsPulseVisible(self):
        return True


class BerserkerSN(BRBuffSN):

    def getItemID(self):
        return VEHICLE_VIEW_STATE.BERSERKER

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.BERSERKER

    def _getTitle(self, value):
        return backport.text(self._stringResource.berserk.active())


class BRSmokeSN(_BRLocalizationProvider, sn_items.SmokeSN):

    def _getSmokeData(self, smokesInfo):
        return getSmokeDataByPredicate(smokesInfo, self._isFitByEquipmentId)

    @staticmethod
    def _isFitByEquipmentId(equipmentId):
        equipment = getEquipmentById(equipmentId)
        return equipment.dotParams is None if equipment else False


class BRDamagingSmokeSN(_BRLocalizationProvider, sn_items.SmokeSN):

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.DAMAGING_SMOKE

    def _getTitle(self, value):
        return backport.text(self._stringResource.smoke.damaging())

    def _getSmokeData(self, smokesInfo):
        return getSmokeDataByPredicate(smokesInfo, self._isFitByEquipmentId)

    @staticmethod
    def _isFitByEquipmentId(equipmentId):
        equipment = getEquipmentById(equipmentId)
        return equipment.dotParams is not None if equipment else False


class DamagingCorrodingShotSN(_BRLocalizationProvider, sn_items.SmokeSN):

    def getItemID(self):
        return VEHICLE_VIEW_STATE.CORRODING_SHOT

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.CORRODING_SHOT

    def _getTitle(self, value):
        return backport.text(self._stringResource.damagingCorrodingShot())

    def _update(self, data):
        duration = data.get('duration', 0)
        if duration > 0.0:
            self._setVisible(True)
            self._updateTimeParams(duration, 0.0)
            self._sendUpdate()
        else:
            self._setVisible(False)


class FireCircleSN(_BRLocalizationProvider, sn_items.SmokeSN):

    def getItemID(self):
        return VEHICLE_VIEW_STATE.FIRE_CIRCLE

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.FIRE_CIRCLE

    def _getTitle(self, value):
        return backport.text(self._stringResource.fireCircle())

    def _update(self, value):
        duration = value.get('duration', 0.0) if isinstance(value, dict) else value
        if duration > 0.0:
            self._setVisible(True)
            self._updateTimeParams(duration, 0.0)
            self._sendUpdate()
        else:
            self._setVisible(False)


class ThunderStrikeSN(_BRLocalizationProvider, sn_items.SmokeSN):

    def getItemID(self):
        return VEHICLE_VIEW_STATE.THUNDER_STRIKE

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.THUNDER_STRIKE

    def _getTitle(self, value):
        return backport.text(self._stringResource.thunderStrike())

    def _update(self, value):
        duration = value.get('duration', 0.0)
        if duration > 0.0:
            self._setVisible(True)
            self._updateTimeParams(duration, 0.0)
            self._sendUpdate()
        else:
            self._setVisible(False)


class AdaptationHealthRestoreSN(_BRLocalizationProvider, sn_items.TimerSN):

    def __init__(self, updateCallback):
        super(AdaptationHealthRestoreSN, self).__init__(updateCallback)
        self._vo['additionalState'] = BATTLE_ROYAL_CONSTS.COUNTER_STATE_INITIAL

    def getItemID(self):
        return VEHICLE_VIEW_STATE.ADAPTATION_HEALTH_RESTORE

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.HP_RESTORE_ON_DAMAGE

    def _getTitle(self, value):
        return backport.text(self._stringResource.hpRestoreOnDamage())

    def _update(self, value):
        restoreHealth = value.get('restoreHealth')
        duration = value.get('duration')
        if duration is not None:
            if duration > 0.0:
                self._setVisible(True)
                self._updateTimeParams(duration, 0.0)
            else:
                self._setVisible(False)
                self._vo['additionalState'] = BATTLE_ROYAL_CONSTS.COUNTER_STATE_INITIAL
        if restoreHealth is not None:
            self._vo['additionalInfo'] = ''.join(('+', str(restoreHealth)))
            if restoreHealth > 0:
                self._vo['additionalState'] = BATTLE_ROYAL_CONSTS.COUNTER_STATE_EXTRA
        if duration is not None or restoreHealth is not None:
            self._sendUpdate()
        return
