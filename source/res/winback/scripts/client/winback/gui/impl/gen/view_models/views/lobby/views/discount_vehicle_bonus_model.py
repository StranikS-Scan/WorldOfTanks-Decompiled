# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: winback/scripts/client/winback/gui/impl/gen/view_models/views/lobby/views/discount_vehicle_bonus_model.py
from winback.gui.impl.gen.view_models.views.lobby.views.vehicle_bonus_model import VehicleBonusModel

class DiscountVehicleBonusModel(VehicleBonusModel):
    __slots__ = ()

    def __init__(self, properties=22, commands=0):
        super(DiscountVehicleBonusModel, self).__init__(properties=properties, commands=commands)

    def getOldPrice(self):
        return self._getNumber(17)

    def setOldPrice(self, value):
        self._setNumber(17, value)

    def getNewPrice(self):
        return self._getNumber(18)

    def setNewPrice(self, value):
        self._setNumber(18, value)

    def getOldExp(self):
        return self._getNumber(19)

    def setOldExp(self, value):
        self._setNumber(19, value)

    def getNewExp(self):
        return self._getNumber(20)

    def setNewExp(self, value):
        self._setNumber(20, value)

    def getIsSelected(self):
        return self._getBool(21)

    def setIsSelected(self, value):
        self._setBool(21, value)

    def _initialize(self):
        super(DiscountVehicleBonusModel, self)._initialize()
        self._addNumberProperty('oldPrice', 0)
        self._addNumberProperty('newPrice', 0)
        self._addNumberProperty('oldExp', 0)
        self._addNumberProperty('newExp', 0)
        self._addBoolProperty('isSelected', False)
