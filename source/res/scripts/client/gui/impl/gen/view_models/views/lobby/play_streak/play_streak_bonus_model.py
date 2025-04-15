# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/play_streak/play_streak_bonus_model.py
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class PlayStreakBonusModel(BonusModel):
    __slots__ = ()

    def __init__(self, properties=13, commands=0):
        super(PlayStreakBonusModel, self).__init__(properties=properties, commands=commands)

    def getVehCD(self):
        return self._getNumber(7)

    def setVehCD(self, value):
        self._setNumber(7, value)

    def getVehType(self):
        return self._getString(8)

    def setVehType(self, value):
        self._setString(8, value)

    def getLevel(self):
        return self._getNumber(9)

    def setLevel(self, value):
        self._setNumber(9, value)

    def getNation(self):
        return self._getString(10)

    def setNation(self, value):
        self._setString(10, value)

    def getVehName(self):
        return self._getString(11)

    def setVehName(self, value):
        self._setString(11, value)

    def getIsElite(self):
        return self._getBool(12)

    def setIsElite(self, value):
        self._setBool(12, value)

    def _initialize(self):
        super(PlayStreakBonusModel, self)._initialize()
        self._addNumberProperty('vehCD', 0)
        self._addStringProperty('vehType', '')
        self._addNumberProperty('level', 0)
        self._addStringProperty('nation', '')
        self._addStringProperty('vehName', '')
        self._addBoolProperty('isElite', False)
