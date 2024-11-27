# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/vehicle_selection_models/discount_vehicle_bonus_model.py
from new_year.gui.impl.gen.view_models.views.lobby.new_year.vehicle_selection_models.vehicle_bonus_model import VehicleBonusModel

class DiscountVehicleBonusModel(VehicleBonusModel):
    __slots__ = ()

    def __init__(self, properties=21, commands=0):
        super(DiscountVehicleBonusModel, self).__init__(properties=properties, commands=commands)

    def getOldPrice(self):
        return self._getNumber(16)

    def setOldPrice(self, value):
        self._setNumber(16, value)

    def getNewPrice(self):
        return self._getNumber(17)

    def setNewPrice(self, value):
        self._setNumber(17, value)

    def getRewardIndex(self):
        return self._getNumber(18)

    def setRewardIndex(self, value):
        self._setNumber(18, value)

    def getIsSelected(self):
        return self._getBool(19)

    def setIsSelected(self, value):
        self._setBool(19, value)

    def getIntCD(self):
        return self._getNumber(20)

    def setIntCD(self, value):
        self._setNumber(20, value)

    def _initialize(self):
        super(DiscountVehicleBonusModel, self)._initialize()
        self._addNumberProperty('oldPrice', 0)
        self._addNumberProperty('newPrice', 0)
        self._addNumberProperty('rewardIndex', 0)
        self._addBoolProperty('isSelected', False)
        self._addNumberProperty('intCD', 0)
