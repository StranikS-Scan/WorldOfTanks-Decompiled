# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/auxiliary/selected_filters.py
from collections import OrderedDict
from gui.impl.gen.view_models.views.selected_filters_model import SelectedFiltersModel
from gui.impl.gen.view_models.views.sub_filter_model import SubFilterModel

class BaseSelectedFilters(object):
    __slots__ = ('__items', '__filters', '__filteredItems', '__selectedFilters')

    def __init__(self):
        self.__items = tuple()
        self.__filteredItems = tuple()
        self.__selectedFilters = []
        self.__filters = OrderedDict()

    def setItems(self, items, model=None):
        self.__items = tuple(items)
        self.__filteredItems = self._createFilteredItems()
        if model is not None:
            model.setSelectedFilterCount(len(self.__filteredItems))
            model.setTotalFilterCount(len(self.__items))
        return

    def changeFilter(self, filterName, model):
        filters = model.getFilters()
        self.__selectedFilters = []
        for filterModel in filters:
            if filterName == filterModel.getName():
                filterModel.setSelected(not filterModel.getSelected())
            if filterModel.getSelected():
                self.__selectedFilters.append(filterModel.getName())

        filters.invalidate()
        if not self.__selectedFilters:
            model.setFilterIsEnabled(False)
            self.__filteredItems = self.__items
        else:
            model.setFilterIsEnabled(True)
            self.__filteredItems = self._createFilteredItems()
        model.setSelectedFilterCount(len(self.__filteredItems))
        model.setTotalFilterCount(len(self.__items))

    def initFilters(self, model):
        filters = model.getFilters()
        filters.clear()
        for filterName in self.__filters:
            filterModel = self._createSubFilterModel(filterName)
            filters.addViewModel(filterModel)

        filters.invalidate()
        model.setSelectedFilterCount(len(self.__filteredItems))
        model.setTotalFilterCount(len(self.__items))

    def resetFilters(self, model):
        for filterModel in model.getFilters():
            filterModel.setSelected(False)

        model.getFilters().invalidate()
        self.__filteredItems = self.__items

    def getItems(self):
        return self.__filteredItems

    def clear(self):
        self.__filteredItems = None
        self.__items = None
        self.__filters = None
        self.__selectedFilters = None
        return

    @staticmethod
    def _createSubFilterModel(filterName):
        filterModel = SubFilterModel()
        filterModel.setName(filterName)
        filterModel.setSelected(False)
        return filterModel

    def _createFilteredItems(self):
        result = tuple((item for item in self.__items if self._checkItem(item)))
        return result

    def _checkItem(self, item):
        result = True
        for filterName in self.__selectedFilters:
            result &= self.__filters[filterName](item)

        return result

    def _addFilter(self, filterName, filterMethod):
        self.__filters[filterName] = filterMethod

    def _delFilter(self, filterName):
        del self.__filters[filterName]

    def _clearFilters(self):
        self.__filters.clear()
