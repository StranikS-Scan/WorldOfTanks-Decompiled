# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/premacc/maps_blacklist_slot_model.py
from frameworks.wulf import ViewModel

class MapsBlacklistSlotModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(MapsBlacklistSlotModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return self._getString(0)

    def setState(self, value):
        self._setString(0, value)

    def getMapId(self):
        return self._getString(1)

    def setMapId(self, value):
        self._setString(1, value)

    def getSeasonId(self):
        return self._getNumber(2)

    def setSeasonId(self, value):
        self._setNumber(2, value)

    def getCooldownTime(self):
        return self._getNumber(3)

    def setCooldownTime(self, value):
        self._setNumber(3, value)

    def getFiltered(self):
        return self._getBool(4)

    def setFiltered(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(MapsBlacklistSlotModel, self)._initialize()
        self._addStringProperty('state', '')
        self._addStringProperty('mapId', '')
        self._addNumberProperty('seasonId', 0)
        self._addNumberProperty('cooldownTime', 0)
        self._addBoolProperty('filtered', True)
