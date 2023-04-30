# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/excluded_maps/excluded_maps_view_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.account_dashboard.map_model import MapModel
from gui.impl.gen.view_models.views.lobby.excluded_maps.filter_model import FilterModel
from gui.impl.gen.view_models.views.lobby.excluded_maps.map_item_model import MapItemModel

class MapStateEnum(Enum):
    AVAILABLE = 'Available'
    EXCLUDEDINCOOLDOWN = 'ExcludedInCooldown'
    EXCLUDEDREPLACEABLE = 'ExcludedReplaceable'
    DISABLED = 'Disabled'


class FilterNameEnum(Enum):
    SUMMER = 'summer'
    WINTER = 'winter'
    DESERT = 'desert'


class ExcludedMapsViewModel(ViewModel):
    __slots__ = ('onBackAction', 'onMapClick', 'onMapRemoveFromSlot', 'onFilterReset', 'onFilterClick')

    def __init__(self, properties=6, commands=5):
        super(ExcludedMapsViewModel, self).__init__(properties=properties, commands=commands)

    def getMapsSelected(self):
        return self._getNumber(0)

    def setMapsSelected(self, value):
        self._setNumber(0, value)

    def getMapsTotal(self):
        return self._getNumber(1)

    def setMapsTotal(self, value):
        self._setNumber(1, value)

    def getIsFilterApplied(self):
        return self._getBool(2)

    def setIsFilterApplied(self, value):
        self._setBool(2, value)

    def getExcludedMaps(self):
        return self._getArray(3)

    def setExcludedMaps(self, value):
        self._setArray(3, value)

    @staticmethod
    def getExcludedMapsType():
        return MapModel

    def getMapFilters(self):
        return self._getArray(4)

    def setMapFilters(self, value):
        self._setArray(4, value)

    @staticmethod
    def getMapFiltersType():
        return FilterModel

    def getMaps(self):
        return self._getArray(5)

    def setMaps(self, value):
        self._setArray(5, value)

    @staticmethod
    def getMapsType():
        return MapItemModel

    def _initialize(self):
        super(ExcludedMapsViewModel, self)._initialize()
        self._addNumberProperty('mapsSelected', 0)
        self._addNumberProperty('mapsTotal', 0)
        self._addBoolProperty('isFilterApplied', False)
        self._addArrayProperty('excludedMaps', Array())
        self._addArrayProperty('mapFilters', Array())
        self._addArrayProperty('maps', Array())
        self.onBackAction = self._addCommand('onBackAction')
        self.onMapClick = self._addCommand('onMapClick')
        self.onMapRemoveFromSlot = self._addCommand('onMapRemoveFromSlot')
        self.onFilterReset = self._addCommand('onFilterReset')
        self.onFilterClick = self._addCommand('onFilterClick')
