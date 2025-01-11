# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/challenge/quest_simplification_model.py
from frameworks.wulf import ViewModel

class QuestSimplificationModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(QuestSimplificationModel, self).__init__(properties=properties, commands=commands)

    def getIcon(self):
        return self._getString(0)

    def setIcon(self, value):
        self._setString(0, value)

    def getPrice(self):
        return self._getNumber(1)

    def setPrice(self, value):
        self._setNumber(1, value)

    def getLevel(self):
        return self._getNumber(2)

    def setLevel(self, value):
        self._setNumber(2, value)

    def getInsufficientFunds(self):
        return self._getBool(3)

    def setInsufficientFunds(self, value):
        self._setBool(3, value)

    def getGoalValue(self):
        return self._getNumber(4)

    def setGoalValue(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(QuestSimplificationModel, self)._initialize()
        self._addStringProperty('icon', '')
        self._addNumberProperty('price', 0)
        self._addNumberProperty('level', 0)
        self._addBoolProperty('insufficientFunds', False)
        self._addNumberProperty('goalValue', 0)
