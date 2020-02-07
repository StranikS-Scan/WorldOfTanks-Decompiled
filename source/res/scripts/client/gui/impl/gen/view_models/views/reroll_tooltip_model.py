# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/reroll_tooltip_model.py
from frameworks.wulf import ViewModel

class RerollTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(RerollTooltipModel, self).__init__(properties=properties, commands=commands)

    def getTimeLeft(self):
        return self._getNumber(0)

    def setTimeLeft(self, value):
        self._setNumber(0, value)

    def getRerollInterval(self):
        return self._getNumber(1)

    def setRerollInterval(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(RerollTooltipModel, self)._initialize()
        self._addNumberProperty('timeLeft', 0)
        self._addNumberProperty('rerollInterval', 0)
