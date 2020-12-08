# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/new_year_vehicle_slot_view_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_drop_down_menu_model import NY2020DropDownMenuModel
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_bonus_info_model import NewYearBonusInfoModel

class NewYearVehicleSlotViewModel(ViewModel):
    __slots__ = ('onClearBtnClick',)
    CHANGE_AVAILABLE = 0
    CHANGE_TIME_OUT = 1
    CHANGE_IN_BATTLE = 2
    SLOT_DISABLED = 3
    SET_AVAILABLE = 4
    SET_COOLDOWN = 5
    CHANGE_IN_SQUAD = 6

    def __init__(self, properties=15, commands=1):
        super(NewYearVehicleSlotViewModel, self).__init__(properties=properties, commands=commands)

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

    def getLevelIcon(self):
        return self._getResource(8)

    def setLevelIcon(self, value):
        self._setResource(8, value)

    def getVehicleTypeIcon(self):
        return self._getResource(9)

    def setVehicleTypeIcon(self, value):
        self._setResource(9, value)

    def getVehicleCD(self):
        return self._getNumber(10)

    def setVehicleCD(self, value):
        self._setNumber(10, value)

    def getCooldown(self):
        return self._getNumber(11)

    def setCooldown(self, value):
        self._setNumber(11, value)

    def getChangePriceString(self):
        return self._getString(12)

    def setChangePriceString(self, value):
        self._setString(12, value)

    def getIsPostEvent(self):
        return self._getBool(13)

    def setIsPostEvent(self, value):
        self._setBool(13, value)

    def getIsExtraSlot(self):
        return self._getBool(14)

    def setIsExtraSlot(self, value):
        self._setBool(14, value)

    def _initialize(self):
        super(NewYearVehicleSlotViewModel, self)._initialize()
        self._addViewModelProperty('choiceBonusesDropDown', NY2020DropDownMenuModel())
        self._addViewModelProperty('bonus', NewYearBonusInfoModel())
        self._addStringProperty('vehicleName', '')
        self._addNumberProperty('slotID', 0)
        self._addStringProperty('levelStr', '')
        self._addResourceProperty('vehicleIcon', R.invalid())
        self._addResourceProperty('nationIcon', R.invalid())
        self._addNumberProperty('slotState', 0)
        self._addResourceProperty('levelIcon', R.invalid())
        self._addResourceProperty('vehicleTypeIcon', R.invalid())
        self._addNumberProperty('vehicleCD', 0)
        self._addNumberProperty('cooldown', 0)
        self._addStringProperty('changePriceString', '')
        self._addBoolProperty('isPostEvent', False)
        self._addBoolProperty('isExtraSlot', False)
        self.onClearBtnClick = self._addCommand('onClearBtnClick')
