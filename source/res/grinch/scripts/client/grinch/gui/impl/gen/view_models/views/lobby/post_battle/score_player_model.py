# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/impl/gen/view_models/views/lobby/post_battle/score_player_model.py
from grinch.gui.impl.gen.view_models.views.battle.grinch_player_model import VehicleTypeEnum
from frameworks.wulf import ViewModel

class ScorePlayerModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(ScorePlayerModel, self).__init__(properties=properties, commands=commands)

    def getPlatoon(self):
        return self._getNumber(0)

    def setPlatoon(self, value):
        self._setNumber(0, value)

    def getVehicle(self):
        return VehicleTypeEnum(self._getString(1))

    def setVehicle(self, value):
        self._setString(1, value.value)

    def getName(self):
        return self._getString(2)

    def setName(self, value):
        self._setString(2, value)

    def getScore(self):
        return self._getNumber(3)

    def setScore(self, value):
        self._setNumber(3, value)

    def getIsCurrentPlayer(self):
        return self._getBool(4)

    def setIsCurrentPlayer(self, value):
        self._setBool(4, value)

    def getIsSelectedPlayer(self):
        return self._getBool(5)

    def setIsSelectedPlayer(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(ScorePlayerModel, self)._initialize()
        self._addNumberProperty('platoon', 0)
        self._addStringProperty('vehicle', VehicleTypeEnum.LIGHTTANK.value)
        self._addStringProperty('name', '')
        self._addNumberProperty('score', 0)
        self._addBoolProperty('isCurrentPlayer', False)
        self._addBoolProperty('isSelectedPlayer', False)
