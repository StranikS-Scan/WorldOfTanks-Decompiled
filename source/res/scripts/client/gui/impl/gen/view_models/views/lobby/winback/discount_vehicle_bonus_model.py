# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/winback/discount_vehicle_bonus_model.py
from gui.impl.gen.view_models.views.lobby.winback.vehicle_bonus_model import VehicleBonusModel

class DiscountVehicleBonusModel(VehicleBonusModel):
    __slots__ = ()

    def __init__(self, properties=23, commands=0):
        super(DiscountVehicleBonusModel, self).__init__(properties=properties, commands=commands)

    def getOldPrice(self):
        return self._getNumber(18)

    def setOldPrice(self, value):
        self._setNumber(18, value)

    def getNewPrice(self):
        return self._getNumber(19)

    def setNewPrice(self, value):
        self._setNumber(19, value)

    def getOldExp(self):
        return self._getNumber(20)

    def setOldExp(self, value):
        self._setNumber(20, value)

    def getNewExp(self):
        return self._getNumber(21)

    def setNewExp(self, value):
        self._setNumber(21, value)

    def getIsSelected(self):
        return self._getBool(22)

    def setIsSelected(self, value):
        self._setBool(22, value)

    def _initialize(self):
        super(DiscountVehicleBonusModel, self)._initialize()
        self._addNumberProperty('oldPrice', 0)
        self._addNumberProperty('newPrice', 0)
        self._addNumberProperty('oldExp', 0)
        self._addNumberProperty('newExp', 0)
        self._addBoolProperty('isSelected', False)
