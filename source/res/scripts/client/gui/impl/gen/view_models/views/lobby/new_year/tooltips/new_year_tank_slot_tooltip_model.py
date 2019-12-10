# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/new_year_tank_slot_tooltip_model.py
from frameworks.wulf import ViewModel

class NewYearTankSlotTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(NewYearTankSlotTooltipModel, self).__init__(properties=properties, commands=commands)

    def getLevel(self):
        return self._getNumber(0)

    def setLevel(self, value):
        self._setNumber(0, value)

    def getLevelName(self):
        return self._getString(1)

    def setLevelName(self, value):
        self._setString(1, value)

    def getXpFactor(self):
        return self._getNumber(2)

    def setXpFactor(self, value):
        self._setNumber(2, value)

    def getFreeXPFactor(self):
        return self._getNumber(3)

    def setFreeXPFactor(self, value):
        self._setNumber(3, value)

    def getTankmenXPFactor(self):
        return self._getNumber(4)

    def setTankmenXPFactor(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(NewYearTankSlotTooltipModel, self)._initialize()
        self._addNumberProperty('level', 0)
        self._addStringProperty('levelName', '')
        self._addNumberProperty('xpFactor', 0)
        self._addNumberProperty('freeXPFactor', 0)
        self._addNumberProperty('tankmenXPFactor', 0)
