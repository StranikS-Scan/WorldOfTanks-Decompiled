# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: server_side_replay/scripts/client/server_side_replay/gui/impl/gen/view_models/views/lobby/replay_model.py
from enum import Enum
from frameworks.wulf import Array, ViewModel
from server_side_replay.gui.impl.gen.view_models.views.lobby.player_model import PlayerModel
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel

class MarksOfMastery(Enum):
    NONE = ''
    MASTER = 'master'
    FIRST = 'first'
    SECOND = 'second'
    THIRD = 'third'


class ReplayModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=13, commands=0):
        super(ReplayModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleInfo(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleInfoType():
        return VehicleModel

    @property
    def playerInfo(self):
        return self._getViewModel(1)

    @staticmethod
    def getPlayerInfoType():
        return PlayerModel

    def getId(self):
        return self._getString(2)

    def setId(self, value):
        self._setString(2, value)

    def getIsFavorite(self):
        return self._getBool(3)

    def setIsFavorite(self, value):
        self._setBool(3, value)

    def getArenaName(self):
        return self._getString(4)

    def setArenaName(self, value):
        self._setString(4, value)

    def getTimestamp(self):
        return self._getNumber(5)

    def setTimestamp(self, value):
        self._setNumber(5, value)

    def getEarnedXp(self):
        return self._getNumber(6)

    def setEarnedXp(self, value):
        self._setNumber(6, value)

    def getDamageDealt(self):
        return self._getNumber(7)

    def setDamageDealt(self, value):
        self._setNumber(7, value)

    def getDamageAssisted(self):
        return self._getNumber(8)

    def setDamageAssisted(self, value):
        self._setNumber(8, value)

    def getDamageBlockedByArmor(self):
        return self._getNumber(9)

    def setDamageBlockedByArmor(self, value):
        self._setNumber(9, value)

    def getKills(self):
        return self._getNumber(10)

    def setKills(self, value):
        self._setNumber(10, value)

    def getMarksOfMastery(self):
        return MarksOfMastery(self._getString(11))

    def setMarksOfMastery(self, value):
        self._setString(11, value.value)

    def getEpicMedals(self):
        return self._getArray(12)

    def setEpicMedals(self, value):
        self._setArray(12, value)

    @staticmethod
    def getEpicMedalsType():
        return unicode

    def _initialize(self):
        super(ReplayModel, self)._initialize()
        self._addViewModelProperty('vehicleInfo', VehicleModel())
        self._addViewModelProperty('playerInfo', PlayerModel())
        self._addStringProperty('id', '')
        self._addBoolProperty('isFavorite', False)
        self._addStringProperty('arenaName', '')
        self._addNumberProperty('timestamp', 0)
        self._addNumberProperty('earnedXp', 0)
        self._addNumberProperty('damageDealt', 0)
        self._addNumberProperty('damageAssisted', 0)
        self._addNumberProperty('damageBlockedByArmor', 0)
        self._addNumberProperty('kills', 0)
        self._addStringProperty('marksOfMastery', MarksOfMastery.NONE.value)
        self._addArrayProperty('epicMedals', Array())
