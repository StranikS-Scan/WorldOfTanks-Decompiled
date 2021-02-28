# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/game_mode_card_rows_model.py
from frameworks.wulf import ViewModel

class GameModeCardRowsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(GameModeCardRowsModel, self).__init__(properties=properties, commands=commands)

    def getLevelIcon(self):
        return self._getString(0)

    def setLevelIcon(self, value):
        self._setString(0, value)

    def getVehicleTypeIcon(self):
        return self._getString(1)

    def setVehicleTypeIcon(self, value):
        self._setString(1, value)

    def getVehicleName(self):
        return self._getString(2)

    def setVehicleName(self, value):
        self._setString(2, value)

    def getPoints(self):
        return self._getNumber(3)

    def setPoints(self, value):
        self._setNumber(3, value)

    def getTextStart(self):
        return self._getString(4)

    def setTextStart(self, value):
        self._setString(4, value)

    def getTextHighlight(self):
        return self._getString(5)

    def setTextHighlight(self, value):
        self._setString(5, value)

    def getTextEnd(self):
        return self._getString(6)

    def setTextEnd(self, value):
        self._setString(6, value)

    def _initialize(self):
        super(GameModeCardRowsModel, self)._initialize()
        self._addStringProperty('levelIcon', '')
        self._addStringProperty('vehicleTypeIcon', '')
        self._addStringProperty('vehicleName', '')
        self._addNumberProperty('points', 0)
        self._addStringProperty('textStart', '')
        self._addStringProperty('textHighlight', '')
        self._addStringProperty('textEnd', '')
