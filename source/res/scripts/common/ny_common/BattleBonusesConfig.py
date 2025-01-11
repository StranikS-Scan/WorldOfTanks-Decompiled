# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ny_common/BattleBonusesConfig.py
from typing import Optional, Dict, Callable, List, TYPE_CHECKING
from ny_common.settings import BattleBonusesConsts
if TYPE_CHECKING:
    from items.vehicles import VehicleType

class BattleBonusesConfig(object):
    __slots__ = ('_config',)

    def __init__(self, config):
        self._config = config

    def getBonusesByType(self, bonusType):
        return {key:value.get(bonusType, {}) for key, value in self._config.iteritems()}

    def getBonusesChoiceByType(self, bonusType, choiceID):
        bonuses = self.getBonusesByType(bonusType)
        return None if not bonuses else {key:value[BattleBonusesConsts.CHOOSABLE_BONUS_NAME][choiceID] for key, value in bonuses.iteritems() if value.get(BattleBonusesConsts.CHOOSABLE_BONUS_NAME, {}).get(choiceID, None) is not None}

    def getXPBonuses(self):
        return self.getBonusesByType(BattleBonusesConsts.XP_BONUSES)

    def getCurrencyBonuses(self):
        return self.getBonusesByType(BattleBonusesConsts.CURRENCY_BONUSES)

    def getDependencies(self):
        return self._config.keys()


class BattleBonusApplier(object):

    @staticmethod
    def getBonusStatus(bonusType, vehType, maxReachedLevel, isRented=False):
        if bonusType == BattleBonusesConsts.XP_BONUSES:
            if vehType is None or 'premium' in vehType.tags and 'special' not in vehType.tags or isRented:
                return BattleBonusesConsts.VEHICLE_ERROR
            vehLevel = vehType.level
            if vehLevel > maxReachedLevel:
                return BattleBonusesConsts.LEVEL_ERROR
        return BattleBonusesConsts.APPLICABLE

    @staticmethod
    def getDependenciesCount(battleBonusesConfig, inventoryCounter):
        counts = {}
        dependencies = battleBonusesConfig.getDependencies()
        if not dependencies:
            return counts
        for key in dependencies:
            counts[key] = inventoryCounter(key)

        return counts

    @staticmethod
    def __mergeBonusData(bonusData, bonuses, counts):
        if not bonuses:
            return bonusData
        for dependency, bonusesData in bonuses.iteritems():
            for bonusType, value in bonusesData.iteritems():
                bonusValue = sum(value[:counts.get(dependency, 0)])
                if bonusType in bonusData:
                    bonusData[bonusType] += bonusValue
                bonusData[bonusType] = 1 + bonusValue

        return bonusData

    @classmethod
    def __getBonusData(cls, bonusType, choiceID, battleBonusesConfig):
        return battleBonusesConfig.getBonusesByType(bonusType) if choiceID is None else battleBonusesConfig.getBonusesChoiceByType(bonusType, choiceID)

    @classmethod
    def mergeBonusData(cls, bonusData, bonusType, choiceID, battleBonusesConfig, counts):
        bonuses = cls.__getBonusData(bonusType, choiceID, battleBonusesConfig)
        return cls.__mergeBonusData(bonusData, bonuses, counts)

    @classmethod
    def mergeBonusDataForToken(cls, bonusData, bonusType, choiceID, battleBonusesConfig, tokenID, index):
        bonuses = cls.__getBonusData(bonusType, choiceID, battleBonusesConfig)
        if tokenID not in bonuses:
            return bonusData
        for bonusType, bonusValue in bonuses[tokenID].iteritems():
            bonusData[bonusType] = bonusValue[index]

        return bonusData
