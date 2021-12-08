# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/break_decorations/ny_break_shards_tip.py
from collections import namedtuple
from gui.impl.gen.view_models.views.lobby.new_year.views.break_decorations.ny_break_shards_tip_model import NyBreakShardsTipModel
from helpers import dependency
from gui.impl.lobby.new_year.craft.components import MegaDeviceState
from skeletons.new_year import INewYearCraftMachineController
_FilteredToysInfo = namedtuple('_FilteredToysInfo', ('toys', 'unseenToys', 'toyCount', 'totalToyCount'))
_ToysInfo = namedtuple('_ToysInfo', ('toyTypes', 'toyRanks'))
_ANIMATION_DELAY = 0.5

class BaseShardsTip(object):

    def __init__(self, tipsModel):
        super(BaseShardsTip, self).__init__()
        self._shardsCount = 0

    def setShardsCount(self, count):
        self._shardsCount = count

    def update(self, model):
        raise NotImplementedError

    @staticmethod
    def _updateModel(decorationtType, shardsShortage, state, model):
        model.setDecorationType(decorationtType)
        model.setCurrentState(state)
        model.setShardsCountLeft(shardsShortage)


class CraftTip(BaseShardsTip):
    _craftCtrl = dependency.descriptor(INewYearCraftMachineController)

    def update(self, model):
        craftCost = self._craftCtrl.calculateSelectedToyCraftCost()
        megaDeviceState = self._craftCtrl.getActualMegaDeviceState()
        desiredToyType = self._craftCtrl.getSelectedToyType()
        shardsShortage = max(craftCost - self._shardsCount, 0)
        if megaDeviceState == MegaDeviceState.ALL_MEGA_TOYS_COLLECTED_ERROR:
            state = NyBreakShardsTipModel.SHARDS_ALL_MEGA_TOYS_COLLECTED
        elif shardsShortage == 0:
            state = NyBreakShardsTipModel.SHARDS_ENOUGH_TO_CREATE
        else:
            state = NyBreakShardsTipModel.SHARDS_NOT_ENOUGH_TO_CREATE
        self._updateModel(decorationtType=desiredToyType, shardsShortage=shardsShortage, state=state, model=model)
