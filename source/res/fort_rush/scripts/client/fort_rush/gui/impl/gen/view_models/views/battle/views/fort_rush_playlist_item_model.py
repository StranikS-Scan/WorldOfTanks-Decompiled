# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/gen/view_models/views/battle/views/fort_rush_playlist_item_model.py
from frameworks.wulf import Array, ViewModel

class FortRushPlaylistItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(FortRushPlaylistItemModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getString(0)

    def setId(self, value):
        self._setString(0, value)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getVehicleIds(self):
        return self._getArray(2)

    def setVehicleIds(self, value):
        self._setArray(2, value)

    @staticmethod
    def getVehicleIdsType():
        return int

    def getTipSize(self):
        return self._getString(3)

    def setTipSize(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(FortRushPlaylistItemModel, self)._initialize()
        self._addStringProperty('id', '')
        self._addStringProperty('name', '')
        self._addArrayProperty('vehicleIds', Array())
        self._addStringProperty('tipSize', '')
