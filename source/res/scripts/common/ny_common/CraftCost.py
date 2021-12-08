# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ny_common/CraftCost.py
import typing
from items.components import ny_constants
from items import collectibles
from items.components.ny_constants import RANDOM_VALUE
from ny_common.settings import CraftCostConsts
if typing.TYPE_CHECKING:
    from typing import Optional
    from items.components.ny_constants import FillerState

class CraftCostConfig(object):
    __slots__ = ('_config',)

    def __init__(self, config):
        self._config = config

    def __getMegaToyCost(self, yearCollection, toyCount):
        megaCost = self._config.get(yearCollection, (0,))
        return megaCost[-1] if toyCount >= len(megaCost) else megaCost[toyCount]

    def __getUsualToyCost(self, yearCollection, rank):
        return self._config.get(yearCollection)[rank - 1]

    def __getUsualMegaToyCost(self, yearCollection):
        return self._config.get(yearCollection)

    def getFillerShardsCost(self):
        return self._config.get(CraftCostConsts.CRAFT_COST_PAID_FILLER, 0)

    def getFillerConvertCost(self):
        return self._config.get(CraftCostConsts.FILLER_CONVERT_COST, 0)

    def calculateMegaCraftCost(self, megaCount):
        return self.__getMegaToyCost(CraftCostConsts.MEGA_COST_BY_COUNT, megaCount)

    def calculateCraftCost(self, typeID=RANDOM_VALUE, settingID=RANDOM_VALUE, fillerState=None):
        config = self._config
        result = config[CraftCostConsts.CRAFT_COST_RANDOM_SETTING] if settingID == RANDOM_VALUE else config[CraftCostConsts.CRAFT_COST_SPECIFIED_SETTING]
        result += config[CraftCostConsts.CRAFT_COST_RANDOM_TYPE] if typeID == RANDOM_VALUE else config[CraftCostConsts.CRAFT_COST_SPECIFIED_TYPE]
        if fillerState == ny_constants.FillerState.USE_SHARDS:
            result += config[CraftCostConsts.CRAFT_COST_PAID_FILLER]
        return result

    def calculateOldCraftCost(self, toyID, year):
        toy = collectibles.g_cache[year].toys[toyID]
        return self.__getMegaToyCost(self.__oldMegaCost[year], 0) if toy.isMegaToy() else self.__getUsualToyCost(self.__oldCraftCost[year], int(toy.rank))

    __oldCraftCost = {'ny18': CraftCostConsts.NY18_COST_BY_RANK,
     'ny19': CraftCostConsts.NY19_COST_BY_RANK,
     'ny20': CraftCostConsts.NY20_COST_BY_RANK,
     'ny21': CraftCostConsts.NY21_COST_BY_RANK}
    __oldMegaCost = {'ny20': CraftCostConsts.NY20_MEGA_COST,
     'ny21': CraftCostConsts.NY21_MEGA_COST}
