# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/battle_control/controllers/consumables/equipment_ctrl.py
import BigWorld
import Event
import logging
from AvatarInputHandler import MapCaseMode
from enum import Enum
from typing import TYPE_CHECKING
from constants import EQUIPMENT_STAGES
from helpers import dependency
from gui.battle_control import avatar_getter
from gui.battle_control.controllers.consumables.equipment_ctrl import _VisualScriptItem, _ReplayItem, _BaseAbilityItem, EquipmentsController, InCooldownError, NotReadyError, EquipmentSound, _OrderItem
from gui.shared.system_factory import registerEquipmentItem
from items import vehicles, EQUIPMENT_TYPES
from skeletons.gui.game_control import ICosmicEventBattleController
from cosmic_event.cosmic_constants import COSMIC_VEHICLES_ROVER_ENUM
from cosmic_event_client_cgf.managers import CosmicEffectComponentManager
from cosmic_event_common.cosmic_constants import COSMIC_EVENT_ROCKET_BOOSTER, COSMIC_EVENT_RAPIDSHELLING, COSMIC_EVENT_BLACKHOLE, COSMIC_EVENT_OVERCHARGE, COSMIC_EVENT_SHIELD, COSMIC_EVENT_POWER_SHOT, COSMIC_EVENT_WAVE, COSMIC_EVENT_STUN_SHOT, COSMIC_EVENT_MINE, COSMIC_EVENT_TELEPORT, LOOT_TO_EQUIPMENT
from cosmic_sound import CosmicBattleSounds
_logger = logging.getLogger(__name__)
if TYPE_CHECKING:
    from typing import Optional, Union
    from Avatar import PlayerAvatar
_PREV_STAGE_FOR_SOUND = (EQUIPMENT_STAGES.DEPLOYING,
 EQUIPMENT_STAGES.COOLDOWN,
 EQUIPMENT_STAGES.SHARED_COOLDOWN,
 EQUIPMENT_STAGES.EXHAUSTED,
 EQUIPMENT_STAGES.NOT_RUNNING)

class ExtraEquipmentTags(Enum):
    TARGETING = 'targeting'


def _CosmicBaseItem(baseClass):

    class _CosmicBaseItemImpl(baseClass):
        extraTags = ()

        def __init__(self, *args):
            super(_CosmicBaseItemImpl, self).__init__(*args)
            self._isPlayingSoundNow = False

        def canActivate(self, entityName=None, avatar=None):
            curTime = BigWorld.serverTime()
            if curTime >= BigWorld.player().arena.periodEndTime:
                return (False, None)
            else:
                canBeActivated, error = super(_CosmicBaseItemImpl, self).canActivate(entityName, avatar)
                if not canBeActivated:
                    if isinstance(error, (InCooldownError, NotReadyError)):
                        CosmicBattleSounds.Abilities.playNotReady()
                return (canBeActivated, error)

        def _soundUpdate(self, prevQuantity, quantity):
            if prevQuantity > quantity and self._stage != self._prevStage:
                if self._stage != EQUIPMENT_STAGES.NOT_RUNNING:
                    EquipmentSound.playSound(self._descriptor.compactDescr)
            if self.isReady and self._serverPrevStage in _PREV_STAGE_FOR_SOUND:
                EquipmentSound.playReady(self)

        def activate(self, entityName=None, avatar=None):
            super(_CosmicBaseItemImpl, self).activate(entityName, avatar)
            CosmicBattleSounds.Abilities.playActivated()

        def onElapsed(self):
            pass

        def getTags(self):
            return self.extraTags + tuple(super(_CosmicBaseItemImpl, self).getTags())

        def clear(self):
            if self._isPlayingSoundNow:
                self._stopSounds()
            super(_CosmicBaseItemImpl, self).clear()

        def _stopSounds(self):
            self._isPlayingSoundNow = False

    return _CosmicBaseItemImpl


class _CosmicBaseVisualScriptItem(_CosmicBaseItem(_VisualScriptItem)):
    pass


class _CosmicEventGravityFieldItem(_CosmicBaseVisualScriptItem):
    pass


class _ReplayCosmicEventGravityFieldItem(_ReplayItem, _CosmicEventGravityFieldItem):
    pass


class _CosmicEventRocketBoosterItem(_CosmicBaseVisualScriptItem):

    def activate(self, entityName=None, avatar=None):
        super(_CosmicEventRocketBoosterItem, self).activate(entityName, avatar)
        CosmicBattleSounds.Abilities.playBoosterActivated()


class _ReplayCosmicEventRocketBoosterItem(_ReplayItem, _CosmicEventRocketBoosterItem):
    pass


class _CosmicEventShieldItem(_CosmicBaseVisualScriptItem):
    pass


class _ReplayCosmicEventShieldItem(_ReplayItem, _CosmicEventShieldItem):
    pass


class _CosmicEventBlackHoleItem(_CosmicBaseVisualScriptItem):
    extraTags = (ExtraEquipmentTags.TARGETING,)

    def _soundUpdate(self, prevQuantity, quantity):
        super(_CosmicEventBlackHoleItem, self)._soundUpdate(prevQuantity, quantity)
        if self._stage == EQUIPMENT_STAGES.READY and self._serverPrevStage == EQUIPMENT_STAGES.PREPARING:
            CosmicBattleSounds.Abilities.handleInstalledAbility(False)
        elif self._stage == EQUIPMENT_STAGES.ACTIVE and self._serverPrevStage == EQUIPMENT_STAGES.PREPARING:
            CosmicBattleSounds.Abilities.handleInstalledAbility(True)

    def _getAimingControlMode(self):
        return MapCaseMode.ArcadeMapCaseControlMode


class _ReplayCosmicEventBlackHoleItem(_ReplayItem, _CosmicEventBlackHoleItem):
    pass


class _CosmicEventHookShotItem(_CosmicBaseVisualScriptItem):
    _GUN_GLOW_RGB = (0.0, 0.1, 1)
    _EFFECT_SWITCH_OFF_STAGES = (EQUIPMENT_STAGES.COOLDOWN, EQUIPMENT_STAGES.SHARED_COOLDOWN, EQUIPMENT_STAGES.EXHAUSTED)

    def activate(self, entityName=None, avatar=None):
        super(_CosmicEventHookShotItem, self).activate(entityName, avatar)
        CosmicEffectComponentManager.setAdvancedVehicleGunGlow(self._GUN_GLOW_RGB)
        CosmicBattleSounds.Abilities.playHookShotActivated()
        self._isPlayingSoundNow = True

    def onElapsed(self):
        super(_CosmicEventHookShotItem, self).onElapsed()
        CosmicEffectComponentManager.setBasicVehicleGunGlow()
        self._stopSounds()

    def _stopSounds(self):
        super(_CosmicEventHookShotItem, self)._stopSounds()
        CosmicBattleSounds.Abilities.playHookShotElapsed()


class _ReplayCosmicEventHookShotItem(_ReplayItem, _CosmicEventHookShotItem):
    pass


class _CosmicEventPowerShotItem(_CosmicBaseVisualScriptItem):
    _GUN_GLOW_RGB = (0.12, 0.0, 0.8)
    _EFFECT_SWITCH_OFF_STAGES = (EQUIPMENT_STAGES.COOLDOWN, EQUIPMENT_STAGES.SHARED_COOLDOWN, EQUIPMENT_STAGES.EXHAUSTED)

    def activate(self, entityName=None, avatar=None):
        super(_CosmicEventPowerShotItem, self).activate(entityName, avatar)
        CosmicEffectComponentManager.setAdvancedVehicleGunGlow(self._GUN_GLOW_RGB)
        CosmicBattleSounds.Abilities.playPowerShotActivated()
        self._isPlayingSoundNow = True

    def onElapsed(self):
        super(_CosmicEventPowerShotItem, self).onElapsed()
        CosmicEffectComponentManager.setBasicVehicleGunGlow()
        self._stopSounds()

    def _stopSounds(self):
        super(_CosmicEventPowerShotItem, self)._stopSounds()
        CosmicBattleSounds.Abilities.playPowerShotElapsed()


class _ReplayCosmicEventPowerShotItem(_ReplayItem, _CosmicEventPowerShotItem):
    pass


class _CosmicEventWaveItem(_CosmicBaseVisualScriptItem):
    pass


class _ReplayCosmicEventWaveItem(_ReplayItem, _CosmicEventWaveItem):
    pass


class _CosmicEventStunShotItem(_CosmicBaseVisualScriptItem):
    _GUN_GLOW_RGB = (0, 1, 0)
    _EFFECT_SWITCH_OFF_STAGES = (EQUIPMENT_STAGES.COOLDOWN, EQUIPMENT_STAGES.SHARED_COOLDOWN, EQUIPMENT_STAGES.EXHAUSTED)

    def activate(self, entityName=None, avatar=None):
        super(_CosmicEventStunShotItem, self).activate(entityName, avatar)
        CosmicEffectComponentManager.setAdvancedVehicleGunGlow(self._GUN_GLOW_RGB)
        CosmicBattleSounds.Abilities.playStunShotActivated()
        self._isPlayingSoundNow = True

    def onElapsed(self):
        super(_CosmicEventStunShotItem, self).onElapsed()
        CosmicEffectComponentManager.setBasicVehicleGunGlow()
        self._stopSounds()

    def _stopSounds(self):
        super(_CosmicEventStunShotItem, self)._stopSounds()
        CosmicBattleSounds.Abilities.playStunShotElapsed()


class _ReplayCosmicEventStunShotItem(_ReplayItem, _CosmicEventStunShotItem):
    pass


class _CosmicEventMineItem(_CosmicBaseItem(_OrderItem)):
    extraTags = (ExtraEquipmentTags.TARGETING,)

    def _soundUpdate(self, prevQuantity, quantity):
        super(_CosmicEventMineItem, self)._soundUpdate(prevQuantity, quantity)
        if self._stage == EQUIPMENT_STAGES.READY and self._serverPrevStage == EQUIPMENT_STAGES.PREPARING:
            CosmicBattleSounds.Abilities.handleInstalledAbility(False)
        elif self._stage == EQUIPMENT_STAGES.COOLDOWN and self._serverPrevStage == EQUIPMENT_STAGES.PREPARING:
            CosmicBattleSounds.Abilities.handleInstalledAbility(True)

    def getAimingControlMode(self):
        return MapCaseMode.ArcadeMapCaseControlMode


class _ReplayCosmicEventMineItem(_ReplayItem, _CosmicEventMineItem):
    pass


class _CosmicTeleportItem(_CosmicBaseItem(_BaseAbilityItem)):

    def onElapsed(self):
        pass

    def canActivate(self, entityName=None, avatar=None):
        curTime = BigWorld.serverTime()
        if curTime >= BigWorld.player().arena.periodEndTime:
            return (False, None)
        else:
            return (False, None) if self._stage not in (EQUIPMENT_STAGES.READY, EQUIPMENT_STAGES.ACTIVE) else (True, None)


class _ReplayCosmicTeleportItem(_ReplayItem, _CosmicTeleportItem):
    pass


def registerCosmicEventEquipmentsItems():
    registerEquipmentItem(COSMIC_EVENT_OVERCHARGE, _CosmicEventGravityFieldItem, _ReplayCosmicEventGravityFieldItem)
    registerEquipmentItem(COSMIC_EVENT_ROCKET_BOOSTER, _CosmicEventRocketBoosterItem, _ReplayCosmicEventRocketBoosterItem)
    registerEquipmentItem(COSMIC_EVENT_BLACKHOLE, _CosmicEventBlackHoleItem, _ReplayCosmicEventBlackHoleItem)
    registerEquipmentItem(COSMIC_EVENT_RAPIDSHELLING, _CosmicEventHookShotItem, _ReplayCosmicEventHookShotItem)
    registerEquipmentItem(COSMIC_EVENT_POWER_SHOT, _CosmicEventPowerShotItem, _ReplayCosmicEventPowerShotItem)
    registerEquipmentItem(COSMIC_EVENT_SHIELD, _CosmicEventShieldItem, _ReplayCosmicEventShieldItem)
    registerEquipmentItem(COSMIC_EVENT_WAVE, _CosmicEventWaveItem, _ReplayCosmicEventWaveItem)
    registerEquipmentItem(COSMIC_EVENT_STUN_SHOT, _CosmicEventStunShotItem, _ReplayCosmicEventStunShotItem)
    registerEquipmentItem(COSMIC_EVENT_MINE, _CosmicEventMineItem, _ReplayItem)
    registerEquipmentItem(COSMIC_EVENT_TELEPORT, _CosmicTeleportItem, _ReplayCosmicTeleportItem)


if TYPE_CHECKING:
    _CosmicItemType = Union[_CosmicBaseVisualScriptItem, _CosmicEventMineItem]

class CosmicEquipmentsController(EquipmentsController):
    cosmicController = dependency.descriptor(ICosmicEventBattleController)

    def __init__(self, setup):
        super(CosmicEquipmentsController, self).__init__(setup)
        self.onEquipmentRemoved = Event.Event(self._eManager)

    def getAbilityIndex(self, intCD):
        descriptor = vehicles.getItemByCompactDescr(intCD)
        abilityName = descriptor.name
        eventVehicles = self.cosmicController.getModeSettings().eventVehicles
        selectedVehicleName = avatar_getter.getVehicleTypeDescriptor().name
        selectedVehicleId = COSMIC_VEHICLES_ROVER_ENUM[selectedVehicleName]
        vehicleData = eventVehicles.get(selectedVehicleId, {})
        vehicleAbilities = vehicleData.get('abilities', [])
        if not vehicleAbilities:
            return None
        elif abilityName in vehicleAbilities:
            return vehicleAbilities.index(abilityName)
        else:
            return len(vehicleAbilities) if abilityName in LOOT_TO_EQUIPMENT.values() else None

    def setEquipment(self, intCD, quantity, stage, timeRemaining, totalTime):
        _logger.debug('Equipment added: intCD=%d, quantity=%d, stage=%s, timeRemaining=%d, totalTime=%d', intCD, quantity, stage, timeRemaining, totalTime)
        item = None
        if not intCD:
            if len(self._order) < self.__equipmentCount:
                self._order.append(0)
                self.onEquipmentAdded(0, None)
        elif intCD in self._equipments:
            item = self._equipments[intCD]
            if quantity == 0:
                item = self._equipments.pop(intCD, None)
                item.onElapsed()
                self._order.remove(intCD)
                self.onEquipmentRemoved(intCD, item)
            elif stage == EQUIPMENT_STAGES.DEPLOYING and isinstance(item, _CosmicEventStunShotItem):
                item.onElapsed()
            else:
                item.update(quantity, stage, timeRemaining, totalTime)
                self.onEquipmentUpdated(intCD, item)
        elif stage in (EQUIPMENT_STAGES.READY, EQUIPMENT_STAGES.PREPARING, EQUIPMENT_STAGES.ACTIVE):
            descriptor = vehicles.getItemByCompactDescr(intCD)
            if descriptor.equipmentType in (EQUIPMENT_TYPES.regular, EQUIPMENT_TYPES.battleAbilities):
                item = self.createItem(descriptor, quantity, stage, timeRemaining, totalTime)
                self._equipments[intCD] = item
                self._order.append(intCD)
                item.updateMapCase()
                self.onEquipmentAdded(intCD, item)
        else:
            _logger.debug('Equipment can not be added: intCD=%d, its stage=%s and is neither READY nor PREPARING nor ACTIVE', intCD, stage)
        if item:
            item.setServerPrevStage(None)
        return

    def changeSetting(self, intCD, entityName=None, avatar=None):
        if self.__canChangeSetting(intCD):
            super(CosmicEquipmentsController, self).changeSetting(intCD, entityName, avatar)

    def __canChangeSetting(self, intCD):
        curItem = self.getEquipment(intCD)
        if not curItem:
            return True
        curItemType = curItem.__class__
        shootingItemTypes = (_CosmicEventStunShotItem, _CosmicEventHookShotItem, _CosmicEventPowerShotItem)
        if curItemType not in shootingItemTypes:
            return True
        for equipment in self._equipments.itervalues():
            itemType = equipment.__class__
            if itemType == curItemType:
                continue
            if itemType in shootingItemTypes and equipment.getStage() == EQUIPMENT_STAGES.ACTIVE:
                return False

        return True
