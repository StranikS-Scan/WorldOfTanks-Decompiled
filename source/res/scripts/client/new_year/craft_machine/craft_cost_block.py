# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/craft_machine/craft_cost_block.py
from items.components.ny_constants import YEARS_INFO, ToySettings, RANDOM_VALUE
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext
from gui.impl.new_year.sounds import NewYearSoundsManager, NewYearSoundEvents
from .shared_stuff import MegaDeviceState, mapToyParamsFromCraftUiToSrv
from .data_nodes import ViewModelDataNode

class CraftCostBlock(ViewModelDataNode):
    _itemsCache = dependency.descriptor(IItemsCache)
    _lobbyCtx = dependency.descriptor(ILobbyContext)

    def __init__(self, viewModel):
        super(CraftCostBlock, self).__init__(viewModel)
        self.__craftCost = 0
        self.__toyTypeID = self.__toySettingID = self.__toyRankID = RANDOM_VALUE

    def getCraftCost(self):
        return self.__craftCost

    def getCraftParams(self):
        return (self.__toyTypeID, self.__toySettingID, self.__toyRankID)

    def updateData(self):
        isMegaDeviceTurnedOn = self._nodesHolder.megaDevice.getState() in MegaDeviceState.ACTIVATED
        toyTypeIdx, toySettingIdx, toyRankIdx, _ = self._nodesHolder.regularToysBlock.getToyConfig()
        craftCost = self._craftCtrl.calculateToyCraftCost(isMegaToy=isMegaDeviceTurnedOn, toyTypeIdx=toyTypeIdx, toySettingIdx=toySettingIdx, toyRankIdx=toyRankIdx)
        self.__toyTypeID, self.__toySettingID, self.__toyRankID = mapToyParamsFromCraftUiToSrv(toyTypeIdx, toySettingIdx, toyRankIdx)
        if isMegaDeviceTurnedOn:
            self.__toySettingID = YEARS_INFO.CURRENT_SETTING_IDS_BY_NAME[ToySettings.MEGA_TOYS]
        shardsCount = self._itemsCache.items.festivity.getShardsCount()
        if shardsCount < craftCost:
            NewYearSoundsManager.playEvent(NewYearSoundEvents.COST_TOYS_NOT_CHANGE)
        elif self.__craftCost > craftCost:
            NewYearSoundsManager.playEvent(NewYearSoundEvents.COST_TOYS_DOWN)
        elif self.__craftCost < craftCost:
            NewYearSoundsManager.playEvent(NewYearSoundEvents.COST_TOYS_UP)
        self.__craftCost = craftCost
        with self._viewModel.transaction() as tx:
            tx.setCraftPrice(self.__craftCost)
