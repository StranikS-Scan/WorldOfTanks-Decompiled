# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/halloween/tooltips/nitro_tooltip_model.py
from frameworks.wulf import ViewModel

class NitroTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(NitroTooltipModel, self).__init__(properties=properties, commands=commands)

    def getTimeRecharge(self):
        return self._getNumber(0)

    def setTimeRecharge(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(NitroTooltipModel, self)._initialize()
        self._addNumberProperty('timeRecharge', 0)
