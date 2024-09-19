# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/postbattle/general_info_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class GeneralInfoModel(ViewModel):
    __slots__ = ()
    WIN_STATUS_TIE = 0
    WIN_STATUS_WIN = 1
    WIN_STATUS_LOSE = 2

    def __init__(self, properties=10, commands=0):
        super(GeneralInfoModel, self).__init__(properties=properties, commands=commands)

    def getWinStatus(self):
        return self._getNumber(0)

    def setWinStatus(self, value):
        self._setNumber(0, value)

    def getBattleType(self):
        return self._getResource(1)

    def setBattleType(self, value):
        self._setResource(1, value)

    def getVehicleIconName(self):
        return self._getString(2)

    def setVehicleIconName(self, value):
        self._setString(2, value)

    def getVehicleLevel(self):
        return self._getNumber(3)

    def setVehicleLevel(self, value):
        self._setNumber(3, value)

    def getArenaName(self):
        return self._getString(4)

    def setArenaName(self, value):
        self._setString(4, value)

    def getBattleFinishTime(self):
        return self._getNumber(5)

    def setBattleFinishTime(self, value):
        self._setNumber(5, value)

    def getBattleFinishReason(self):
        return self._getNumber(6)

    def setBattleFinishReason(self, value):
        self._setNumber(6, value)

    def getServerTime(self):
        return self._getNumber(7)

    def setServerTime(self, value):
        self._setNumber(7, value)

    def getVehicleType(self):
        return self._getString(8)

    def setVehicleType(self, value):
        self._setString(8, value)

    def getLocalizedVehicleName(self):
        return self._getString(9)

    def setLocalizedVehicleName(self, value):
        self._setString(9, value)

    def _initialize(self):
        super(GeneralInfoModel, self)._initialize()
        self._addNumberProperty('winStatus', 0)
        self._addResourceProperty('battleType', R.invalid())
        self._addStringProperty('vehicleIconName', '')
        self._addNumberProperty('vehicleLevel', 0)
        self._addStringProperty('arenaName', '')
        self._addNumberProperty('battleFinishTime', 0)
        self._addNumberProperty('battleFinishReason', 0)
        self._addNumberProperty('serverTime', 0)
        self._addStringProperty('vehicleType', '')
        self._addStringProperty('localizedVehicleName', '')
