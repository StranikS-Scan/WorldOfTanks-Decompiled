# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/dog_tags/required_achievement.py
from frameworks.wulf import ViewModel

class RequiredAchievement(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(RequiredAchievement, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getType(self):
        return self._getString(1)

    def setType(self, value):
        self._setString(1, value)

    def getBackground(self):
        return self._getString(2)

    def setBackground(self, value):
        self._setString(2, value)

    def getProgress(self):
        return self._getNumber(3)

    def setProgress(self, value):
        self._setNumber(3, value)

    def getStage(self):
        return self._getNumber(4)

    def setStage(self, value):
        self._setNumber(4, value)

    def getIsTrophy(self):
        return self._getBool(5)

    def setIsTrophy(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(RequiredAchievement, self)._initialize()
        self._addStringProperty('name', '')
        self._addStringProperty('type', '')
        self._addStringProperty('background', '')
        self._addNumberProperty('progress', 0)
        self._addNumberProperty('stage', 0)
        self._addBoolProperty('isTrophy', False)
