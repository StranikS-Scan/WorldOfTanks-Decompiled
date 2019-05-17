# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/premacc/maps_blacklist_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.ui_kit.list_model import ListModel

class MapsBlacklistViewModel(ViewModel):
    __slots__ = ('onBackAction', 'onCloseEvent', 'onMapAddToBlacklistEvent', 'onMapRemoveFromBlacklistEvent', 'onFilterReset', 'onInitialized')

    @property
    def disabledMaps(self):
        return self._getViewModel(0)

    @property
    def mapsFilters(self):
        return self._getViewModel(1)

    @property
    def maps(self):
        return self._getViewModel(2)

    def getCooldownTime(self):
        return self._getNumber(3)

    def setCooldownTime(self, value):
        self._setNumber(3, value)

    def getMapsSelected(self):
        return self._getNumber(4)

    def setMapsSelected(self, value):
        self._setNumber(4, value)

    def getMapsTotal(self):
        return self._getNumber(5)

    def setMapsTotal(self, value):
        self._setNumber(5, value)

    def getIsFilterApplied(self):
        return self._getBool(6)

    def setIsFilterApplied(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(MapsBlacklistViewModel, self)._initialize()
        self._addViewModelProperty('disabledMaps', ListModel())
        self._addViewModelProperty('mapsFilters', ListModel())
        self._addViewModelProperty('maps', ListModel())
        self._addNumberProperty('cooldownTime', 0)
        self._addNumberProperty('mapsSelected', 0)
        self._addNumberProperty('mapsTotal', 0)
        self._addBoolProperty('isFilterApplied', False)
        self.onBackAction = self._addCommand('onBackAction')
        self.onCloseEvent = self._addCommand('onCloseEvent')
        self.onMapAddToBlacklistEvent = self._addCommand('onMapAddToBlacklistEvent')
        self.onMapRemoveFromBlacklistEvent = self._addCommand('onMapRemoveFromBlacklistEvent')
        self.onFilterReset = self._addCommand('onFilterReset')
        self.onInitialized = self._addCommand('onInitialized')
