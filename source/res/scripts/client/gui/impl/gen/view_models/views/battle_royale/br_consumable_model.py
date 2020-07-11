# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle_royale/br_consumable_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class BrConsumableModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(BrConsumableModel, self).__init__(properties=properties, commands=commands)

    def getIconSource(self):
        return self._getResource(0)

    def setIconSource(self, value):
        self._setResource(0, value)

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
        super(BrConsumableModel, self)._initialize()
        self._addResourceProperty('iconSource', R.invalid())
        self._addNumberProperty('quantity', 0)
        self._addNumberProperty('intCD', 0)
        self._addStringProperty('tooltipType', '')
