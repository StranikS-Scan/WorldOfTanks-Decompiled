# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ny_common/CraftCost.py
import typing
from items.components import ny_constants
from items import collectibles
from items.components.ny_constants import RANDOM_VALUE, YEARS, MIN_TOY_RANK
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
        return megaCost[-1 if toyCount >= len(megaCost) else toyCount]

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

    def calculateCraftCost(self, typeID=RANDOM_VALUE, settingID=RANDOM_VALUE, rank=RANDOM_VALUE, fillerState=None):
        config = self._config
        result = rankCost = config[CraftCostConsts.CRAFT_COST_RANDOM_RANK] if rank == RANDOM_VALUE else config[CraftCostConsts.CRAFT_COST_SPECIFIED_RANK][rank - MIN_TOY_RANK]
        result += config[CraftCostConsts.CRAFT_COST_RANDOM_SETTING] if settingID == RANDOM_VALUE else config[CraftCostConsts.CRAFT_COST_SPECIFIED_SETTING] + rankCost
        result += config[CraftCostConsts.CRAFT_COST_RANDOM_TYPE] if typeID == RANDOM_VALUE else config[CraftCostConsts.CRAFT_COST_SPECIFIED_TYPE] + rankCost
        if fillerState == ny_constants.FillerState.USE_SHARDS:
            result += config[CraftCostConsts.CRAFT_COST_PAID_FILLER]
        return result

    def calculateOldCraftCost(self, toyID, year):
        toy = collectibles.g_cache[year].toys[toyID]
        yearInt = YEARS.getYearNumFromYearStr(year)
        return self.__getMegaToyCost(CraftCostConsts.MEGA_TOYS[yearInt], 0) if toy.isMegaToy() else self.__getUsualToyCost(CraftCostConsts.USUAL_TOYS[yearInt], int(toy.rank))
