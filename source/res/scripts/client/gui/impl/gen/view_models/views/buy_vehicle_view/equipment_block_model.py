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

    def getSelectedRentTerm(self):
        return self._getNumber(10)

    def setSelectedRentTerm(self, value):
        self._setNumber(10, value)

    def getEmtySlotAvailable(self):
        return self._getBool(11)

    def setEmtySlotAvailable(self, value):
        self._setBool(11, value)

    def getIsRestore(self):
        return self._getBool(12)

    def setIsRestore(self, value):
        self._setBool(12, value)

    def getIsSlotAnimPlaying(self):
        return self._getBool(13)

    def setIsSlotAnimPlaying(self, value):
        self._setBool(13, value)

    def getBuyBtnLabel(self):
        return self._getResource(14)

    def setBuyBtnLabel(self, value):
        self._setResource(14, value)

    def getConfirmGoldPrice(self):
        return self._getNumber(15)

    def setConfirmGoldPrice(self, value):
        self._setNumber(15, value)

    def getPopoverIsAvailable(self):
        return self._getBool(16)

    def setPopoverIsAvailable(self, value):
        self._setBool(16, value)

    def getShowBuyBootcampAnim(self):
        return self._getBool(17)

    def setShowBuyBootcampAnim(self, value):
        self._setBool(17, value)

    def getIsRentVisible(self):
        return self._getBool(18)

    def setIsRentVisible(self, value):
        self._setBool(18, value)

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
        self._addNumberProperty('selectedRentTerm', 0)
        self._addBoolProperty('emtySlotAvailable', False)
        self._addBoolProperty('isRestore', False)
        self._addBoolProperty('isSlotAnimPlaying', False)
        self._addResourceProperty('buyBtnLabel', Resource.INVALID)
        self._addNumberProperty('confirmGoldPrice', 0)
        self._addBoolProperty('popoverIsAvailable', False)
        self._addBoolProperty('showBuyBootcampAnim', False)
        self._addBoolProperty('isRentVisible', False)
        self.onCancelTradeOffVehicle = self._addCommand('onCancelTradeOffVehicle')
