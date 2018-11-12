# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/buy_vehicle_view/equipment_block_model.py
import typing
from frameworks.wulf import Resource
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.ui_kit.list_model import ListModel
from gui.impl.gen.view_models.ui_kit.vehicle_action_btn_model import VehicleActionBtnModel
from gui.impl.gen.view_models.ui_kit.vehicle_btn_model import VehicleBtnModel
from gui.impl.gen.view_models.views.buy_vehicle_view.additional_equipment_slot_model import AdditionalEquipmentSlotModel

class EquipmentBlockModel(ViewModel):
    __slots__ = ('onCancelTradeOffVehicle',)

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

    def getBuyVehicleIntCD(self):
        return self._getNumber(9)

    def setBuyVehicleIntCD(self, value):
        self._setNumber(9, value)

    def getSelectedRentID(self):
        return self._getNumber(10)

    def setSelectedRentID(self, value):
        self._setNumber(10, value)

    def getSelectedRentDays(self):
        return self._getNumber(11)

    def setSelectedRentDays(self, value):
        self._setNumber(11, value)

    def getSelectedRentType(self):
        return self._getNumber(12)

    def setSelectedRentType(self, value):
        self._setNumber(12, value)

    def getSelectedRentSeason(self):
        return self._getNumber(13)

    def setSelectedRentSeason(self, value):
        self._setNumber(13, value)

    def getEmtySlotAvailable(self):
        return self._getBool(14)

    def setEmtySlotAvailable(self, value):
        self._setBool(14, value)

    def getIsRestore(self):
        return self._getBool(15)

    def setIsRestore(self, value):
        self._setBool(15, value)

    def getIsSlotAnimPlaying(self):
        return self._getBool(16)

    def setIsSlotAnimPlaying(self, value):
        self._setBool(16, value)

    def getBuyBtnLabel(self):
        return self._getResource(17)

    def setBuyBtnLabel(self, value):
        self._setResource(17, value)

    def getConfirmGoldPrice(self):
        return self._getNumber(18)

    def setConfirmGoldPrice(self, value):
        self._setNumber(18, value)

    def getPopoverIsAvailable(self):
        return self._getBool(19)

    def setPopoverIsAvailable(self, value):
        self._setBool(19, value)

    def getShowBuyBootcampAnim(self):
        return self._getBool(20)

    def setShowBuyBootcampAnim(self, value):
        self._setBool(20, value)

    def getIsRentVisible(self):
        return self._getBool(21)

    def setIsRentVisible(self, value):
        self._setBool(21, value)

    def _initialize(self):
        super(EquipmentBlockModel, self)._initialize()
        self._addViewModelProperty('totalPrice', ListModel())
        self._addViewModelProperty('ammo', AdditionalEquipmentSlotModel())
        self._addViewModelProperty('slot', AdditionalEquipmentSlotModel())
        self._addViewModelProperty('vehicleBtn', VehicleBtnModel())
        self._addViewModelProperty('vehicleRentBtn', VehicleActionBtnModel())
        self._addViewModelProperty('vehicleTradeInBtn', VehicleActionBtnModel())
        self._addBoolProperty('buyBtnIsEnabled', False)
        self._addBoolProperty('tradeInIsEnabled', False)
        self._addNumberProperty('tradeOffVehicleIntCD', -1)
        self._addNumberProperty('buyVehicleIntCD', 0)
        self._addNumberProperty('selectedRentID', 0)
        self._addNumberProperty('selectedRentDays', 0)
        self._addNumberProperty('selectedRentType', 0)
        self._addNumberProperty('selectedRentSeason', 0)
        self._addBoolProperty('emtySlotAvailable', False)
        self._addBoolProperty('isRestore', False)
        self._addBoolProperty('isSlotAnimPlaying', False)
        self._addResourceProperty('buyBtnLabel', Resource.INVALID)
        self._addNumberProperty('confirmGoldPrice', 0)
        self._addBoolProperty('popoverIsAvailable', False)
        self._addBoolProperty('showBuyBootcampAnim', False)
        self._addBoolProperty('isRentVisible', False)
        self.onCancelTradeOffVehicle = self._addCommand('onCancelTradeOffVehicle')
