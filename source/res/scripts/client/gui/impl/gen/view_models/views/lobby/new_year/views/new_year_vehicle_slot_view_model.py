# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/new_year_vehicle_slot_view_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel
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

    def __init__(self, properties=13, commands=1):
        super(NewYearVehicleSlotViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def bonus(self):
        return self._getViewModel(0)

    def getVehicleName(self):
        return self._getString(1)

    def setVehicleName(self, value):
        self._setString(1, value)

    def getSlotID(self):
        return self._getNumber(2)

    def setSlotID(self, value):
        self._setNumber(2, value)

    def getLevelStr(self):
        return self._getString(3)

    def setLevelStr(self, value):
        self._setString(3, value)

    def getVehicleIcon(self):
        return self._getResource(4)

    def setVehicleIcon(self, value):
        self._setResource(4, value)

    def getNationIcon(self):
        return self._getResource(5)

    def setNationIcon(self, value):
        self._setResource(5, value)

    def getSlotState(self):
        return self._getNumber(6)

    def setSlotState(self, value):
        self._setNumber(6, value)

    def getLevelIcon(self):
        return self._getResource(7)

    def setLevelIcon(self, value):
        self._setResource(7, value)

    def getVehicleTypeIcon(self):
        return self._getResource(8)

    def setVehicleTypeIcon(self, value):
        self._setResource(8, value)

    def getVehicleCD(self):
        return self._getNumber(9)

    def setVehicleCD(self, value):
        self._setNumber(9, value)

    def getCooldown(self):
        return self._getNumber(10)

    def setCooldown(self, value):
        self._setNumber(10, value)

    def getChangePriceString(self):
        return self._getString(11)

    def setChangePriceString(self, value):
        self._setString(11, value)

    def getIsPostEvent(self):
        return self._getBool(12)

    def setIsPostEvent(self, value):
        self._setBool(12, value)

    def _initialize(self):
        super(NewYearVehicleSlotViewModel, self)._initialize()
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
        self.onClearBtnClick = self._addCommand('onClearBtnClick')
