# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/tooltips/experience_overflow_tooltip_model.py
from frameworks.wulf import ViewModel

class ExperienceOverflowTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(ExperienceOverflowTooltipModel, self).__init__(properties=properties, commands=commands)

    def getUsedExp(self):
        return self._getNumber(0)

    def setUsedExp(self, value):
        self._setNumber(0, value)

    def getLostExp(self):
        return self._getNumber(1)

    def setLostExp(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(ExperienceOverflowTooltipModel, self)._initialize()
        self._addNumberProperty('usedExp', 0)
        self._addNumberProperty('lostExp', 0)
