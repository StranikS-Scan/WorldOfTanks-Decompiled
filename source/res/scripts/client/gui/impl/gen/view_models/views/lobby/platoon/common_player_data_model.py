# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/platoon/common_player_data_model.py
from frameworks.wulf import ViewModel

class CommonPlayerDataModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(CommonPlayerDataModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getClanTag(self):
        return self._getString(1)

    def setClanTag(self, value):
        self._setString(1, value)

    def getBadgeID(self):
        return self._getString(2)

    def setBadgeID(self, value):
        self._setString(2, value)

    def getRating(self):
        return self._getString(3)

    def setRating(self, value):
        self._setString(3, value)

    def getColor(self):
        return self._getString(4)

    def setColor(self, value):
        self._setString(4, value)

    def getMaxDifficultyLevelMessage(self):
        return self._getString(5)

    def setMaxDifficultyLevelMessage(self, value):
        self._setString(5, value)

    def getMaxDifficultyLevel(self):
        return self._getNumber(6)

    def setMaxDifficultyLevel(self, value):
        self._setNumber(6, value)

    def getSquadDifficultyLevel(self):
        return self._getNumber(7)

    def setSquadDifficultyLevel(self, value):
        self._setNumber(7, value)

    def getIsEvent(self):
        return self._getBool(8)

    def setIsEvent(self, value):
        self._setBool(8, value)

    def _initialize(self):
        super(CommonPlayerDataModel, self)._initialize()
        self._addStringProperty('name', 'rookie')
        self._addStringProperty('clanTag', '')
        self._addStringProperty('badgeID', '')
        self._addStringProperty('rating', '')
        self._addStringProperty('color', '')
        self._addStringProperty('maxDifficultyLevelMessage', '')
        self._addNumberProperty('maxDifficultyLevel', 0)
        self._addNumberProperty('squadDifficultyLevel', 0)
        self._addBoolProperty('isEvent', False)
