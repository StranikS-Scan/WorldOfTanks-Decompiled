# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lootbox_system/main_view_model.py
from enum import IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.lootbox_system.submodels.has_boxes_view_model import HasBoxesViewModel
from gui.impl.gen.view_models.views.lobby.lootbox_system.submodels.multiple_boxes_rewards_view_model import MultipleBoxesRewardsViewModel
from gui.impl.gen.view_models.views.lobby.lootbox_system.submodels.no_boxes_view_model import NoBoxesViewModel
from gui.impl.gen.view_models.views.lobby.lootbox_system.submodels.single_box_rewards_view_model import SingleBoxRewardsViewModel

class SubViewID(IntEnum):
    NO_BOXES = 0
    HAS_BOXES = 1
    SINGLE_BOX_REWARDS = 2
    MULTIPLE_BOXES_REWARDS = 3


class MainViewModel(ViewModel):
    __slots__ = ('onResourcesLoadCompleted',)

    def __init__(self, properties=5, commands=1):
        super(MainViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def noBoxes(self):
        return self._getViewModel(0)

    @staticmethod
    def getNoBoxesType():
        return NoBoxesViewModel

    @property
    def hasBoxes(self):
        return self._getViewModel(1)

    @staticmethod
    def getHasBoxesType():
        return HasBoxesViewModel

    @property
    def singleBoxRewards(self):
        return self._getViewModel(2)

    @staticmethod
    def getSingleBoxRewardsType():
        return SingleBoxRewardsViewModel

    @property
    def multipleBoxesRewards(self):
        return self._getViewModel(3)

    @staticmethod
    def getMultipleBoxesRewardsType():
        return MultipleBoxesRewardsViewModel

    def getSubViewIDs(self):
        return self._getArray(4)

    def setSubViewIDs(self, value):
        self._setArray(4, value)

    @staticmethod
    def getSubViewIDsType():
        return int

    def _initialize(self):
        super(MainViewModel, self)._initialize()
        self._addViewModelProperty('noBoxes', NoBoxesViewModel())
        self._addViewModelProperty('hasBoxes', HasBoxesViewModel())
        self._addViewModelProperty('singleBoxRewards', SingleBoxRewardsViewModel())
        self._addViewModelProperty('multipleBoxesRewards', MultipleBoxesRewardsViewModel())
        self._addArrayProperty('subViewIDs', Array())
        self.onResourcesLoadCompleted = self._addCommand('onResourcesLoadCompleted')
