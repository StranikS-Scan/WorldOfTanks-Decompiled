# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tooltips/racing_cup_tooltip_model.py
from frameworks.wulf import ViewModel

class RacingCupTooltipModel(ViewModel):
    __slots__ = ()

    def getCupType(self):
        return self._getString(0)

    def setCupType(self, value):
        self._setString(0, value)

    def getPricePoints(self):
        return self._getNumber(1)

    def setPricePoints(self, value):
        self._setNumber(1, value)

    def getCountCups(self):
        return self._getNumber(2)

    def setCountCups(self, value):
        self._setNumber(2, value)

    def getCupCondition(self):
        return self._getString(3)

    def setCupCondition(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(RacingCupTooltipModel, self)._initialize()
        self._addStringProperty('cupType', '')
        self._addNumberProperty('pricePoints', 0)
        self._addNumberProperty('countCups', 0)
        self._addStringProperty('cupCondition', '0')
