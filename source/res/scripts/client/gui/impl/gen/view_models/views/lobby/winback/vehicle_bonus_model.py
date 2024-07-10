# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/winback/vehicle_bonus_model.py
from gui.impl.gen.view_models.common.missions.bonuses.item_bonus_model import ItemBonusModel

class VehicleBonusModel(ItemBonusModel):
    __slots__ = ()

    def __init__(self, properties=19, commands=0):
        super(VehicleBonusModel, self).__init__(properties=properties, commands=commands)

    def getIsElite(self):
        return self._getBool(10)

    def setIsElite(self, value):
        self._setBool(10, value)

    def getIsFromStorage(self):
        return self._getBool(11)

    def setIsFromStorage(self, value):
        self._setBool(11, value)

    def getVehicleName(self):
        return self._getString(12)

    def setVehicleName(self, value):
        self._setString(12, value)

    def getUserName(self):
        return self._getString(13)

    def setUserName(self, value):
        self._setString(13, value)

    def getVehicleType(self):
        return self._getString(14)

    def setVehicleType(self, value):
        self._setString(14, value)

    def getNation(self):
        return self._getString(15)

    def setNation(self, value):
        self._setString(15, value)

    def getVehicleLvl(self):
        return self._getNumber(16)

    def setVehicleLvl(self, value):
        self._setNumber(16, value)

    def getPriceDiscount(self):
        return self._getNumber(17)

    def setPriceDiscount(self, value):
        self._setNumber(17, value)

    def getExpDiscount(self):
        return self._getNumber(18)

    def setExpDiscount(self, value):
        self._setNumber(18, value)

    def _initialize(self):
        super(VehicleBonusModel, self)._initialize()
        self._addBoolProperty('isElite', True)
        self._addBoolProperty('isFromStorage', False)
        self._addStringProperty('vehicleName', '')
        self._addStringProperty('userName', '')
        self._addStringProperty('vehicleType', '')
        self._addStringProperty('nation', '')
        self._addNumberProperty('vehicleLvl', 0)
        self._addNumberProperty('priceDiscount', 0)
        self._addNumberProperty('expDiscount', 0)
