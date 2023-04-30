# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/winback/vehicle_selectable_bonus_model.py
from gui.impl.gen.view_models.common.missions.bonuses.item_bonus_model import ItemBonusModel

class VehicleSelectableBonusModel(ItemBonusModel):
    __slots__ = ()

    def __init__(self, properties=12, commands=0):
        super(VehicleSelectableBonusModel, self).__init__(properties=properties, commands=commands)

    def getVehicleLvl(self):
        return self._getNumber(9)

    def setVehicleLvl(self, value):
        self._setNumber(9, value)

    def getPriceDiscount(self):
        return self._getNumber(10)

    def setPriceDiscount(self, value):
        self._setNumber(10, value)

    def getExpDiscount(self):
        return self._getNumber(11)

    def setExpDiscount(self, value):
        self._setNumber(11, value)

    def _initialize(self):
        super(VehicleSelectableBonusModel, self)._initialize()
        self._addNumberProperty('vehicleLvl', 0)
        self._addNumberProperty('priceDiscount', 0)
        self._addNumberProperty('expDiscount', 0)
