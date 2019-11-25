# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/premacc/piggybank_base_model.py
from frameworks.wulf import ViewModel

class PiggybankBaseModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(PiggybankBaseModel, self).__init__(properties=properties, commands=commands)

    def getMaxAmount(self):
        return self._getNumber(0)

    def setMaxAmount(self, value):
        self._setNumber(0, value)

    def getMaxAmountStr(self):
        return self._getString(1)

    def setMaxAmountStr(self, value):
        self._setString(1, value)

    def getCurrentAmount(self):
        return self._getNumber(2)

    def setCurrentAmount(self, value):
        self._setNumber(2, value)

    def getCurrentAmountStr(self):
        return self._getString(3)

    def setCurrentAmountStr(self, value):
        self._setString(3, value)

    def getIsTankPremiumActive(self):
        return self._getBool(4)

    def setIsTankPremiumActive(self, value):
        self._setBool(4, value)

    def getTimeleft(self):
        return self._getNumber(5)

    def setTimeleft(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(PiggybankBaseModel, self)._initialize()
        self._addNumberProperty('maxAmount', 1)
        self._addStringProperty('maxAmountStr', '0')
        self._addNumberProperty('currentAmount', 0)
        self._addStringProperty('currentAmountStr', '0')
        self._addBoolProperty('isTankPremiumActive', False)
        self._addNumberProperty('timeleft', 0)
