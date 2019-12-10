# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ny_common/CraftCost.py
import typing
from items.components import ny_constants
from items import new_year, collectibles
from ny_common.settings import CraftCostConsts

class CraftCostConfig(object):
    __slots__ = ('_config',)

    def __init__(self, config):
        self._config = config

    def __getRandomToyCost(self):
        return self._config.get(CraftCostConsts.RANDOM_TOY_COST, 0)

    def __getMegaToyCost(self, toyCount):
        megaCost = self._config.get(CraftCostConsts.MEGA_COST_BY_COUNT, (0,))
        return megaCost[-1] if toyCount >= len(megaCost) else megaCost[toyCount]

    def __getUsualToyCost(self, yearCollection, rank):
        return self._config.get(yearCollection)[rank - 1]

    def __getSettingCostFactor(self):
        return self._config.get(CraftCostConsts.SETTING_COST_FACTOR, 1)

    def __getCustomizationCostFactor(self, customization):
        return self._config.get(CraftCostConsts.CUSTOMIZATION_COST_FACTOR, {}).get(customization, 1)

    def __isRandomValue(self, value):
        return value is None or value == ny_constants.RANDOM_VALUE

    def getFillerConvertCost(self):
        return self._config.get(CraftCostConsts.FILLER_CONVERT_COST, 0)

    def calculateMegaCraftCost(self, megaCount):
        return self.__getMegaToyCost(megaCount)

    def calculateCraftCost(self, typeID=None, settingID=None, rank=None):
        if self.__isRandomValue(rank):
            baseCost = self.__getRandomToyCost()
        else:
            baseCost = self.__getUsualToyCost(CraftCostConsts.COST_BY_RANK, rank)
        result = baseCost
        if not self.__isRandomValue(settingID):
            result += baseCost * self.__getSettingCostFactor()
        if not self.__isRandomValue(typeID):
            customization = new_year.getObjectByToyType(ny_constants.ToyTypes.ALL[typeID])
            result += baseCost * self.__getCustomizationCostFactor(customization)
        return result

    def calculateOldCraftCost(self, toyID, year):
        toy = collectibles.g_cache[year].toys[toyID]
        return self.__getUsualToyCost(self.__oldCraftCost[year], int(toy.rank))

    __oldCraftCost = {'ny18': CraftCostConsts.NY18_COST_BY_RANK,
     'ny19': CraftCostConsts.NY19_COST_BY_RANK}
