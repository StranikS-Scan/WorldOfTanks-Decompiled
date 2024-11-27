# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/vehicle_selection_models/selectable_reward_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.vehicle_selection_models.discount_vehicle_bonus_model import DiscountVehicleBonusModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.vehicle_selection_models.selectable_reward_category_model import SelectableRewardCategoryModel

class SelectableRewardViewModel(ViewModel):
    __slots__ = ('onCategorySelect', 'onFilterReset', 'onSelectReward', 'onClose', 'onConfirm')

    def __init__(self, properties=4, commands=5):
        super(SelectableRewardViewModel, self).__init__(properties=properties, commands=commands)

    def getCategories(self):
        return self._getArray(0)

    def setCategories(self, value):
        self._setArray(0, value)

    @staticmethod
    def getCategoriesType():
        return SelectableRewardCategoryModel

    def getTotalRewardsCount(self):
        return self._getNumber(1)

    def setTotalRewardsCount(self, value):
        self._setNumber(1, value)

    def getSelectedRewardsCount(self):
        return self._getNumber(2)

    def setSelectedRewardsCount(self, value):
        self._setNumber(2, value)

    def getSelectableRewards(self):
        return self._getArray(3)

    def setSelectableRewards(self, value):
        self._setArray(3, value)

    @staticmethod
    def getSelectableRewardsType():
        return DiscountVehicleBonusModel

    def _initialize(self):
        super(SelectableRewardViewModel, self)._initialize()
        self._addArrayProperty('categories', Array())
        self._addNumberProperty('totalRewardsCount', 0)
        self._addNumberProperty('selectedRewardsCount', 0)
        self._addArrayProperty('selectableRewards', Array())
        self.onCategorySelect = self._addCommand('onCategorySelect')
        self.onFilterReset = self._addCommand('onFilterReset')
        self.onSelectReward = self._addCommand('onSelectReward')
        self.onClose = self._addCommand('onClose')
        self.onConfirm = self._addCommand('onConfirm')
