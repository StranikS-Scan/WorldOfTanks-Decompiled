# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/tooltips/dismiss_tooltip_model.py
from frameworks.wulf import ViewModel

class DismissTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(DismissTooltipModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return self._getString(0)

    def setState(self, value):
        self._setString(0, value)

    def getSellLimit(self):
        return self._getNumber(1)

    def setSellLimit(self, value):
        self._setNumber(1, value)

    def getCurSellCount(self):
        return self._getNumber(2)

    def setCurSellCount(self, value):
        self._setNumber(2, value)

    def getDetLevel(self):
        return self._getNumber(3)

    def setDetLevel(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(DismissTooltipModel, self)._initialize()
        self._addStringProperty('state', '')
        self._addNumberProperty('sellLimit', 0)
        self._addNumberProperty('curSellCount', 0)
        self._addNumberProperty('detLevel', 0)
