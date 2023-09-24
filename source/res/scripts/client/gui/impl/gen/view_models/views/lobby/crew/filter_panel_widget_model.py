# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/filter_panel_widget_model.py
from enum import Enum
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.crew.common.filter_toggle_group_model import FilterToggleGroupModel
from gui.impl.gen.view_models.views.lobby.crew.common.range_model import RangeModel

class FilterPanelType(Enum):
    DEFAULT = 'default'
    BARRACKS = 'barracks'
    MEMBERCHANGE = 'memberChange'
    TANKCHANGE = 'tankChange'
    PERSONALDATA = 'personalData'


class FilterPanelWidgetModel(ViewModel):
    __slots__ = ('onSearch', 'onUpdateFilter', 'onResetFilter')

    def __init__(self, properties=15, commands=3):
        super(FilterPanelWidgetModel, self).__init__(properties=properties, commands=commands)

    @property
    def amountInfo(self):
        return self._getViewModel(0)

    @staticmethod
    def getAmountInfoType():
        return RangeModel

    @property
    def filter(self):
        return self._getViewModel(1)

    @staticmethod
    def getFilterType():
        return FilterToggleGroupModel

    def getIsSearchEnabled(self):
        return self._getBool(2)

    def setIsSearchEnabled(self, value):
        self._setBool(2, value)

    def getTitle(self):
        return self._getResource(3)

    def setTitle(self, value):
        self._setResource(3, value)

    def getPopoverTooltipHeader(self):
        return self._getResource(4)

    def setPopoverTooltipHeader(self, value):
        self._setResource(4, value)

    def getPopoverTooltipBody(self):
        return self._getResource(5)

    def setPopoverTooltipBody(self, value):
        self._setResource(5, value)

    def getSearchString(self):
        return self._getString(6)

    def setSearchString(self, value):
        self._setString(6, value)

    def getSearchPlaceholder(self):
        return self._getResource(7)

    def setSearchPlaceholder(self, value):
        self._setResource(7, value)

    def getSearchTooltipHeader(self):
        return self._getResource(8)

    def setSearchTooltipHeader(self, value):
        self._setResource(8, value)

    def getSearchTooltipBody(self):
        return self._getString(9)

    def setSearchTooltipBody(self, value):
        self._setString(9, value)

    def getIsPopoverEnabled(self):
        return self._getBool(10)

    def setIsPopoverEnabled(self, value):
        self._setBool(10, value)

    def getIsPopoverHighlighted(self):
        return self._getBool(11)

    def setIsPopoverHighlighted(self, value):
        self._setBool(11, value)

    def getHasDiscountAlert(self):
        return self._getBool(12)

    def setHasDiscountAlert(self, value):
        self._setBool(12, value)

    def getHasAppliedFilters(self):
        return self._getBool(13)

    def setHasAppliedFilters(self, value):
        self._setBool(13, value)

    def getPanelType(self):
        return FilterPanelType(self._getString(14))

    def setPanelType(self, value):
        self._setString(14, value.value)

    def _initialize(self):
        super(FilterPanelWidgetModel, self)._initialize()
        self._addViewModelProperty('amountInfo', RangeModel())
        self._addViewModelProperty('filter', FilterToggleGroupModel())
        self._addBoolProperty('isSearchEnabled', False)
        self._addResourceProperty('title', R.invalid())
        self._addResourceProperty('popoverTooltipHeader', R.invalid())
        self._addResourceProperty('popoverTooltipBody', R.invalid())
        self._addStringProperty('searchString', '')
        self._addResourceProperty('searchPlaceholder', R.invalid())
        self._addResourceProperty('searchTooltipHeader', R.invalid())
        self._addStringProperty('searchTooltipBody', '')
        self._addBoolProperty('isPopoverEnabled', True)
        self._addBoolProperty('isPopoverHighlighted', False)
        self._addBoolProperty('hasDiscountAlert', False)
        self._addBoolProperty('hasAppliedFilters', False)
        self._addStringProperty('panelType')
        self.onSearch = self._addCommand('onSearch')
        self.onUpdateFilter = self._addCommand('onUpdateFilter')
        self.onResetFilter = self._addCommand('onResetFilter')
