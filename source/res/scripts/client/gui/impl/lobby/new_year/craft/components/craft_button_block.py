# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/craft/components/craft_button_block.py
from helpers import dependency
from items.components.ny_constants import FillerState
from skeletons.new_year import INewYearController
from .data_nodes import ViewModelDataNode
from .shared_stuff import MegaDeviceState, RANDOM_TOY_CONFIG_INDEX

class CraftButtonBlock(ViewModelDataNode):
    __nyController = dependency.descriptor(INewYearController)

    def updateData(self):
        shardsCount = self._nodesHolder.shardsStorage.getShardsCount()
        if shardsCount == 0:
            self._viewModel.setEnableCraftBtn(False)
            self._viewModel.setHasShards(False)
            return
        craftCost = self._nodesHolder.craftCostBlock.getCraftCost()
        if craftCost > shardsCount:
            self._viewModel.setEnableCraftBtn(False)
            self._viewModel.setHasShards(False)
            return
        self._viewModel.setHasShards(True)
        fillerState = self._nodesHolder.antiduplicator.getState()
        if fillerState == FillerState.ERROR:
            self._viewModel.setEnableCraftBtn(False)
            return
        megaDeviceState = self._nodesHolder.megaDevice.getState()
        if megaDeviceState in MegaDeviceState.ERRORS:
            self._viewModel.setEnableCraftBtn(False)
            return
        if fillerState.isActive and (self.__hasRandomToyParam() or self.__isFullRegularToys()):
            self._viewModel.setEnableCraftBtn(False)
            return
        if fillerState == FillerState.USE_CHARGES and self._nodesHolder.fillersStorage.getFillersCount() == 0:
            self._viewModel.setEnableCraftBtn(False)
            return
        self._viewModel.setEnableCraftBtn(True)

    def _onInit(self):
        self.updateData()

    def _onDestroy(self):
        pass

    def __hasRandomToyParam(self):
        toyType, toySetting, _, __ = self._nodesHolder.regularToysBlock.getToyConfig()
        return RANDOM_TOY_CONFIG_INDEX in (toyType, toySetting)

    def __isFullRegularToys(self):
        toyType, toySetting, toyRank = self._nodesHolder.craftCostBlock.getCraftParams()
        return self.__nyController.isFullRegularToysGroup(toyType, toySetting, toyRank)
