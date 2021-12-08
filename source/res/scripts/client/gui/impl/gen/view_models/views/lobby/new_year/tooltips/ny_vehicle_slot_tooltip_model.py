# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_vehicle_slot_tooltip_model.py
from frameworks.wulf import ViewModel

class NyVehicleSlotTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(NyVehicleSlotTooltipModel, self).__init__(properties=properties, commands=commands)

    def getIsExtraSlot(self):
        return self._getBool(0)

    def setIsExtraSlot(self, value):
        self._setBool(0, value)

    def getXpFactor(self):
        return self._getNumber(1)

    def setXpFactor(self, value):
        self._setNumber(1, value)

    def getFreeXPFactor(self):
        return self._getNumber(2)

    def setFreeXPFactor(self, value):
        self._setNumber(2, value)

    def getTankmenXPFactor(self):
        return self._getNumber(3)

    def setTankmenXPFactor(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(NyVehicleSlotTooltipModel, self)._initialize()
        self._addBoolProperty('isExtraSlot', False)
        self._addNumberProperty('xpFactor', 0)
        self._addNumberProperty('freeXPFactor', 0)
        self._addNumberProperty('tankmenXPFactor', 0)
