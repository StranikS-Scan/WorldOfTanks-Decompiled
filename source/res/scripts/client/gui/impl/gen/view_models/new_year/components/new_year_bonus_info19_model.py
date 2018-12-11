# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/new_year/components/new_year_bonus_info19_model.py
from frameworks.wulf import Resource
from frameworks.wulf import ViewModel

class NewYearBonusInfo19Model(ViewModel):
    __slots__ = ()

    def getTypeCollection(self):
        return self._getResource(0)

    def setTypeCollection(self, value):
        self._setResource(0, value)

    def getBonusDesc(self):
        return self._getResource(1)

    def setBonusDesc(self, value):
        self._setResource(1, value)

    def getCurrentValue(self):
        return self._getNumber(2)

    def setCurrentValue(self, value):
        self._setNumber(2, value)

    def getTotalValue(self):
        return self._getNumber(3)

    def setTotalValue(self, value):
        self._setNumber(3, value)

    def getBonusPercent(self):
        return self._getNumber(4)

    def setBonusPercent(self, value):
        self._setNumber(4, value)

    def getBonusIcon(self):
        return self._getResource(5)

    def setBonusIcon(self, value):
        self._setResource(5, value)

    def _initialize(self):
        super(NewYearBonusInfo19Model, self)._initialize()
        self._addResourceProperty('typeCollection', Resource.INVALID)
        self._addResourceProperty('bonusDesc', Resource.INVALID)
        self._addNumberProperty('currentValue', 0)
        self._addNumberProperty('totalValue', 0)
        self._addNumberProperty('bonusPercent', 0)
        self._addResourceProperty('bonusIcon', Resource.INVALID)
