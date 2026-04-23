# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/customization/customization_marker_model.py
from enum import IntEnum
from gui.impl.gen.view_models.common.marker_model import MarkerModel

class AnchorStateEnum(IntEnum):
    UNSELECTEDEMPTY = 0
    SELECTEDEMPTY = 1
    UNSELECTEDFILLED = 2
    SELECTEDFILLED = 3
    PREVIEW = 4
    LOCKED = 5
    REMOVED = 6
    EDIT = 7


class CustomizationMarkerModel(MarkerModel):
    __slots__ = ()

    def __init__(self, properties=13, commands=0):
        super(CustomizationMarkerModel, self).__init__(properties=properties, commands=commands)

    def getAreaId(self):
        return self._getNumber(6)

    def setAreaId(self, value):
        self._setNumber(6, value)

    def getSlotType(self):
        return self._getNumber(7)

    def setSlotType(self, value):
        self._setNumber(7, value)

    def getRegionIdx(self):
        return self._getNumber(8)

    def setRegionIdx(self, value):
        self._setNumber(8, value)

    def getZIndex(self):
        return self._getNumber(9)

    def setZIndex(self, value):
        self._setNumber(9, value)

    def getIsHovered(self):
        return self._getBool(10)

    def setIsHovered(self, value):
        self._setBool(10, value)

    def getOpacity(self):
        return self._getReal(11)

    def setOpacity(self, value):
        self._setReal(11, value)

    def getState(self):
        return AnchorStateEnum(self._getNumber(12))

    def setState(self, value):
        self._setNumber(12, value.value)

    def _initialize(self):
        super(CustomizationMarkerModel, self)._initialize()
        self._addNumberProperty('areaId', 0)
        self._addNumberProperty('slotType', 0)
        self._addNumberProperty('regionIdx', 0)
        self._addNumberProperty('zIndex', 0)
        self._addBoolProperty('isHovered', False)
        self._addRealProperty('opacity', 1)
        self._addNumberProperty('state')
