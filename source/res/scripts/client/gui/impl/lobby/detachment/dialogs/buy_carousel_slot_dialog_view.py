# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/dialogs/buy_carousel_slot_dialog_view.py
import typing
from frameworks.wulf import ViewSettings
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport.backport_tooltip import createBackportTooltipContent
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.dialogs.buy_carousel_slot_dialog_view_model import BuyCarouselSlotDialogViewModel
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogView
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Optional
    from gui.shared.money import Money
    from gui.shared.gui_items.gui_item_economics import ItemPrice

class BuyCarouselSlotDialogView(FullScreenDialogView):
    __slots__ = ()
    __NUMBER_DORM_ROOMS = 1
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.detachment.dialogs.BuyCarouselSlotDialogView())
        settings.model = BuyCarouselSlotDialogViewModel()
        super(BuyCarouselSlotDialogView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BuyCarouselSlotDialogView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId == TOOLTIPS_CONSTANTS.NOT_ENOUGH_MONEY:
                currency = event.getArgument('currency')
                value = int(event.getArgument('value', 0))
                shortage = max(value - self.__itemsCache.items.stats.money.get(currency, 0), 0)
                return createBackportTooltipContent(TOOLTIPS_CONSTANTS.NOT_ENOUGH_MONEY, (shortage, currency))
        return super(BuyCarouselSlotDialogView, self).createToolTipContent(event, contentID)

    def _onLoading(self):
        super(BuyCarouselSlotDialogView, self)._onLoading()
        self.__fillModel()

    def _onInventoryResync(self, *args, **kwargs):
        super(BuyCarouselSlotDialogView, self)._onInventoryResync(*args, **kwargs)
        self.__fillModel()

    def _addListeners(self):
        super(BuyCarouselSlotDialogView, self)._addListeners()
        g_clientUpdateManager.addMoneyCallback(self._onMoneyUpdate)
        g_clientUpdateManager.addCallbacks({'shop': self._onMoneyUpdate})

    def _removeListeners(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(BuyCarouselSlotDialogView, self)._removeListeners()

    def _onMoneyUpdate(self, *args, **kwargs):
        self.__fillModel()

    def __fillModel(self):
        with self.viewModel.transaction() as model:
            items = self.__itemsCache.items
            model.setHasEmptySlots(items.inventory.getFreeSlots(items.stats.vehicleSlots) > 0)
            model.setNumberDormitoryRoom(self.__NUMBER_DORM_ROOMS)
            model.setTitleBody(R.strings.detachment.hangarBuy.title())
            model.setAcceptButtonText(R.strings.detachment.common.buy())
            model.setCancelButtonText(R.strings.detachment.common.cancel())
            itemPrice = items.shop.getVehicleSlotsItemPrice(items.stats.vehicleSlots)
            currency = self.__getCurrency(itemPrice.price)
            model.priceModel.setValue(int(itemPrice.price.get(currency)))
            model.priceModel.setType(currency)
            model.priceModel.setHasDiscount(itemPrice.isActionPrice())
            model.priceModel.setDiscountValue(-itemPrice.getActionPrc())
            model.priceModel.setIsEnough(items.stats.money.getShortage(itemPrice.price).get(currency, 0) == 0)

    def __getCurrency(self, price):
        for currency in Currency.ALL:
            if price.get(currency):
                return currency
