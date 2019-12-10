# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/craft_machine/craft_button_block.py
from helpers import dependency
from skeletons.new_year import INewYearController
from .data_nodes import ViewModelDataNode
from .shared_stuff import AntiduplicatorState, MegaDeviceState, RANDOM_TOY_CONFIG_INDEX

class CraftButtonBlock(ViewModelDataNode):
    _nyController = dependency.descriptor(INewYearController)

    def updateData(self):
        shardsCount = self._nodesHolder.shardsStorage.getShards()
        if shardsCount == 0:
            self._viewModel.setEnableCraftBtn(False)
            return
        craftCost = self._nodesHolder.craftCostBlock.getCraftCost()
        if craftCost > shardsCount:
            self._viewModel.setEnableCraftBtn(False)
            return
        antiduplicatorState = self._nodesHolder.antiduplicator.getState()
        if antiduplicatorState == AntiduplicatorState.ERROR:
            self._viewModel.setEnableCraftBtn(False)
            return
        megaDeviceState = self._nodesHolder.megaDevice.getState()
        if megaDeviceState in MegaDeviceState.ERRORS:
            self._viewModel.setEnableCraftBtn(False)
            return
        if antiduplicatorState == AntiduplicatorState.ACTIVE and (self.__hasRandomToyParam() or self.__isFullRegularToys()):
            self._viewModel.setEnableCraftBtn(False)
            return
        self._viewModel.setEnableCraftBtn(True)

    def _onInit(self):
        self.updateData()

    def _onDestroy(self):
        pass

    def __hasRandomToyParam(self):
        toyType, toySetting, toyRank, _ = self._nodesHolder.regularToysBlock.getToyConfig()
        return RANDOM_TOY_CONFIG_INDEX in (toyType, toySetting, toyRank)

    def __isFullRegularToys(self):
        toyType, toySetting, toyRank = self._nodesHolder.craftCostBlock.getCraftParams()
        return self._nyController.isFullRegularToysGroup(toyType, toySetting, toyRank)
