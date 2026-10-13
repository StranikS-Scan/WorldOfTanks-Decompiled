# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle/shared/crosshair_state_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel

class CrosshairType(IntEnum):
    UNDEFINED = 0
    ARCADE = 1
    SNIPER = 2
    STRATEGIC = 3
    POSTMORTEM = 4


class CrosshairStateModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(CrosshairStateModel, self).__init__(properties=properties, commands=commands)

    def getCrosshairType(self):
        return CrosshairType(self._getNumber(0))

    def setCrosshairType(self, value):
        self._setNumber(0, value.value)

    def getZoomFactor(self):
        return self._getNumber(1)

    def setZoomFactor(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(CrosshairStateModel, self)._initialize()
        self._addNumberProperty('crosshairType')
        self._addNumberProperty('zoomFactor', 1)
