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

class BRANCH_SLOT_TYPE(object):
    REGULAR = 0
    EXTRA = 1
    _NAME_TO_ID = {'regular': REGULAR,
     'extra': EXTRA}
    _ID_TO_NAME = None

    @classmethod
    def getSlotTypeIDByName(cls, slotTypeName):
        return cls._NAME_TO_ID.get(slotTypeName, None)

    @classmethod
    def getSlotTypeNameByID(cls, slotTypeID):
        if cls._ID_TO_NAME is None:
            cls._initIDToName()
        return cls._ID_TO_NAME.get(slotTypeID, None)

    @classmethod
    def _initIDToName(cls):
        if cls._ID_TO_NAME is None:
            cls._ID_TO_NAME = {slotID:slotName for slotName, slotID in cls._NAME_TO_ID.iteritems()}
        return


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
        return None if slotInfo is None else self._config.get(NYVehBranchConsts.VEH_CHANGE_COOLDOWN, {}).get(slotInfo[NYVehBranchConsts.SLOT_TYPE], None)

    def getPriceForChangeInPostEvent(self, slotID):
        slotInfo = self.getSlotInfo(slotID)
        return None if slotInfo is None else self._config.get(NYVehBranchConsts.VEH_CHANGE_PRICE, {}).get(slotInfo[NYVehBranchConsts.SLOT_TYPE], None)

    def getNewYearStyleID(self):
        return self._config.get(NYVehBranchConsts.STYLE_ID)

    def getExtraSlotChoices(self):
        return self._config.get(NYVehBranchConsts.EXTRA_SLOT_BONUS_CHOICES, {})

    def getRegularBonusesForVehClass(self, vehClass):
        return self._config.get(NYVehBranchConsts.REGULAR_SLOT_BONUS, {}).get(vehClass, {})

    def getExtraBonusesForChoice(self, choiceID):
        return self.getExtraSlotChoices().get(choiceID, {})


class VehicleBranchBonus(object):

    @classmethod
    def checkSlotID(cls, slotID, vehBranchConfig):
        return vehBranchConfig.getSlotInfo(slotID) is not None

    @classmethod
    def checkVehicleCompatibilityForSlot(cls, slotID, vehType, maxReachedLevel, quests, vehBranchConfig):
        slotInfo = vehBranchConfig.getSlotInfo(slotID)
        if slotInfo is None:
            return (False, 'Invalid slotID')
        else:
            vehLevel = vehType.level
            isExtraSlot = slotInfo[NYVehBranchConsts.SLOT_TYPE] == BRANCH_SLOT_TYPE.EXTRA
            if isExtraSlot and maxReachedLevel < NY_BRANCH_MIN_LEVEL:
                if vehLevel != NY_BRANCH_MIN_LEVEL:
                    return (False, 'Not enough atmosphere level')
            elif not vehLevel <= maxReachedLevel:
                return (False, 'Not enough atmosphere level')
            if vehLevel not in slotInfo[NYVehBranchConsts.VEHICLE_LEVELS]:
                return (False, 'Invalid vehicle level')
            if 'premium' in vehType.tags and 'special' not in vehType.tags:
                return (False, 'cannot set premium vehicle')
            if isExtraSlot:
                if not quests.hasToken(VEH_BRANCH_EXTRA_SLOT_TOKEN):
                    return (False, 'Extra slot is not allowed')
            return (True, None)

    @classmethod
    def checkBonusChoiceForSlot(cls, slotID, choiceID, vehBranchConfig):
        slotInfo = vehBranchConfig.getSlotInfo(slotID)
        if slotInfo is None:
            return (False, 'Invalid slotID')
        else:
            slotType = slotInfo[NYVehBranchConsts.SLOT_TYPE]
            if slotType == BRANCH_SLOT_TYPE.REGULAR:
                return cls._checkBonusChoiceForRegularSlot(choiceID, vehBranchConfig)
            return cls._checkBonusChoiceForExtraSlot(choiceID, vehBranchConfig) if slotType == BRANCH_SLOT_TYPE.EXTRA else (False, 'Wrong slot type')

    @classmethod
    def mergeBonusData(cls, bonusData, vehTypeCompDescr, slotID, choiceID, vehBranchConfig):
        slotInfo = vehBranchConfig.getSlotInfo(slotID)
        if slotInfo is None:
            return bonusData
        else:
            bonuses = cls._getBonusesForSlot(slotInfo, vehTypeCompDescr, choiceID, vehBranchConfig)
            for bonusType, value in bonuses.iteritems():
                if bonusType in bonusData:
                    bonusData[bonusType] += value
                bonusData[bonusType] = 1 + value

            return bonusData

    @classmethod
    def _getBonusesForSlot(cls, slotInfo, vehTypeCompDescr, choiceID, vehBranchConfig):
        if slotInfo[NYVehBranchConsts.SLOT_TYPE] == BRANCH_SLOT_TYPE.REGULAR:
            vehClass = vehicles.getVehicleClass(vehTypeCompDescr)
            bonuses = vehBranchConfig.getRegularBonusesForVehClass(vehClass)
        else:
            bonuses = vehBranchConfig.getExtraBonusesForChoice(choiceID)
        return bonuses

    @classmethod
    def _checkBonusChoiceForRegularSlot(cls, choiceID, vehBranchConfig):
        return (False, 'Not allowed for regular slot')

    @classmethod
    def _checkBonusChoiceForExtraSlot(cls, choiceID, vehBranchConfig):
        return (False, 'Invalid choiceID') if choiceID not in vehBranchConfig.getExtraSlotChoices() else (True, None)
