# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/ui_kit/filter_counter_model.py
from frameworks.wulf import ViewModel

class FilterCounterModel(ViewModel):
    __slots__ = ('onResetBtnClick',)

    def getCurrentCount(self):
        return self._getNumber(0)

    def setCurrentCount(self, value):
        self._setNumber(0, value)

    def getTotalCount(self):
        return self._getNumber(1)

    def setTotalCount(self, value):
        self._setNumber(1, value)

    def getIsFilterApplied(self):
        return self._getBool(2)

    def setIsFilterApplied(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(FilterCounterModel, self)._initialize()
        self._addNumberProperty('currentCount', 0)
        self._addNumberProperty('totalCount', 0)
        self._addBoolProperty('isFilterApplied', False)
        self.onResetBtnClick = self._addCommand('onResetBtnClick')
