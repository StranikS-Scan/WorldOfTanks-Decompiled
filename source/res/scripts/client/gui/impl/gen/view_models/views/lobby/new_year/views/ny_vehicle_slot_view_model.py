# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/ny_vehicle_slot_view_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.ny_bonus_dropdown_model import NyBonusDropdownModel
from gui.impl.gen.view_models.views.lobby.new_year.views.ny_bonus_info_model import NyBonusInfoModel

class NyVehicleSlotViewModel(ViewModel):
    __slots__ = ()
    CHANGE_AVAILABLE = 0
    CHANGE_TIME_OUT = 1
    CHANGE_IN_BATTLE = 2
    SLOT_DISABLED = 3
    SET_AVAILABLE = 4
    SET_COOLDOWN = 5
    CHANGE_IN_SQUAD = 6

    def __init__(self, properties=17, commands=0):
        super(NyVehicleSlotViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def choiceBonusesDropDown(self):
        return self._getViewModel(0)

    @property
    def bonus(self):
        return self._getViewModel(1)

    def getVehicleName(self):
        return self._getString(2)

    def setVehicleName(self, value):
        self._setString(2, value)

    def getSlotID(self):
        return self._getNumber(3)

    def setSlotID(self, value):
        self._setNumber(3, value)

    def getLevelStr(self):
        return self._getString(4)

    def setLevelStr(self, value):
        self._setString(4, value)

    def getVehicleIcon(self):
        return self._getResource(5)

    def setVehicleIcon(self, value):
        self._setResource(5, value)

    def getNationIcon(self):
        return self._getResource(6)

    def setNationIcon(self, value):
        self._setResource(6, value)

    def getSlotState(self):
        return self._getNumber(7)

    def setSlotState(self, value):
        self._setNumber(7, value)

    def getVehicleLevel(self):
        return self._getString(8)

    def setVehicleLevel(self, value):
        self._setString(8, value)

    def getVehicleType(self):
        return self._getString(9)

    def setVehicleType(self, value):
        self._setString(9, value)

    def getVehicleTypeIcon(self):
        return self._getResource(10)

    def setVehicleTypeIcon(self, value):
        self._setResource(10, value)

    def getCooldown(self):
        return self._getNumber(11)

    def setCooldown(self, value):
        self._setNumber(11, value)

    def getChangePrice(self):
        return self._getNumber(12)

    def setChangePrice(self, value):
        self._setNumber(12, value)

    def getCurrency(self):
        return self._getString(13)

    def setCurrency(self, value):
        self._setString(13, value)

    def getIsExtraSlot(self):
        return self._getBool(14)

    def setIsExtraSlot(self, value):
        self._setBool(14, value)

    def getUnlockExtraSlotTaskCount(self):
        return self._getNumber(15)

    def setUnlockExtraSlotTaskCount(self, value):
        self._setNumber(15, value)

    def getUnlockSlotAtmosphereLevel(self):
        return self._getNumber(16)

    def setUnlockSlotAtmosphereLevel(self, value):
        self._setNumber(16, value)

    def _initialize(self):
        super(NyVehicleSlotViewModel, self)._initialize()
        self._addViewModelProperty('choiceBonusesDropDown', NyBonusDropdownModel())
        self._addViewModelProperty('bonus', NyBonusInfoModel())
        self._addStringProperty('vehicleName', '')
        self._addNumberProperty('slotID', 0)
        self._addStringProperty('levelStr', '')
        self._addResourceProperty('vehicleIcon', R.invalid())
        self._addResourceProperty('nationIcon', R.invalid())
        self._addNumberProperty('slotState', 0)
        self._addStringProperty('vehicleLevel', '')
        self._addStringProperty('vehicleType', '')
        self._addResourceProperty('vehicleTypeIcon', R.invalid())
        self._addNumberProperty('cooldown', 0)
        self._addNumberProperty('changePrice', 0)
        self._addStringProperty('currency', '')
        self._addBoolProperty('isExtraSlot', False)
        self._addNumberProperty('unlockExtraSlotTaskCount', 0)
        self._addNumberProperty('unlockSlotAtmosphereLevel', 0)
