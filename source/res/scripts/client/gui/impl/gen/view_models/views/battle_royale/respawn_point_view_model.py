# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle_royale/respawn_point_view_model.py
from frameworks.wulf import ViewModel

class RespawnPointViewModel(ViewModel):
    __slots__ = ()

    def getPointID(self):
        return self._getString(0)

    def setPointID(self, value):
        self._setString(0, value)

    def getCoordX(self):
        return self._getNumber(1)

    def setCoordX(self, value):
        self._setNumber(1, value)

    def getCoordY(self):
        return self._getNumber(2)

    def setCoordY(self, value):
        self._setNumber(2, value)

    def getPlayerName1(self):
        return self._getString(3)

    def setPlayerName1(self, value):
        self._setString(3, value)

    def getPlayerName2(self):
        return self._getString(4)

    def setPlayerName2(self, value):
        self._setString(4, value)

    def getSelected(self):
        return self._getBool(5)

    def setSelected(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(RespawnPointViewModel, self)._initialize()
        self._addStringProperty('pointID', '')
        self._addNumberProperty('coordX', 0)
        self._addNumberProperty('coordY', 0)
        self._addStringProperty('playerName1', '')
        self._addStringProperty('playerName2', '')
        self._addBoolProperty('selected', False)
