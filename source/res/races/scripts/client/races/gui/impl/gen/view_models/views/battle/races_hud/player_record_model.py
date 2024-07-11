# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/impl/gen/view_models/views/battle/races_hud/player_record_model.py
from frameworks.wulf import ViewModel

class PlayerRecordModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(PlayerRecordModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getClanAbbrev(self):
        return self._getString(1)

    def setClanAbbrev(self, value):
        self._setString(1, value)

    def getVehicleGuiName(self):
        return self._getString(2)

    def setVehicleGuiName(self, value):
        self._setString(2, value)

    def getIsReady(self):
        return self._getBool(3)

    def setIsReady(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(PlayerRecordModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addStringProperty('clanAbbrev', '')
        self._addStringProperty('vehicleGuiName', '')
        self._addBoolProperty('isReady', False)
