# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/secret_event/buy_fuel_view.py
from gui.impl.gen import R
from gui.impl.lobby.secret_event import convertPriceToMoney, EventViewMixin
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogView
from gui.impl.gen.view_models.views.lobby.secret_event.buy_fuel_model import BuyFuelModel
from helpers import dependency
from skeletons.gui.game_event_controller import IGameEventController

class BuyFuelView(FullScreenDialogView, EventViewMixin):
    gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, layoutID=R.views.lobby.secretEvent.FuelBuyWindow()):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.TOP_WINDOW_VIEW
        settings.model = BuyFuelModel()
        super(BuyFuelView, self).__init__(settings, False)

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId == TOOLTIPS_CONSTANTS.ACTION_PRICE:
                energy = self.gameEventController.getEnergy()
                args = (ACTION_TOOLTIPS_TYPE.ITEM,
                 GUI_ITEM_TYPE.VEHICLE,
                 [convertPriceToMoney(*energy.getPrice())],
                 [convertPriceToMoney(*energy.getDefPrice())],
                 True)
                window = BackportTooltipWindow(createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=args), self.getParentWindow())
                window.load()
                return window
        return super(BuyFuelView, self).createToolTip(event)

    def _onLoading(self, *args, **kwargs):
        super(BuyFuelView, self)._onLoading(*args, **kwargs)
        self.__setParams()

    def __setParams(self):
        energy = self.gameEventController.getEnergy()
        currency, amount = energy.getPrice()
        discount = energy.getDiscount()
        shortage = self._stats.money.getShortage(convertPriceToMoney(*energy.getPrice()))
        isEnough = bool(shortage)
        with self.viewModel.transaction() as vm:
            vm.setIsAcceptDisabled(isEnough)
            vm.setTitleBody(R.strings.event.fuelWindow.buyTitle())
            vm.fuelPrice.setCurrencyType(currency)
            vm.fuelPrice.setValue(amount)
            vm.fuelPrice.setIsDiscount(bool(discount))
            vm.fuelPrice.setDiscountValue(discount)
            vm.fuelPrice.setIsEnough(isEnough)

    def _onAcceptClicked(self):
        super(BuyFuelView, self)._onAcceptClicked()
        self.gameEventController.getEnergy().buy()

    def _initialize(self):
        super(BuyFuelView, self)._initialize()
        self._eventCacheSubscribe()

    def _finalize(self):
        super(BuyFuelView, self)._finalize()
        self._eventCacheUnsubscribe()
