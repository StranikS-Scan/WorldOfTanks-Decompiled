# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: one_time_gift/scripts/client/one_time_gift/gui/impl/gen/view_models/views/lobby/one_time_gift_view_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel
from one_time_gift.gui.impl.gen.view_models.views.lobby.branch_selection_view_model import BranchSelectionViewModel
from one_time_gift.gui.impl.gen.view_models.views.lobby.intro_view_model import IntroViewModel
from one_time_gift.gui.impl.gen.view_models.views.lobby.one_time_gift_reward_view_model import OneTimeGiftRewardViewModel

class MainViews(IntEnum):
    INTRO = 0
    BRANCH_SELECTION = 1
    BRANCH_REWARD = 2
    PREMIUM_VEHICLES_REWARD = 3
    ADDITIONAL_REWARD = 4
    COLLECTORS_COMPENSATION_REWARD = 5


class OneTimeGiftViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(OneTimeGiftViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def introModel(self):
        return self._getViewModel(0)

    @staticmethod
    def getIntroModelType():
        return IntroViewModel

    @property
    def branchSelectionModel(self):
        return self._getViewModel(1)

    @staticmethod
    def getBranchSelectionModelType():
        return BranchSelectionViewModel

    @property
    def rewardModel(self):
        return self._getViewModel(2)

    @staticmethod
    def getRewardModelType():
        return OneTimeGiftRewardViewModel

    def getViewType(self):
        return MainViews(self._getNumber(3))

    def setViewType(self, value):
        self._setNumber(3, value.value)

    def _initialize(self):
        super(OneTimeGiftViewModel, self)._initialize()
        self._addViewModelProperty('introModel', IntroViewModel())
        self._addViewModelProperty('branchSelectionModel', BranchSelectionViewModel())
        self._addViewModelProperty('rewardModel', OneTimeGiftRewardViewModel())
        self._addNumberProperty('viewType')
