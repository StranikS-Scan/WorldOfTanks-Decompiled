# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/excluded_maps/map_item_model.py
from frameworks.wulf import ViewModel

class MapItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(MapItemModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return self._getString(0)

    def setState(self, value):
        self._setString(0, value)

    def getMapId(self):
        return self._getString(1)

    def setMapId(self, value):
        self._setString(1, value)

    def getCooldownEndTime(self):
        return self._getNumber(2)

    def setCooldownEndTime(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(MapItemModel, self)._initialize()
        self._addStringProperty('state', '')
        self._addStringProperty('mapId', '')
        self._addNumberProperty('cooldownEndTime', 0)
