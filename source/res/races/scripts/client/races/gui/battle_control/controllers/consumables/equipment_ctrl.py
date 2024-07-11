# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/battle_control/controllers/consumables/equipment_ctrl.py
import logging
from races_common.races_constants import RACES_RAPIDSHELLING, RACES_SHIELD, RACES_POWER_IMPULSE, RACES_ROCKET_BOOSTER
from typing import TYPE_CHECKING
import CommandMapping
import Event
import SoundGroups
from constants import EQUIPMENT_STAGES
from gui.battle_control.controllers.consumables.equipment_ctrl import EquipmentsController, _VisualScriptItem, EquipmentSound, _ReplayItem
from gui.shared.system_factory import registerEquipmentItem
from items import vehicles, EQUIPMENT_TYPES
from shared_utils import findFirst
_logger = logging.getLogger(__name__)
if TYPE_CHECKING:
    from typing import Optional, Dict
_PREV_STAGE_FOR_SOUND = (EQUIPMENT_STAGES.DEPLOYING,
 EQUIPMENT_STAGES.COOLDOWN,
 EQUIPMENT_STAGES.SHARED_COOLDOWN,
 EQUIPMENT_STAGES.EXHAUSTED,
 EQUIPMENT_STAGES.NOT_RUNNING)

class _RacesBaseItem(_VisualScriptItem):
    extraTags = ()
    RACES_PICKUP_SOUND = 'ev_race_ability_pickup'

    def __init__(self, *args):
        super(_RacesBaseItem, self).__init__(*args)
        self.pressed = False

    def canActivate(self, entityName=None, avatar=None):
        canBeActivated, error = super(_RacesBaseItem, self).canActivate(entityName, avatar)
        return (canBeActivated, error)

    def _soundUpdate(self, prevQuantity, quantity):
        if quantity > prevQuantity:
            SoundGroups.g_instance.playSound2D(self.RACES_PICKUP_SOUND)
        if prevQuantity > quantity and self._stage != self._prevStage:
            if self._stage != EQUIPMENT_STAGES.NOT_RUNNING:
                EquipmentSound.playSound(self._descriptor.compactDescr)
        if self.isReady and self._serverPrevStage in _PREV_STAGE_FOR_SOUND:
            EquipmentSound.playReady(self)

    def onElapsed(self):
        pass

    def getTags(self):
        return self.extraTags + tuple(super(_RacesBaseItem, self).getTags())


class _RacesRapidShellingItem(_RacesBaseItem):
    pass


class _ReplayRacesRapidShellingItem(_ReplayItem, _RacesRapidShellingItem):
    pass


class _RacesShieldItem(_RacesBaseItem):
    pass


class _ReplayRacesShieldItem(_ReplayItem, _RacesShieldItem):
    pass


class _RacesPowerImpulseItem(_RacesBaseItem):
    pass


class _ReplayRacesPowerImpulseItem(_ReplayItem, _RacesPowerImpulseItem):
    pass


class _RacesRocketBoosterItem(_RacesBaseItem):
    pass


class _ReplayRacesRocketBoosterItem(_ReplayItem, _RacesRocketBoosterItem):
    pass


def registerRacesEquipmentsItems():
    registerEquipmentItem(RACES_RAPIDSHELLING, _RacesRapidShellingItem, _ReplayRacesRapidShellingItem)
    registerEquipmentItem(RACES_SHIELD, _RacesShieldItem, _ReplayRacesShieldItem)
    registerEquipmentItem(RACES_POWER_IMPULSE, _RacesPowerImpulseItem, _ReplayRacesPowerImpulseItem)
    registerEquipmentItem(RACES_ROCKET_BOOSTER, _RacesRocketBoosterItem, _ReplayRacesRocketBoosterItem)


class RacesEquipmentsController(EquipmentsController):

    def __init__(self, setup):
        super(RacesEquipmentsController, self).__init__(setup)
        self.onEquipmentRemoved = Event.Event(self._eManager)
        self.__abilitiesSlots = {0: None,
         1: None,
         2: None}
        self.__pressedAbilities = {}
        return

    def setEquipment(self, intCD, quantity, stage, timeRemaining, totalTime):
        _logger.debug('Equipment added: intCD=%d, quantity=%d, stage=%s, timeRemaining=%d, totalTime=%d', intCD, quantity, stage, timeRemaining, totalTime)
        item = None
        totalAbilityCount = 0
        for index, abilityItem in self.__abilitiesSlots.items():
            if abilityItem:
                if abilityItem.getDescriptor().compactDescr == intCD:
                    totalAbilityCount += 1

        ability = vehicles.getItemByCompactDescr(intCD)
        if totalAbilityCount < quantity:
            if ability.equipmentType in (EQUIPMENT_TYPES.regular, EQUIPMENT_TYPES.battleAbilities):
                item = self.createItem(ability, quantity, stage, timeRemaining, totalTime)
                abilityIndexToAdd = 0
                for index, abilityItem in self.__abilitiesSlots.items():
                    if not abilityItem:
                        self.__abilitiesSlots[index] = item
                        abilityIndexToAdd = index
                        break

                item.updateMapCase()
                self.onEquipmentAdded(abilityIndexToAdd, item)
        elif totalAbilityCount > quantity:
            for index, abilityItem in self.__abilitiesSlots.items():
                if not abilityItem:
                    continue
                if abilityItem.getDescriptor().compactDescr != intCD:
                    continue
                if abilityItem.pressed:
                    abilityItem.onElapsed()
                    self.onEquipmentRemoved(index, abilityItem)
                    self.__abilitiesSlots[index] = None
                    continue
                if stage == EQUIPMENT_STAGES.COOLDOWN:
                    abilityItem.update(quantity, stage, timeRemaining, totalTime)
                    self.onEquipmentUpdated(index, abilityItem)

        elif totalAbilityCount == quantity and quantity > 0:
            for index, abilityItem in self.__abilitiesSlots.items():
                if abilityItem:
                    if abilityItem.getDescriptor().compactDescr != intCD:
                        continue
                    isRapidShelling = abilityItem.getDescriptor().name == RACES_RAPIDSHELLING
                    pressed = abilityItem.pressed
                    if stage == EQUIPMENT_STAGES.DEPLOYING and isRapidShelling and not pressed:
                        continue
                    if stage == EQUIPMENT_STAGES.ACTIVE and not pressed:
                        continue
                    abilityItem.update(quantity, stage, timeRemaining, totalTime)
                    self.onEquipmentUpdated(index, abilityItem)

        if stage == EQUIPMENT_STAGES.READY:
            self.__pressedAbilities[intCD] = False
        if item:
            item.setServerPrevStage(None)
        CommandMapping.g_instance.onMappingChanged()
        return

    def pressAbility(self, slotIdx):
        abilityToUse = self.__abilitiesSlots[slotIdx]
        if not abilityToUse:
            return False
        abilityDescr = abilityToUse.getDescriptor().compactDescr
        if self.__pressedAbilities.get(abilityDescr, False):
            return False
        abilityToUse.pressed = True
        self.__pressedAbilities[abilityDescr] = True
        return True

    def getOrderedEquipmentsLayout(self):
        return self.__abilitiesSlots.items()

    def getEquipment(self, slotIndex):
        try:
            item = self.__abilitiesSlots[slotIndex]
        except KeyError:
            _logger.error('Equipment is not found in slot index. %d', slotIndex)
            item = None

        return item

    def getEquipmentByIntCD(self, intCD):
        return findFirst(lambda item: item is not None and item.getDescriptor().compactDescr == intCD, self.__abilitiesSlots.itervalues())

    def setServerPrevStage(self, prevStage, intCD):
        equipment = self.getEquipmentByIntCD(intCD)
        if equipment:
            equipment.setServerPrevStage(prevStage)
