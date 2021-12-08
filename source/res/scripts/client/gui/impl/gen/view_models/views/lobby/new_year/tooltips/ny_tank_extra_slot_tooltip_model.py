# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_tank_extra_slot_tooltip_model.py
from frameworks.wulf import ViewModel

class NyTankExtraSlotTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(NyTankExtraSlotTooltipModel, self).__init__(properties=properties, commands=commands)

    def getXpFactor(self):
        return self._getNumber(0)

    def setXpFactor(self, value):
        self._setNumber(0, value)

    def getFreeXPFactor(self):
        return self._getNumber(1)

    def setFreeXPFactor(self, value):
        self._setNumber(1, value)

    def getTankmenXPFactor(self):
        return self._getNumber(2)

    def setTankmenXPFactor(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(NyTankExtraSlotTooltipModel, self)._initialize()
        self._addNumberProperty('xpFactor', 0)
        self._addNumberProperty('freeXPFactor', 0)
        self._addNumberProperty('tankmenXPFactor', 0)
