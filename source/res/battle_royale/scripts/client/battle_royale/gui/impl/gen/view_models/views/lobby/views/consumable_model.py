# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/gen/view_models/views/lobby/views/consumable_model.py
from frameworks.wulf import ViewModel

class ConsumableModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(ConsumableModel, self).__init__(properties=properties, commands=commands)

    def getIconName(self):
        return self._getString(0)

    def setIconName(self, value):
        self._setString(0, value)

    def getQuantity(self):
        return self._getNumber(1)

    def setQuantity(self, value):
        self._setNumber(1, value)

    def getIntCD(self):
        return self._getNumber(2)

    def setIntCD(self, value):
        self._setNumber(2, value)

    def getTooltipType(self):
        return self._getString(3)

    def setTooltipType(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(ConsumableModel, self)._initialize()
        self._addStringProperty('iconName', '')
        self._addNumberProperty('quantity', 0)
        self._addNumberProperty('intCD', 0)
        self._addStringProperty('tooltipType', '')
