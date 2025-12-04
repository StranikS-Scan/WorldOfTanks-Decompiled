# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/vehicle_selection_models/selectable_reward_category_model.py
from frameworks.wulf import ViewModel

class SelectableRewardCategoryModel(ViewModel):
    __slots__ = ()
    UNDEFIEND_REVARD_INDEX = -1

    def __init__(self, properties=9, commands=0):
        super(SelectableRewardCategoryModel, self).__init__(properties=properties, commands=commands)

    def getVariadicID(self):
        return self._getString(0)

    def setVariadicID(self, value):
        self._setString(0, value)

    def getTabIndex(self):
        return self._getNumber(1)

    def setTabIndex(self, value):
        self._setNumber(1, value)

    def getDiscount(self):
        return self._getNumber(2)

    def setDiscount(self, value):
        self._setNumber(2, value)

    def getIsSelected(self):
        return self._getBool(3)

    def setIsSelected(self, value):
        self._setBool(3, value)

    def getLevel(self):
        return self._getNumber(4)

    def setLevel(self, value):
        self._setNumber(4, value)

    def getSelectedRewardIndex(self):
        return self._getNumber(5)

    def setSelectedRewardIndex(self, value):
        self._setNumber(5, value)

    def getTooltipContentId(self):
        return self._getString(6)

    def setTooltipContentId(self, value):
        self._setString(6, value)

    def getTooltipId(self):
        return self._getString(7)

    def setTooltipId(self, value):
        self._setString(7, value)

    def getSelectedVehicle(self):
        return self._getString(8)

    def setSelectedVehicle(self, value):
        self._setString(8, value)

    def _initialize(self):
        super(SelectableRewardCategoryModel, self)._initialize()
        self._addStringProperty('variadicID', '')
        self._addNumberProperty('tabIndex', 0)
        self._addNumberProperty('discount', 0)
        self._addBoolProperty('isSelected', False)
        self._addNumberProperty('level', 0)
        self._addNumberProperty('selectedRewardIndex', -1)
        self._addStringProperty('tooltipContentId', '')
        self._addStringProperty('tooltipId', '')
        self._addStringProperty('selectedVehicle', '')
