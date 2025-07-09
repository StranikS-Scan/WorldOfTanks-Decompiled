# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/gen/view_models/views/lobby/tooltips/economy_bonus_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class EconomyBonusTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(EconomyBonusTooltipModel, self).__init__(properties=properties, commands=commands)

    def getPercent(self):
        return self._getNumber(0)

    def setPercent(self, value):
        self._setNumber(0, value)

    def getModes(self):
        return self._getArray(1)

    def setModes(self, value):
        self._setArray(1, value)

    @staticmethod
    def getModesType():
        return int

    def _initialize(self):
        super(EconomyBonusTooltipModel, self)._initialize()
        self._addNumberProperty('percent', 0)
        self._addArrayProperty('modes', Array())
