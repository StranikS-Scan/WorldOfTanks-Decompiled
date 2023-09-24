# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/personal_case/achievement_model.py
from frameworks.wulf import ViewModel

class AchievementModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(AchievementModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getAmount(self):
        return self._getNumber(1)

    def setAmount(self, value):
        self._setNumber(1, value)

    def getBlock(self):
        return self._getString(2)

    def setBlock(self, value):
        self._setString(2, value)

    def getIsRare(self):
        return self._getBool(3)

    def setIsRare(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(AchievementModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addNumberProperty('amount', 0)
        self._addStringProperty('block', '')
        self._addBoolProperty('isRare', False)
