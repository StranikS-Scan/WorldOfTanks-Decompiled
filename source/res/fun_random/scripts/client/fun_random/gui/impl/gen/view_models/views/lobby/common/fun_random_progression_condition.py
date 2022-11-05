# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/gen/view_models/views/lobby/common/fun_random_progression_condition.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class FunRandomProgressionCondition(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(FunRandomProgressionCondition, self).__init__(properties=properties, commands=commands)

    def getCurrentPoints(self):
        return self._getNumber(0)

    def setCurrentPoints(self, value):
        self._setNumber(0, value)

    def getMaximumPoints(self):
        return self._getNumber(1)

    def setMaximumPoints(self, value):
        self._setNumber(1, value)

    def getText(self):
        return self._getString(2)

    def setText(self, value):
        self._setString(2, value)

    def getConditions(self):
        return self._getArray(3)

    def setConditions(self, value):
        self._setArray(3, value)

    @staticmethod
    def getConditionsType():
        return str

    def _initialize(self):
        super(FunRandomProgressionCondition, self)._initialize()
        self._addNumberProperty('currentPoints', -1)
        self._addNumberProperty('maximumPoints', -1)
        self._addStringProperty('text', '')
        self._addArrayProperty('conditions', Array())
