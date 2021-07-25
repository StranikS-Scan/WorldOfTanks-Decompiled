# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/tooltips/discount_tooltip_model.py
from frameworks.wulf import ViewModel

class DiscountTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(DiscountTooltipModel, self).__init__(properties=properties, commands=commands)

    def getCurrentValue(self):
        return self._getNumber(0)

    def setCurrentValue(self, value):
        self._setNumber(0, value)

    def getIsCurrentEnough(self):
        return self._getBool(1)

    def setIsCurrentEnough(self, value):
        self._setBool(1, value)

    def getType(self):
        return self._getString(2)

    def setType(self, value):
        self._setString(2, value)

    def getDefaultValue(self):
        return self._getNumber(3)

    def setDefaultValue(self, value):
        self._setNumber(3, value)

    def getIsDefaultEnough(self):
        return self._getBool(4)

    def setIsDefaultEnough(self, value):
        self._setBool(4, value)

    def getInfo(self):
        return self._getString(5)

    def setInfo(self, value):
        self._setString(5, value)

    def _initialize(self):
        super(DiscountTooltipModel, self)._initialize()
        self._addNumberProperty('currentValue', 0)
        self._addBoolProperty('isCurrentEnough', False)
        self._addStringProperty('type', '')
        self._addNumberProperty('defaultValue', 0)
        self._addBoolProperty('isDefaultEnough', False)
        self._addStringProperty('info', '')
