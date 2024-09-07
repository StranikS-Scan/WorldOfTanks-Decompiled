# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: winback/scripts/client/winback/gui/impl/gen/view_models/views/lobby/views/winback_selectable_reward_view_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from winback.gui.impl.gen.view_models.views.lobby.views.selectable_reward_category_model import SelectableRewardCategoryModel

class SelectableRewardName(Enum):
    VEHICLE = 'vehicle'
    COMPENSATION = 'compensation'


class WinbackSelectableRewardViewModel(ViewModel):
    __slots__ = ('onCategorySelect', 'onFilterReset', 'onSelectReward', 'onClose', 'onConfirm')
    VEHICLE_LEVEL = 'vehicleLevel'
    REWARD_INDEX = 'rewardIndex'

    def __init__(self, properties=5, commands=5):
        super(WinbackSelectableRewardViewModel, self).__init__(properties=properties, commands=commands)

    def getCategories(self):
        return self._getArray(0)

    def setCategories(self, value):
        self._setArray(0, value)

    @staticmethod
    def getCategoriesType():
        return SelectableRewardCategoryModel

    def getProgressionName(self):
        return self._getString(1)

    def setProgressionName(self, value):
        self._setString(1, value)

    def getTotalRewardsCount(self):
        return self._getNumber(2)

    def setTotalRewardsCount(self, value):
        self._setNumber(2, value)

    def getSelectedRewardsCount(self):
        return self._getNumber(3)

    def setSelectedRewardsCount(self, value):
        self._setNumber(3, value)

    def getSelectableRewards(self):
        return self._getArray(4)

    def setSelectableRewards(self, value):
        self._setArray(4, value)

    @staticmethod
    def getSelectableRewardsType():
        return BonusModel

    def _initialize(self):
        super(WinbackSelectableRewardViewModel, self)._initialize()
        self._addArrayProperty('categories', Array())
        self._addStringProperty('progressionName', '')
        self._addNumberProperty('totalRewardsCount', 0)
        self._addNumberProperty('selectedRewardsCount', 0)
        self._addArrayProperty('selectableRewards', Array())
        self.onCategorySelect = self._addCommand('onCategorySelect')
        self.onFilterReset = self._addCommand('onFilterReset')
        self.onSelectReward = self._addCommand('onSelectReward')
        self.onClose = self._addCommand('onClose')
        self.onConfirm = self._addCommand('onConfirm')
