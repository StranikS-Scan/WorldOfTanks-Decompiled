# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/auxiliary/selected_filters.py
import operator
from collections import OrderedDict, namedtuple
from gui.impl.gen.view_models.views.lobby.tank_setup.common.filters_model import FiltersModel
from gui.impl.gen.view_models.views.lobby.tank_setup.common.sub_filter_model import SubFilterModel
_FilterData = namedtuple('_FilterData', 'method, operator')

def getFilterDecorator(selectedFitler, model):

    def makeFilter(items):
        return selectedFitler.getItems(items, model)

    return makeFilter if selectedFitler is not None else None


class BaseSelectedFilters(object):
    __slots__ = ('__filters', '_selectedFilters')

    def __init__(self):
        self._selectedFilters = []
        self.__filters = OrderedDict()

    def changeFilter(self, filterName, model):
        filters = model.getFilters()
        self._selectedFilters = []
        for filterModel in filters:
            if filterName == filterModel.getName():
                filterModel.setIsSelected(not filterModel.getIsSelected())
            if filterModel.getIsSelected():
                self._selectedFilters.append(filterModel.getName())

        filters.invalidate()
        if not self._selectedFilters:
            model.setIsEnabled(False)
        else:
            model.setIsEnabled(True)

    def initFilters(self, model):
        filters = model.getFilters()
        filters.clear()
        for filterName in self.__filters:
            filterModel = self._createSubFilterModel(filterName)
            filters.addViewModel(filterModel)

        filters.invalidate()

    def resetFilters(self, model):
        for filterModel in model.getFilters():
            filterModel.setIsSelected(False)

        self._selectedFilters = []
        model.setIsEnabled(False)
        model.getFilters().invalidate()

    def getItems(self, items, model):
        filteredItems = self._getFilteredItems(items)
        model.setSelectedFilterCount(len(filteredItems))
        model.setTotalFilterCount(len(items))
        return filteredItems

    def checkItem(self, item):
        result = True
        for idx, filterName in enumerate(self._selectedFilters):
            filterData = self.__filters[filterName]
            if idx == 0 and filterData.operator is operator.or_:
                result = False
            result = filterData.operator(self.__filters[filterName].method(item), result)

        return result

    def clear(self):
        self.__filters = None
        self._selectedFilters = None
        return

    def _getFilteredItems(self, items):
        result = tuple((item for item in items if self.checkItem(item)))
        return result

    @staticmethod
    def _createSubFilterModel(filterName):
        filterModel = SubFilterModel()
        filterModel.setName(filterName)
        filterModel.setIsSelected(False)
        return filterModel

    def _addFilter(self, filterName, filterMethod, op=operator.and_):
        self.__filters[filterName] = _FilterData(filterMethod, op)

    def _delFilter(self, filterName):
        del self.__filters[filterName]

    def _clearFilters(self):
        self.__filters.clear()
