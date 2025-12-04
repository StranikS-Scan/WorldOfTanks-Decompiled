# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/gen/view_models/views/lobby/feature/armory_yard_rewards_vehicle_model.py
from gui.impl.gen.view_models.common.missions.bonuses.item_bonus_model import ItemBonusModel

class ArmoryYardRewardsVehicleModel(ItemBonusModel):
    __slots__ = ()

    def __init__(self, properties=27, commands=0):
        super(ArmoryYardRewardsVehicleModel, self).__init__(properties=properties, commands=commands)

    def getIndex(self):
        return self._getNumber(9)

    def setIndex(self, value):
        self._setNumber(9, value)

    def getVehicleImg(self):
        return self._getString(10)

    def setVehicleImg(self, value):
        self._setString(10, value)

    def getTooltipId(self):
        return self._getString(11)

    def setTooltipId(self, value):
        self._setString(11, value)

    def getTooltipContentId(self):
        return self._getString(12)

    def setTooltipContentId(self, value):
        self._setString(12, value)

    def getVehicleName(self):
        return self._getString(13)

    def setVehicleName(self, value):
        self._setString(13, value)

    def getType(self):
        return self._getString(14)

    def setType(self, value):
        self._setString(14, value)

    def getLevel(self):
        return self._getNumber(15)

    def setLevel(self, value):
        self._setNumber(15, value)

    def getShortVehicleLabel(self):
        return self._getString(16)

    def setShortVehicleLabel(self, value):
        self._setString(16, value)

    def getNationTag(self):
        return self._getString(17)

    def setNationTag(self, value):
        self._setString(17, value)

    def getIsElite(self):
        return self._getBool(18)

    def setIsElite(self, value):
        self._setBool(18, value)

    def getIsRent(self):
        return self._getBool(19)

    def setIsRent(self, value):
        self._setBool(19, value)

    def getRentDays(self):
        return self._getNumber(20)

    def setRentDays(self, value):
        self._setNumber(20, value)

    def getRentBattles(self):
        return self._getNumber(21)

    def setRentBattles(self, value):
        self._setNumber(21, value)

    def getInInventory(self):
        return self._getBool(22)

    def setInInventory(self, value):
        self._setBool(22, value)

    def getVehicleCD(self):
        return self._getNumber(23)

    def setVehicleCD(self, value):
        self._setNumber(23, value)

    def getCompensatedBonus(self):
        return self._getString(24)

    def setCompensatedBonus(self, value):
        self._setString(24, value)

    def getWasSold(self):
        return self._getBool(25)

    def setWasSold(self, value):
        self._setBool(25, value)

    def getRole(self):
        return self._getString(26)

    def setRole(self, value):
        self._setString(26, value)

    def _initialize(self):
        super(ArmoryYardRewardsVehicleModel, self)._initialize()
        self._addNumberProperty('index', 0)
        self._addStringProperty('vehicleImg', '')
        self._addStringProperty('tooltipId', '')
        self._addStringProperty('tooltipContentId', '')
        self._addStringProperty('vehicleName', '')
        self._addStringProperty('type', '')
        self._addNumberProperty('level', 0)
        self._addStringProperty('shortVehicleLabel', '')
        self._addStringProperty('nationTag', '')
        self._addBoolProperty('isElite', False)
        self._addBoolProperty('isRent', False)
        self._addNumberProperty('rentDays', 0)
        self._addNumberProperty('rentBattles', 0)
        self._addBoolProperty('inInventory', False)
        self._addNumberProperty('vehicleCD', 0)
        self._addStringProperty('compensatedBonus', '')
        self._addBoolProperty('wasSold', False)
        self._addStringProperty('role', '')
