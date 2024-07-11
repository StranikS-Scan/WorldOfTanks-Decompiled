# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/impl/gen/view_models/views/lobby/player_information.py
from frameworks.wulf import ViewModel
from races.gui.impl.gen.view_models.views.lobby.battle_result import BattleResult

class PlayerInformation(ViewModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(PlayerInformation, self).__init__(properties=properties, commands=commands)

    @property
    def battleResultPoints(self):
        return self._getViewModel(0)

    @staticmethod
    def getBattleResultPointsType():
        return BattleResult

    def getPlayerId(self):
        return self._getNumber(1)

    def setPlayerId(self, value):
        self._setNumber(1, value)

    def getPlayerNickname(self):
        return self._getString(2)

    def setPlayerNickname(self, value):
        self._setString(2, value)

    def getIsFinishFail(self):
        return self._getBool(3)

    def setIsFinishFail(self, value):
        self._setBool(3, value)

    def getIsDisqualification(self):
        return self._getBool(4)

    def setIsDisqualification(self, value):
        self._setBool(4, value)

    def getPlace(self):
        return self._getNumber(5)

    def setPlace(self, value):
        self._setNumber(5, value)

    def getRaceDuration(self):
        return self._getNumber(6)

    def setRaceDuration(self, value):
        self._setNumber(6, value)

    def getPoints(self):
        return self._getNumber(7)

    def setPoints(self, value):
        self._setNumber(7, value)

    def getVehicleName(self):
        return self._getString(8)

    def setVehicleName(self, value):
        self._setString(8, value)

    def getVehicleIconName(self):
        return self._getString(9)

    def setVehicleIconName(self, value):
        self._setString(9, value)

    def _initialize(self):
        super(PlayerInformation, self)._initialize()
        self._addViewModelProperty('battleResultPoints', BattleResult())
        self._addNumberProperty('playerId', 0)
        self._addStringProperty('playerNickname', '')
        self._addBoolProperty('isFinishFail', False)
        self._addBoolProperty('isDisqualification', False)
        self._addNumberProperty('place', 1)
        self._addNumberProperty('raceDuration', 0)
        self._addNumberProperty('points', 0)
        self._addStringProperty('vehicleName', '')
        self._addStringProperty('vehicleIconName', '')
