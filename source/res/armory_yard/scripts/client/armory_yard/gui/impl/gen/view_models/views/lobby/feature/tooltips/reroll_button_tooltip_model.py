# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/gen/view_models/views/lobby/feature/tooltips/reroll_button_tooltip_model.py
from frameworks.wulf import ViewModel

class RerollButtonTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(RerollButtonTooltipModel, self).__init__(properties=properties, commands=commands)

    def getFreeRerollCount(self):
        return self._getNumber(0)

    def setFreeRerollCount(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(RerollButtonTooltipModel, self)._initialize()
        self._addNumberProperty('freeRerollCount', 0)
