# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/buy_vehicle/buy_vehicle_content_view_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.ui_kit.action_price_model import ActionPriceModel
from gui.impl.gen.view_models.ui_kit.button_icon_text_model import ButtonIconTextModel
from gui.impl.gen.view_models.ui_kit.list_model import ListModel
from gui.impl.gen.view_models.ui_kit.vehicle_btn_model import VehicleBtnModel
from gui.impl.gen.view_models.views.lobby.buy_vehicle.buy_vehicle_item_slot_model import BuyVehicleItemSlotModel

class BuyVehicleContentViewModel(ViewModel):
    __slots__ = ('onSelectTradeOffVehicle', 'onCancelTradeOffVehicle')

    def __init__(self, properties=31, commands=2):
        super(BuyVehicleContentViewModel, self).__init__(properties=properties, commands=commands)

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

    def getTitleLeft(self):
        return self._getString(6)

    def setTitleLeft(self, value):
        self._setString(6, value)

    def getTitleRight(self):
        return self._getString(7)

    def setTitleRight(self, value):
        self._setString(7, value)

    def getVehicleType(self):
        return self._getResource(8)

    def setVehicleType(self, value):
        self._setResource(8, value)

    def getIsElite(self):
        return self._getBool(9)

    def setIsElite(self, value):
        self._setBool(9, value)

    def getBuyBtnIsEnabled(self):
        return self._getBool(10)

    def setBuyBtnIsEnabled(self, value):
        self._setBool(10, value)

    def getTradeInIsEnabled(self):
        return self._getBool(11)

    def setTradeInIsEnabled(self, value):
        self._setBool(11, value)

    def getTradeOffVehicleIntCD(self):
        return self._getNumber(12)

    def setTradeOffVehicleIntCD(self, value):
        self._setNumber(12, value)

    def getTradeOffWidgetEnabled(self):
        return self._getBool(13)

    def setTradeOffWidgetEnabled(self, value):
        self._setBool(13, value)

    def getBuyVehicleIntCD(self):
        return self._getNumber(14)

    def setBuyVehicleIntCD(self, value):
        self._setNumber(14, value)

    def getSelectedRentID(self):
        return self._getNumber(15)

    def setSelectedRentID(self, value):
        self._setNumber(15, value)

    def getSelectedRentDays(self):
        return self._getNumber(16)

    def setSelectedRentDays(self, value):
        self._setNumber(16, value)

    def getSelectedRentType(self):
        return self._getNumber(17)

    def setSelectedRentType(self, value):
        self._setNumber(17, value)

    def getSelectedRentSeason(self):
        return self._getNumber(18)

    def setSelectedRentSeason(self, value):
        self._setNumber(18, value)

    def getEmtySlotAvailable(self):
        return self._getBool(19)

    def setEmtySlotAvailable(self, value):
        self._setBool(19, value)

    def getIsRestore(self):
        return self._getBool(20)

    def setIsRestore(self, value):
        self._setBool(20, value)

    def getIsSlotAnimPlaying(self):
        return self._getBool(21)

    def setIsSlotAnimPlaying(self, value):
        self._setBool(21, value)

    def getBuyBtnLabel(self):
        return self._getResource(22)

    def setBuyBtnLabel(self, value):
        self._setResource(22, value)

    def getConfirmGoldPrice(self):
        return self._getNumber(23)

    def setConfirmGoldPrice(self, value):
        self._setNumber(23, value)

    def getPopoverIsAvailable(self):
        return self._getBool(24)

    def setPopoverIsAvailable(self, value):
        self._setBool(24, value)

    def getIsRentVisible(self):
        return self._getBool(25)

    def setIsRentVisible(self, value):
        self._setBool(25, value)

    def getPersonalTradeInIsEnabled(self):
        return self._getBool(26)

    def setPersonalTradeInIsEnabled(self, value):
        self._setBool(26, value)

    def getTradeInTooltip(self):
        return self._getString(27)

    def setTradeInTooltip(self, value):
        self._setString(27, value)

    def getIsFree(self):
        return self._getBool(28)

    def setIsFree(self, value):
        self._setBool(28, value)

    def getDisabledBuyButtonTooptip(self):
        return self._getString(29)

    def setDisabledBuyButtonTooptip(self, value):
        self._setString(29, value)

    def getBuyBlockLabel(self):
        return self._getResource(30)

    def setBuyBlockLabel(self, value):
        self._setResource(30, value)

    def _initialize(self):
        super(BuyVehicleContentViewModel, self)._initialize()
        self._addViewModelProperty('totalPrice', ListModel())
        self._addViewModelProperty('ammo', BuyVehicleItemSlotModel())
        self._addViewModelProperty('slot', BuyVehicleItemSlotModel())
        self._addViewModelProperty('vehicleBtn', VehicleBtnModel())
        self._addViewModelProperty('vehicleRentBtn', ButtonIconTextModel())
        self._addViewModelProperty('vehicleTradeInBtn', ButtonIconTextModel())
        self._addStringProperty('titleLeft', '')
        self._addStringProperty('titleRight', '')
        self._addResourceProperty('vehicleType', R.invalid())
        self._addBoolProperty('isElite', False)
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
        self._addBoolProperty('isFree', False)
        self._addStringProperty('disabledBuyButtonTooptip', '')
        self._addResourceProperty('buyBlockLabel', R.invalid())
        self.onSelectTradeOffVehicle = self._addCommand('onSelectTradeOffVehicle')
        self.onCancelTradeOffVehicle = self._addCommand('onCancelTradeOffVehicle')
