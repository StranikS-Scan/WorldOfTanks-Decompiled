# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/gen/view_models/views/lobby/tooltips/description_rules_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class DescriptionRulesTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(DescriptionRulesTooltipModel, self).__init__(properties=properties, commands=commands)

    def getMinLevel(self):
        return self._getNumber(0)

    def setMinLevel(self, value):
        self._setNumber(0, value)

    def getMaxLevel(self):
        return self._getNumber(1)

    def setMaxLevel(self, value):
        self._setNumber(1, value)

    def getBattleTypes(self):
        return self._getArray(2)

    def setBattleTypes(self, value):
        self._setArray(2, value)

    @staticmethod
    def getBattleTypesType():
        return int

    def _initialize(self):
        super(DescriptionRulesTooltipModel, self)._initialize()
        self._addNumberProperty('minLevel', 0)
        self._addNumberProperty('maxLevel', 0)
        self._addArrayProperty('battleTypes', Array())
