# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle_royale/br_consum_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class BrConsumModel(ViewModel):
    __slots__ = ()

    def getIconSource(self):
        return self._getResource(0)

    def setIconSource(self, value):
        self._setResource(0, value)

    def getConsumValue(self):
        return self._getNumber(1)

    def setConsumValue(self, value):
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
        super(BrConsumModel, self)._initialize()
        self._addResourceProperty('iconSource', R.invalid())
        self._addNumberProperty('consumValue', 0)
        self._addNumberProperty('intCD', 0)
        self._addStringProperty('tooltipType', '')
