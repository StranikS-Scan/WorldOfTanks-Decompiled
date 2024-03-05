# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/battle_control/controllers/consumables/equipment_ctrl.py
import logging
from enum import Enum
from typing import TYPE_CHECKING
import Event
from cgf_mechanics import CosmicEffectComponentManager
from constants import EQUIPMENT_STAGES
from cosmic_event.cosmic_control_mode import BlackHoleArcadeMapCaseControlMode
from cosmic_event_common.cosmic_constants import COSMIC_EVENT_ROCKET_BOOSTER, COSMIC_EVENT_RAPIDSHELLING, COSMIC_EVENT_BLACKHOLE, COSMIC_EVENT_OVERCHARGE, COSMIC_EVENT_SHIELD, COSMIC_EVENT_POWER_SHOT
from cosmic_sound import CosmicBattleSounds
from gui.battle_control.controllers.consumables.equipment_ctrl import _VisualScriptItem, _ReplayItem, EquipmentsController, InCooldownError, NotReadyError, EquipmentSound
from gui.shared.system_factory import registerEquipmentItem
from items import vehicles, EQUIPMENT_TYPES
_logger = logging.getLogger(__name__)
if TYPE_CHECKING:
    from typing import Optional
    from Avatar import PlayerAvatar
_PREV_STAGE_FOR_SOUND = (EQUIPMENT_STAGES.DEPLOYING,
 EQUIPMENT_STAGES.COOLDOWN,
 EQUIPMENT_STAGES.SHARED_COOLDOWN,
 EQUIPMENT_STAGES.EXHAUSTED,
 EQUIPMENT_STAGES.NOT_RUNNING)

class ExtraEquipmentTags(Enum):
    TARGETING = 'targeting'


class _CosmicBaseItem(_VisualScriptItem):
    extraTags = ()

    def canActivate(self, entityName=None, avatar=None):
        canBeActivated, error = super(_CosmicBaseItem, self).canActivate(entityName, avatar)
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
        super(_CosmicBaseItem, self).activate(entityName, avatar)
        CosmicBattleSounds.Abilities.playActivated()

    def onElapsed(self):
        pass

    def getTags(self):
        return self.extraTags + tuple(super(_CosmicBaseItem, self).getTags())


class _CosmicEventGravityFieldItem(_CosmicBaseItem):
    pass


class _ReplayCosmicEventGravityFieldItem(_ReplayItem, _CosmicEventGravityFieldItem):
    pass


class _CosmicEventRocketBoosterItem(_CosmicBaseItem):

    def activate(self, entityName=None, avatar=None):
        super(_CosmicEventRocketBoosterItem, self).activate(entityName, avatar)
        CosmicBattleSounds.Abilities.playBoosterActivated()


class _ReplayCosmicEventRocketBoosterItem(_ReplayItem, _CosmicEventRocketBoosterItem):
    pass


class _CosmicEventShieldItem(_CosmicBaseItem):
    pass


class _ReplayCosmicEventShieldItem(_ReplayItem, _CosmicEventShieldItem):
    pass


class _CosmicEventBlackHoleItem(_CosmicBaseItem):
    extraTags = (ExtraEquipmentTags.TARGETING,)

    def _getAimingControlMode(self):
        return BlackHoleArcadeMapCaseControlMode


class _ReplayCosmicEventBlackHoleItem(_ReplayItem, _CosmicEventBlackHoleItem):
    pass


class _CosmicEventHookShotItem(_CosmicBaseItem):
    _GUN_GLOW_RGB = (0.0, 0.1, 1)
    _EFFECT_SWITCH_OFF_STAGES = (EQUIPMENT_STAGES.COOLDOWN, EQUIPMENT_STAGES.SHARED_COOLDOWN, EQUIPMENT_STAGES.EXHAUSTED)

    def activate(self, entityName=None, avatar=None):
        super(_CosmicEventHookShotItem, self).activate(entityName, avatar)
        CosmicBattleSounds.Abilities.playHookShotActivated()
        CosmicEffectComponentManager.setAdvancedVehicleGunGlow(self._GUN_GLOW_RGB)

    def onElapsed(self):
        super(_CosmicEventHookShotItem, self).onElapsed()
        CosmicBattleSounds.Abilities.playHookShotElapsed()
        CosmicEffectComponentManager.setBasicVehicleGunGlow()


class _ReplayCosmicEventHookShotItem(_ReplayItem, _CosmicEventHookShotItem):
    pass


class _CosmicEventPowerShotItem(_CosmicBaseItem):
    _GUN_GLOW_RGB = (0.12, 0.0, 0.8)
    _EFFECT_SWITCH_OFF_STAGES = (EQUIPMENT_STAGES.COOLDOWN, EQUIPMENT_STAGES.SHARED_COOLDOWN, EQUIPMENT_STAGES.EXHAUSTED)

    def activate(self, entityName=None, avatar=None):
        super(_CosmicEventPowerShotItem, self).activate(entityName, avatar)
        CosmicBattleSounds.Abilities.playPowerShotActivated()
        CosmicEffectComponentManager.setAdvancedVehicleGunGlow(self._GUN_GLOW_RGB)

    def onElapsed(self):
        super(_CosmicEventPowerShotItem, self).onElapsed()
        CosmicBattleSounds.Abilities.playPowerShotElapsed()
        CosmicEffectComponentManager.setBasicVehicleGunGlow()


class _ReplayCosmicEventPowerShotItem(_ReplayItem, _CosmicEventPowerShotItem):
    pass


def registerCosmicEventEquipmentsItems():
    registerEquipmentItem(COSMIC_EVENT_OVERCHARGE, _CosmicEventGravityFieldItem, _ReplayCosmicEventGravityFieldItem)
    registerEquipmentItem(COSMIC_EVENT_ROCKET_BOOSTER, _CosmicEventRocketBoosterItem, _ReplayCosmicEventRocketBoosterItem)
    registerEquipmentItem(COSMIC_EVENT_BLACKHOLE, _CosmicEventBlackHoleItem, _ReplayCosmicEventBlackHoleItem)
    registerEquipmentItem(COSMIC_EVENT_RAPIDSHELLING, _CosmicEventHookShotItem, _ReplayCosmicEventHookShotItem)
    registerEquipmentItem(COSMIC_EVENT_POWER_SHOT, _CosmicEventPowerShotItem, _ReplayCosmicEventPowerShotItem)
    registerEquipmentItem(COSMIC_EVENT_SHIELD, _CosmicEventShieldItem, _ReplayCosmicEventShieldItem)


class CosmicEquipmentsController(EquipmentsController):

    def __init__(self, setup):
        super(CosmicEquipmentsController, self).__init__(setup)
        self.onEquipmentRemoved = Event.Event(self._eManager)

    def getOrdinal(self, intCD):
        if intCD not in self._order:
            _logger.warning('Equipment %d, cannot be found in equipment controller. Equipment order %s', intCD, self.getOrderedEquipmentsLayout())
            return None
        else:
            return self._order.index(intCD)

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
            else:
                item.update(quantity, stage, timeRemaining, totalTime)
                self.onEquipmentUpdated(intCD, item)
        elif stage == EQUIPMENT_STAGES.READY:
            descriptor = vehicles.getItemByCompactDescr(intCD)
            if descriptor.equipmentType in (EQUIPMENT_TYPES.regular, EQUIPMENT_TYPES.battleAbilities):
                item = self.createItem(descriptor, quantity, stage, timeRemaining, totalTime)
                self._equipments[intCD] = item
                self._order.append(intCD)
                item.updateMapCase()
                self.onEquipmentAdded(intCD, item)
        if item:
            item.setServerPrevStage(None)
        return
