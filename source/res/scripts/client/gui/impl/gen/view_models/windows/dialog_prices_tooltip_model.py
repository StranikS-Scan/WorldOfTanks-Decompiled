# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/windows/dialog_prices_tooltip_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class DialogPricesTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(DialogPricesTooltipModel, self).__init__(properties=properties, commands=commands)

    def getValueMainCost(self):
        return self._getString(0)

    def setValueMainCost(self, value):
        self._setString(0, value)

    def getIconMainCost(self):
        return self._getResource(1)

    def setIconMainCost(self, value):
        self._setResource(1, value)

    def getLabelMainCost(self):
        return self._getResource(2)

    def setLabelMainCost(self, value):
        self._setResource(2, value)

    def getValueAdditionalCost(self):
        return self._getString(3)

    def setValueAdditionalCost(self, value):
        self._setString(3, value)

    def getIconAdditionalCost(self):
        return self._getResource(4)

    def setIconAdditionalCost(self, value):
        self._setResource(4, value)

    def getLabelAdditionalCost(self):
        return self._getResource(5)

    def setLabelAdditionalCost(self, value):
        self._setResource(5, value)

    def getTotalCost(self):
        return self._getString(6)

    def setTotalCost(self, value):
        self._setString(6, value)

    def getLabelTotalCost(self):
        return self._getResource(7)

    def setLabelTotalCost(self, value):
        self._setResource(7, value)

    def _initialize(self):
        super(DialogPricesTooltipModel, self)._initialize()
        self._addStringProperty('valueMainCost', '0')
        self._addResourceProperty('iconMainCost', R.invalid())
        self._addResourceProperty('labelMainCost', R.invalid())
        self._addStringProperty('valueAdditionalCost', '0')
        self._addResourceProperty('iconAdditionalCost', R.invalid())
        self._addResourceProperty('labelAdditionalCost', R.invalid())
        self._addStringProperty('totalCost', '0')
        self._addResourceProperty('labelTotalCost', R.invalid())
