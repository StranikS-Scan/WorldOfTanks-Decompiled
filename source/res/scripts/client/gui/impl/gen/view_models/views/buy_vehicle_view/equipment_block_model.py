# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/buy_vehicle_view/equipment_block_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.ui_kit.button_icon_text_model import ButtonIconTextModel
from gui.impl.gen.view_models.ui_kit.list_model import ListModel
from gui.impl.gen.view_models.ui_kit.vehicle_btn_model import VehicleBtnModel
from gui.impl.gen.view_models.views.buy_vehicle_view.additional_equipment_slot_model import AdditionalEquipmentSlotModel

class EquipmentBlockModel(ViewModel):
    __slots__ = ('onSelectTradeOffVehicle', 'onCancelTradeOffVehicle')

    def __init__(self, properties=24, commands=2):
        super(EquipmentBlockModel, self).__init__(properties=properties, commands=commands)

    @property
    def totalPrice(self):
        return self._getViewModel(0)

    @property
    def ammo(self):
        return self._getViewModel(1)

    @property
    def slot(self):
        return self._getViewModel(2)

    @property
    def vehicleBtn(self):
        return self._getViewModel(3)

    @property
    def vehicleRentBtn(self):
        return self._getViewModel(4)

    @property
    def vehicleTradeInBtn(self):
        return self._getViewModel(5)

    def getBuyBtnIsEnabled(self):
        return self._getBool(6)

    def setBuyBtnIsEnabled(self, value):
        self._setBool(6, value)

    def getTradeInIsEnabled(self):
        return self._getBool(7)

    def setTradeInIsEnabled(self, value):
        self._setBool(7, value)

    def getTradeOffVehicleIntCD(self):
        return self._getNumber(8)

    def setTradeOffVehicleIntCD(self, value):
        self._setNumber(8, value)

    def getTradeOffWidgetEnabled(self):
        return self._getBool(9)

    def setTradeOffWidgetEnabled(self, value):
        self._setBool(9, value)

    def getBuyVehicleIntCD(self):
        return self._getNumber(10)

    def setBuyVehicleIntCD(self, value):
        self._setNumber(10, value)

    def getSelectedRentID(self):
        return self._getNumber(11)

    def setSelectedRentID(self, value):
        self._setNumber(11, value)

    def getSelectedRentDays(self):
        return self._getNumber(12)

    def setSelectedRentDays(self, value):
        self._setNumber(12, value)

    def getSelectedRentType(self):
        return self._getNumber(13)

    def setSelectedRentType(self, value):
        self._setNumber(13, value)

    def getSelectedRentSeason(self):
        return self._getNumber(14)

    def setSelectedRentSeason(self, value):
        self._setNumber(14, value)

    def getEmtySlotAvailable(self):
        return self._getBool(15)

    def setEmtySlotAvailable(self, value):
        self._setBool(15, value)

    def getIsRestore(self):
        return self._getBool(16)

    def setIsRestore(self, value):
        self._setBool(16, value)

    def getIsSlotAnimPlaying(self):
        return self._getBool(17)

    def setIsSlotAnimPlaying(self, value):
        self._setBool(17, value)

    def getBuyBtnLabel(self):
        return self._getResource(18)

    def setBuyBtnLabel(self, value):
        self._setResource(18, value)

    def getConfirmGoldPrice(self):
        return self._getNumber(19)

    def setConfirmGoldPrice(self, value):
        self._setNumber(19, value)

    def getPopoverIsAvailable(self):
        return self._getBool(20)

    def setPopoverIsAvailable(self, value):
        self._setBool(20, value)

    def getIsRentVisible(self):
        return self._getBool(21)

    def setIsRentVisible(self, value):
        self._setBool(21, value)

    def getPersonalTradeInIsEnabled(self):
        return self._getBool(22)

    def setPersonalTradeInIsEnabled(self, value):
        self._setBool(22, value)

    def getTradeInTooltip(self):
        return self._getString(23)

    def setTradeInTooltip(self, value):
        self._setString(23, value)

    def _initialize(self):
        super(EquipmentBlockModel, self)._initialize()
        self._addViewModelProperty('totalPrice', ListModel())
        self._addViewModelProperty('ammo', AdditionalEquipmentSlotModel())
        self._addViewModelProperty('slot', AdditionalEquipmentSlotModel())
        self._addViewModelProperty('vehicleBtn', VehicleBtnModel())
        self._addViewModelProperty('vehicleRentBtn', ButtonIconTextModel())
        self._addViewModelProperty('vehicleTradeInBtn', ButtonIconTextModel())
        self._addBoolProperty('buyBtnIsEnabled', False)
        self._addBoolProperty('tradeInIsEnabled', False)
        self._addNumberProperty('tradeOffVehicleIntCD', -1)
        self._addBoolProperty('tradeOffWidgetEnabled', True)
        self._addNumberProperty('buyVehicleIntCD', 0)
        self._addNumberProperty('selectedRentID', 0)
        self._addNumberProperty('selectedRentDays', 0)
        self._addNumberProperty('selectedRentType', 0)
        self._addNumberProperty('selectedRentSeason', 0)
        self._addBoolProperty('emtySlotAvailable', False)
        self._addBoolProperty('isRestore', False)
        self._addBoolProperty('isSlotAnimPlaying', False)
        self._addResourceProperty('buyBtnLabel', R.invalid())
        self._addNumberProperty('confirmGoldPrice', 0)
        self._addBoolProperty('popoverIsAvailable', False)
        self._addBoolProperty('isRentVisible', False)
        self._addBoolProperty('personalTradeInIsEnabled', False)
        self._addStringProperty('tradeInTooltip', '')
        self.onSelectTradeOffVehicle = self._addCommand('onSelectTradeOffVehicle')
        self.onCancelTradeOffVehicle = self._addCommand('onCancelTradeOffVehicle')
