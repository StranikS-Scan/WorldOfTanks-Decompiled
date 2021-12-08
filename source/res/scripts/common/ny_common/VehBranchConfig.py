# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ny_common/VehBranchConfig.py
from typing import Tuple, Optional, TYPE_CHECKING, Dict, Any
from items import vehicles
from items.components.ny_constants import VEH_BRANCH_EXTRA_SLOT_TOKEN, NY_BRANCH_MIN_LEVEL
from ny_common.settings import NYVehBranchConsts
if TYPE_CHECKING:
    from account_helpers import QuestProgress
    from items.vehicles import VehicleType
_BonusesType = Dict[str, float]
_SlotType = Dict[str, Any]
_ResultType = Tuple[bool, Optional[str]]

class VehBranchConfig(object):
    __slots__ = ('_config',)

    def __init__(self, config):
        self._config = config

    def getSlotInfo(self, slotID):
        return self._config.get(NYVehBranchConsts.SLOTS, {}).get(slotID, None)

    def getSlotsCount(self):
        return len(self._config.get(NYVehBranchConsts.SLOTS, {}))

    def getCooldownFor(self, slotID):
        slotInfo = self.getSlotInfo(slotID)
        return None if slotInfo is None else self._config.get(NYVehBranchConsts.VEH_CHANGE_COOLDOWN, None)

    def getPriceForChangeInPostEvent(self, slotID):
        slotInfo = self.getSlotInfo(slotID)
        return None if slotInfo is None else self._config.get(NYVehBranchConsts.VEH_CHANGE_PRICE, None)

    def getSlotChoices(self):
        return self._config.get(NYVehBranchConsts.SLOT_BONUS_CHOICES, {})

    def getBonusesForChoice(self, choiceID):
        return self.getSlotChoices().get(choiceID, {})


class VehicleBranchBonus(object):

    @classmethod
    def checkSlotID(cls, slotID, vehBranchConfig):
        return vehBranchConfig.getSlotInfo(slotID) is not None

    @classmethod
    def checkVehicleCompatibilityForSlot(cls, slotID, vehType, maxReachedLevel, quests, vehBranchConfig):
        slotInfo = vehBranchConfig.getSlotInfo(slotID)
        if slotInfo is None:
            return (False, 'Invalid slotID')
        vehLevel = vehType.level
        if vehLevel < NY_BRANCH_MIN_LEVEL:
            return (False, 'Invalid vehicle level')
        elif NYVehBranchConsts.LEVEL in slotInfo and maxReachedLevel < slotInfo[NYVehBranchConsts.LEVEL]:
            return (False, 'Not enough atmosphere level')
        elif NYVehBranchConsts.TOKEN in slotInfo and not quests.hasToken(slotInfo[NYVehBranchConsts.TOKEN]):
            return (False, 'No required token')
        else:
            return (False, 'cannot set premium vehicle') if 'premium' in vehType.tags and 'special' not in vehType.tags else (True, None)

    @classmethod
    def checkBonusChoiceForSlot(cls, slotID, choiceID, vehBranchConfig):
        slotInfo = vehBranchConfig.getSlotInfo(slotID)
        if slotInfo is None:
            return (False, 'Invalid slotID')
        else:
            return (False, 'Invalid choiceID') if choiceID not in vehBranchConfig.getSlotChoices() else (True, None)

    @classmethod
    def mergeBonusData(cls, bonusData, slotID, choiceID, vehBranchConfig):
        slotInfo = vehBranchConfig.getSlotInfo(slotID)
        if slotInfo is None:
            return bonusData
        else:
            bonuses = vehBranchConfig.getBonusesForChoice(choiceID)
            for bonusType, value in bonuses.iteritems():
                if bonusType in bonusData:
                    bonusData[bonusType] += value
                bonusData[bonusType] = 1 + value

            return bonusData
