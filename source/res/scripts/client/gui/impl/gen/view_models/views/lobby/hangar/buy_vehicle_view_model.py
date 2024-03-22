# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/hangar/buy_vehicle_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel
from gui.impl.gen.view_models.views.lobby.hangar.buy_vehicle_option_model import BuyVehicleOptionModel
from gui.impl.gen.view_models.views.lobby.hangar.buy_vehicle_price_model import BuyVehiclePriceModel
from gui.impl.gen.view_models.views.lobby.hangar.buy_vehicle_simple_tooltip_model import BuyVehicleSimpleTooltipModel

class BuyVehicleViewModel(ViewModel):
    __slots__ = ('onCloseBtnClick', 'onBuyBtnClick', 'onBackClick', 'onOptionClick', 'onSelectTradeInVehicleToSell', 'onClearTradeInVehicleToSell', 'onDisclaimerClick')
    VEHICLE_NOT_SELECTED_CD = -1
    BUYING_RENT_IDX = -1
    RENT_NOT_SELECTED_IDX = -2
    ACTION_PRICE_TOOLTIP = 'actionPrice'
    TRADE_IN_INFO_NOT_AVAILABLE_TOOLTIP = 'tradeInInfoNotAvailable'
    TRADE_IN_INFO_TOOLTIP = 'tradeInInfo'
    TRADE_IN_STATE_NOT_AVAILABLE_TOOLTIP = 'tradeInStateNotAvailable'
    SELECTED_VEHICLE_TRADEOFF_TOOLTIP = 'selectedVehicleTradeOff'
    VEHICLE_SELL_CONFIRMATION_POPOVER = 'VehicleSellConfirmationPopover'
    RENTAL_TERM_SELECTION_POPOVER = 'RentalTermSelectionPopover'

    def __init__(self, properties=15, commands=7):
        super(BuyVehicleViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicle(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleType():
        return VehicleModel

    @property
    def tradeInVehicleToSell(self):
        return self._getViewModel(1)

    @staticmethod
    def getTradeInVehicleToSellType():
        return VehicleModel

    @property
    def totals(self):
        return self._getViewModel(2)

    @staticmethod
    def getTotalsType():
        return BuyVehiclePriceModel

    @property
    def buyButtonTooltip(self):
        return self._getViewModel(3)

    @staticmethod
    def getBuyButtonTooltipType():
        return BuyVehicleSimpleTooltipModel

    def getIsRestore(self):
        return self._getBool(4)

    def setIsRestore(self, value):
        self._setBool(4, value)

    def getHasTradeInWidget(self):
        return self._getBool(5)

    def setHasTradeInWidget(self, value):
        self._setBool(5, value)

    def getHasTradeInVehiclesToSelect(self):
        return self._getBool(6)

    def setHasTradeInVehiclesToSelect(self, value):
        self._setBool(6, value)

    def getHasTradeInGoldConfirmation(self):
        return self._getBool(7)

    def setHasTradeInGoldConfirmation(self, value):
        self._setBool(7, value)

    def getHasDisclaimer(self):
        return self._getBool(8)

    def setHasDisclaimer(self, value):
        self._setBool(8, value)

    def getIsBuyButtonEnabled(self):
        return self._getBool(9)

    def setIsBuyButtonEnabled(self, value):
        self._setBool(9, value)

    def getIsRentAvailable(self):
        return self._getBool(10)

    def setIsRentAvailable(self, value):
        self._setBool(10, value)

    def getTitle(self):
        return self._getString(11)

    def setTitle(self, value):
        self._setString(11, value)

    def getRentButtonLabel(self):
        return self._getString(12)

    def setRentButtonLabel(self, value):
        self._setString(12, value)

    def getBuyButtonLabel(self):
        return self._getString(13)

    def setBuyButtonLabel(self, value):
        self._setString(13, value)

    def getOptions(self):
        return self._getArray(14)

    def setOptions(self, value):
        self._setArray(14, value)

    @staticmethod
    def getOptionsType():
        return BuyVehicleOptionModel

    def _initialize(self):
        super(BuyVehicleViewModel, self)._initialize()
        self._addViewModelProperty('vehicle', VehicleModel())
        self._addViewModelProperty('tradeInVehicleToSell', VehicleModel())
        self._addViewModelProperty('totals', BuyVehiclePriceModel())
        self._addViewModelProperty('buyButtonTooltip', BuyVehicleSimpleTooltipModel())
        self._addBoolProperty('isRestore', False)
        self._addBoolProperty('hasTradeInWidget', False)
        self._addBoolProperty('hasTradeInVehiclesToSelect', False)
        self._addBoolProperty('hasTradeInGoldConfirmation', False)
        self._addBoolProperty('hasDisclaimer', False)
        self._addBoolProperty('isBuyButtonEnabled', False)
        self._addBoolProperty('isRentAvailable', False)
        self._addStringProperty('title', '')
        self._addStringProperty('rentButtonLabel', '')
        self._addStringProperty('buyButtonLabel', '')
        self._addArrayProperty('options', Array())
        self.onCloseBtnClick = self._addCommand('onCloseBtnClick')
        self.onBuyBtnClick = self._addCommand('onBuyBtnClick')
        self.onBackClick = self._addCommand('onBackClick')
        self.onOptionClick = self._addCommand('onOptionClick')
        self.onSelectTradeInVehicleToSell = self._addCommand('onSelectTradeInVehicleToSell')
        self.onClearTradeInVehicleToSell = self._addCommand('onClearTradeInVehicleToSell')
        self.onDisclaimerClick = self._addCommand('onDisclaimerClick')
