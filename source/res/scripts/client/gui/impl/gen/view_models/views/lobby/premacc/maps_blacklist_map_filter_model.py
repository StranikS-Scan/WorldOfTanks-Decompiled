# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/premacc/maps_blacklist_map_filter_model.py
from frameworks.wulf import ViewModel

class MapsBlacklistMapFilterModel(ViewModel):
    __slots__ = ()

    def getFilterName(self):
        return self._getString(0)

    def setFilterName(self, value):
        self._setString(0, value)

    def getFilterID(self):
        return self._getNumber(1)

    def setFilterID(self, value):
        self._setNumber(1, value)

    def getSelected(self):
        return self._getBool(2)

    def setSelected(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(MapsBlacklistMapFilterModel, self)._initialize()
        self._addStringProperty('filterName', '')
        self._addNumberProperty('filterID', -1)
        self._addBoolProperty('selected', False)
