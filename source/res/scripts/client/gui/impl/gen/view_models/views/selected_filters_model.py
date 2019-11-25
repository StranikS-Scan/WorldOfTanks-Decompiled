# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/selected_filters_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class SelectedFiltersModel(ViewModel):
    __slots__ = ('onFilterChanged', 'onFilterReset')

    def __init__(self, properties=4, commands=2):
        super(SelectedFiltersModel, self).__init__(properties=properties, commands=commands)

    def getSelectedFilterCount(self):
        return self._getNumber(0)

    def setSelectedFilterCount(self, value):
        self._setNumber(0, value)

    def getTotalFilterCount(self):
        return self._getNumber(1)

    def setTotalFilterCount(self, value):
        self._setNumber(1, value)

    def getFilterIsEnabled(self):
        return self._getBool(2)

    def setFilterIsEnabled(self, value):
        self._setBool(2, value)

    def getFilters(self):
        return self._getArray(3)

    def setFilters(self, value):
        self._setArray(3, value)

    def _initialize(self):
        super(SelectedFiltersModel, self)._initialize()
        self._addNumberProperty('selectedFilterCount', 0)
        self._addNumberProperty('totalFilterCount', 0)
        self._addBoolProperty('filterIsEnabled', False)
        self._addArrayProperty('filters', Array())
        self.onFilterChanged = self._addCommand('onFilterChanged')
        self.onFilterReset = self._addCommand('onFilterReset')
