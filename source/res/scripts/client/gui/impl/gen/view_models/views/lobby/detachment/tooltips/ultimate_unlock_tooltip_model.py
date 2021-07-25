# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/tooltips/ultimate_unlock_tooltip_model.py
from frameworks.wulf import ViewModel

class UltimateUnlockTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(UltimateUnlockTooltipModel, self).__init__(properties=properties, commands=commands)

    def getUltimateSelected(self):
        return self._getBool(0)

    def setUltimateSelected(self, value):
        self._setBool(0, value)

    def getCurrentPoints(self):
        return self._getNumber(1)

    def setCurrentPoints(self, value):
        self._setNumber(1, value)

    def getMaxPoints(self):
        return self._getNumber(2)

    def setMaxPoints(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(UltimateUnlockTooltipModel, self)._initialize()
        self._addBoolProperty('ultimateSelected', False)
        self._addNumberProperty('currentPoints', 0)
        self._addNumberProperty('maxPoints', 0)
