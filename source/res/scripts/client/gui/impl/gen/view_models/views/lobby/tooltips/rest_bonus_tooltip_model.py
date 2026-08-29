# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tooltips/rest_bonus_tooltip_model.py
from frameworks.wulf import ViewModel

class RestBonusTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(RestBonusTooltipModel, self).__init__(properties=properties, commands=commands)

    def getMultiplier(self):
        return self._getNumber(0)

    def setMultiplier(self, value):
        self._setNumber(0, value)

    def getResetTimestamp(self):
        return self._getNumber(1)

    def setResetTimestamp(self, value):
        self._setNumber(1, value)

    def getEndTimestamp(self):
        return self._getNumber(2)

    def setEndTimestamp(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(RestBonusTooltipModel, self)._initialize()
        self._addNumberProperty('multiplier', 0)
        self._addNumberProperty('resetTimestamp', 0)
        self._addNumberProperty('endTimestamp', 0)
