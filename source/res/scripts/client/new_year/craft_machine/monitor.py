# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/craft_machine/monitor.py
from helpers import dependency
from skeletons.new_year import INewYearController
from .data_nodes import ViewModelDataNode
from .shared_stuff import AntiduplicatorState, MegaDeviceState, RANDOM_TOY_CONFIG_INDEX
from .texts import TOY_TYPE_STRINGS, TOY_RANKS_STRINGS, TOY_SETTING_STRINGS, TOY_PLACES_STRINGS

class CraftMonitor(ViewModelDataNode):
    _nyController = dependency.descriptor(INewYearController)

    def updateData(self):
        with self._viewModel.transaction() as tx:
            shardsCount = self._nodesHolder.shardsStorage.getShards()
            tx.setShardsCount(shardsCount)
            uniqueMegaToysCount = self._nodesHolder.megaToysStorage.getUniqueMegaToysCount()
            tx.setCountMegaToys(uniqueMegaToysCount)
            antiduplicatorState = self._nodesHolder.antiduplicator.getState()
            if antiduplicatorState == AntiduplicatorState.ERROR:
                tx.setState(tx.HAS_NOT_FILLERS)
                return
            megaDeviceState = self._nodesHolder.megaDevice.getState()
            if megaDeviceState == MegaDeviceState.ALL_MEGA_TOYS_COLLECTED_ERROR:
                tx.setState(tx.FULL_MEGA)
                return
            hasRandomRegularToyParam = self.__hasRandomRegularToyParam()
            if antiduplicatorState == AntiduplicatorState.ACTIVE:
                tx.setAntiduplicateEnabled(True)
                if self.__isRegularToysCollected():
                    tx.setState(tx.FULL_REGULAR)
                    return
                if hasRandomRegularToyParam:
                    tx.setState(tx.HAS_RANDOM_PARAM)
                    return
                if self.__isFullRegularToysGroup():
                    tx.setState(tx.FULL_REGULAR_SUBGROUP)
                    return
            elif antiduplicatorState == AntiduplicatorState.INACTIVE:
                tx.setAntiduplicateEnabled(False)
            if shardsCount == 0:
                tx.setState(tx.SHARDS_NOT_AVAILABLE)
                return
            craftCost = self._nodesHolder.craftCostBlock.getCraftCost()
            if megaDeviceState == MegaDeviceState.ACTIVE:
                if craftCost > shardsCount:
                    tx.setState(tx.NOT_ENOUGH_SHARDS_FOR_MEGA)
                else:
                    tx.setState(tx.PARAMS_MEGA)
                return
            self.__updateRegularToysVisuals(tx)
            if craftCost > shardsCount:
                tx.setState(tx.NOT_ENOUGH_SHARDS_FOR_REGULAR)
            else:
                tx.setState(tx.PARAMS_REGULAR)

    def _onInit(self):
        self.updateData()

    def _onDestroy(self):
        pass

    def __hasRandomRegularToyParam(self):
        toyType, toySetting, toyRank, _ = self._nodesHolder.regularToysBlock.getToyConfig()
        return RANDOM_TOY_CONFIG_INDEX in (toyType, toySetting, toyRank)

    def __updateRegularToysVisuals(self, model):
        toyType, toySetting, toyRank, toyPlace = self._nodesHolder.regularToysBlock.getToyConfig()
        model.setType(TOY_TYPE_STRINGS[toyType])
        model.setLevel(TOY_RANKS_STRINGS[toyRank])
        model.setSetting(TOY_SETTING_STRINGS[toySetting])
        model.setObjectType(TOY_PLACES_STRINGS[toyPlace])

    def __isFullRegularToysGroup(self):
        toyType, toySetting, toyRank = self._nodesHolder.craftCostBlock.getCraftParams()
        return self._nyController.isFullRegularToysGroup(toyType, toySetting, toyRank)

    def __isRegularToysCollected(self):
        return self._nyController.isRegularToysCollected()
