# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/common/tooltips/selected_rewards_tooltip_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.common.tooltips.selected_rewards_tooltip_category_model import SelectedRewardsTooltipCategoryModel

class SelectedRewardsTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(SelectedRewardsTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getCategories(self):
        return self._getArray(0)

    def setCategories(self, value):
        self._setArray(0, value)

    @staticmethod
    def getCategoriesType():
        return SelectedRewardsTooltipCategoryModel

    def getTotalSelected(self):
        return self._getNumber(1)

    def setTotalSelected(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(SelectedRewardsTooltipViewModel, self)._initialize()
        self._addArrayProperty('categories', Array())
        self._addNumberProperty('totalSelected', 0)
