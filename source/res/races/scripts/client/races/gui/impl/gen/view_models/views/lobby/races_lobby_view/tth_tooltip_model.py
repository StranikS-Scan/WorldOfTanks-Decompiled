# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/impl/gen/view_models/views/lobby/races_lobby_view/tth_tooltip_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel

class Property(IntEnum):
    MAXSPEED = 0
    RELOADTIME = 1
    ACCELERATION = 2
    STABILITY = 3
    CONTROLLABILITY = 4


class TthTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(TthTooltipModel, self).__init__(properties=properties, commands=commands)

    def getValue(self):
        return self._getString(0)

    def setValue(self, value):
        self._setString(0, value)

    def getProperty(self):
        return self._getNumber(1)

    def setProperty(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(TthTooltipModel, self)._initialize()
        self._addStringProperty('value', '')
        self._addNumberProperty('property', 0)
