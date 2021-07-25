# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/research/insufficient_credits_tooltip_model.py
from frameworks.wulf import ViewModel

class InsufficientCreditsTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(InsufficientCreditsTooltipModel, self).__init__(properties=properties, commands=commands)

    def getMissingAmount(self):
        return self._getNumber(0)

    def setMissingAmount(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(InsufficientCreditsTooltipModel, self)._initialize()
        self._addNumberProperty('missingAmount', 0)
