# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/craft/components/craft_cost_block.py
from items.components.ny_constants import RANDOM_VALUE, MIN_TOY_RANK
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext
from .shared_stuff import mapToyParamsFromCraftUiToSrv
from .data_nodes import ViewModelDataNode

class CraftCostBlock(ViewModelDataNode):
    _itemsCache = dependency.descriptor(IItemsCache)
    _lobbyCtx = dependency.descriptor(ILobbyContext)

    def __init__(self, viewModel):
        super(CraftCostBlock, self).__init__(viewModel)
        self.__craftCost = 0
        self.__toyTypeID = self.__toySettingID = RANDOM_VALUE
        self.__toyRankID = MIN_TOY_RANK

    def getCraftCost(self):
        return self.__craftCost

    def getCraftParams(self):
        return (self.__toyTypeID, self.__toySettingID, self.__toyRankID)

    def updateData(self):
        toyTypeIdx, toySettingIdx, toyRankIdx, _ = self._nodesHolder.regularToysBlock.getToyConfig()
        fillerState = self._nodesHolder.antiduplicator.getAntiDuplicatorState()
        self.__craftCost = self._craftCtrl.calculateToyCraftCost(toyTypeIdx=toyTypeIdx, toySettingIdx=toySettingIdx, toyRankIdx=toyRankIdx, fillerState=fillerState)
        self.__toyTypeID, self.__toySettingID, self.__toyRankID = mapToyParamsFromCraftUiToSrv(toyTypeIdx, toySettingIdx, toyRankIdx)
        with self._viewModel.transaction() as tx:
            tx.setCraftPrice(self.__craftCost)
