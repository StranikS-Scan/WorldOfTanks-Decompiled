# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/dialogs/enlarge_barracks_dialog.py
from adisp import adisp_process, adisp_async
from base_crew_dialog_template_view import BaseCrewDialogTemplateView
from gui.impl.backport.backport_tooltip import createBackportTooltipContent
from gui.impl.dialogs.dialog_template_button import CancelButton, ConfirmButton
from gui.impl.dialogs.sub_views.icon.icon_set import IconSet
from gui.impl.dialogs.sub_views.top_right.money_balance import MoneyBalance
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders as Placeholder
from gui.impl.gen.view_models.views.dialogs.dialog_template_button_view_model import ButtonType
from gui.impl.gen.view_models.views.dialogs.template_settings.default_dialog_template_settings import DisplayFlags
from gui.impl.gen.view_models.views.lobby.crew.dialogs.enlarge_barracks_dialog_model import EnlargeBarracksDialogModel
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.crew.tooltips.bunks_confirm_discount_tooltip import BunksConfirmDiscountTooltip
from gui.impl.pub.dialog_window import DialogButtons
from gui.impl.gen.view_models.views.dialogs.sub_views.currency_view_model import CurrencyType
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.gui_items.items_actions import factory
from gui.shared.items_cache import CACHE_SYNC_REASON
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from items.item_price import getBerthPackCount

class EnlargeBarracksDialog(BaseCrewDialogTemplateView):
    __slots__ = ('__berthPrice', '__berthsInPack', '__defaultBerthPrice', '__isDiscount', '__countPacksBerths', '__pricePacksBerths', '__berthCurrency')
    LAYOUT_ID = R.views.lobby.crew.dialogs.EnlargeBarracksDialog()
    VIEW_MODEL = EnlargeBarracksDialogModel
    itemsCache = dependency.descriptor(IItemsCache)
    __STEPPER_MAX_VALUE = 160

    def __init__(self):
        self.__countPacksBerths = 1
        self.__prepareBerthInfo()
        super(EnlargeBarracksDialog, self).__init__()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.dialogs.common.DialogTemplateGenericTooltip():
            shortage = self.__pricePacksBerths.get(self.__berthCurrency) - self.itemsCache.items.stats.money.get(self.__berthCurrency)
            return createBackportTooltipContent(TOOLTIPS_CONSTANTS.NOT_ENOUGH_MONEY, (shortage, self.__berthCurrency))
        return BunksConfirmDiscountTooltip(bunksCount=self.__berthsInPack, oldCost=self.__defaultBerthPrice.get(self.__berthCurrency, 0), newCost=self.__berthPrice.get(self.__berthCurrency, 0), isEnough=self.__isEnoughMoney()) if contentID == R.views.lobby.crew.tooltips.BunksConfirmDiscountTooltip() else super(EnlargeBarracksDialog, self).createToolTipContent(event=event, contentID=contentID)

    @property
    def viewModel(self):
        return super(EnlargeBarracksDialog, self).getViewModel()

    @adisp_async
    @adisp_process
    def _doAction(self, callback):
        action = factory.getAction(factory.BUY_BERTHS, self.__pricePacksBerths, self.__countPacksBerths, self.__berthsInPack, self.getParentWindow())
        result = yield factory.asyncDoAction(action)
        callback(result)

    @adisp_process
    def _enlargeBarracks(self):
        result = yield self._doAction()
        if result:
            super(EnlargeBarracksDialog, self)._setResult(DialogButtons.SUBMIT)

    def _getEvents(self):
        return ((self.viewModel.onBunksCountChange, self.__onBunksCountChange), (self.itemsCache.onSyncCompleted, self.__onCacheResync))

    def _onLoading(self, *args, **kwargs):
        slotsCount, freeBerthsCount = self.__getCountSlotsAndFreeBerths()
        self.setDisplayFlags(DisplayFlags.RESPONSIVEHEADER.value)
        self.setSubView(Placeholder.TOP_RIGHT, MoneyBalance())
        self.setSubView(Placeholder.ICON, IconSet(R.images.gui.maps.icons.crew.place_in_barracks()))
        self.addButton(ConfirmButton(label=R.strings.crew.barracks.action.enlarge(), buttonType=ButtonType.MAIN))
        self.addButton(CancelButton())
        self._updateViewModel(freeBerthsCount, slotsCount)
        super(EnlargeBarracksDialog, self)._onLoading(*args, **kwargs)

    def _getCallbacks(self):
        return (('stats.' + str(self.__berthCurrency), self._onCurrencyUpdate),)

    def _onCurrencyUpdate(self, *_):
        with self.viewModel.transaction() as vm:
            vm.currency.setIsEnough(self.__isEnoughMoney())

    def _setResult(self, result):
        if result == DialogButtons.SUBMIT:
            self._enlargeBarracks()
        else:
            super(EnlargeBarracksDialog, self)._setResult(result)

    def _updateViewModel(self, freeBunksCount, allBunksCount):
        with self.viewModel.transaction() as vm:
            stepper = vm.stepper
            currency = vm.currency
            stepper.setMinimum(self.__berthsInPack)
            stepper.setMaximum(self.__STEPPER_MAX_VALUE)
            stepper.setStepSize(self.__berthsInPack)
            stepper.setValue(self.__berthsInPack)
            currency.setType(CurrencyType(self.__berthCurrency))
            currency.setValue(self.__pricePacksBerths.get(self.__berthCurrency))
            currency.setIsEnough(self.__isEnoughMoney())
            currency.setIsDiscount(self.__isDiscount)
            vm.setFreeBunksCount(freeBunksCount)
            vm.setAllBunksCount(allBunksCount)

    def __prepareBerthInfo(self):
        berths = self.itemsCache.items.stats.tankmenBerthsCount
        self.__berthPrice, self.__berthsInPack = self.itemsCache.items.shop.getTankmanBerthPrice(berths)
        self.__defaultBerthPrice, _ = self.itemsCache.items.shop.defaults.getTankmanBerthPrice(berths)
        self.__isDiscount = self.__berthPrice != self.__defaultBerthPrice
        self.__pricePacksBerths = self.__berthPrice * self.__countPacksBerths
        self.__berthCurrency = self.__berthPrice.getCurrency()

    def __getCountSlotsAndFreeBerths(self):
        tankmenInBarracks = self.itemsCache.items.tankmenInBarracksCount()
        slotsCount = self.itemsCache.items.stats.tankmenBerthsCount
        freeBerthsCount = max(slotsCount - tankmenInBarracks, 0)
        return (slotsCount, freeBerthsCount)

    @args2params(int)
    def __onBunksCountChange(self, selectedCount):
        berths = self.itemsCache.items.stats.tankmenBerthsCount
        self.__countPacksBerths = getBerthPackCount(self.__berthsInPack, selectedCount)
        self.__pricePacksBerths = self.itemsCache.items.shop.getTankmanBerthPrice(berths, selectedCount)[0]
        with self.viewModel.transaction() as vm:
            vm.currency.setValue(self.__pricePacksBerths.get(self.__berthCurrency))
            vm.currency.setIsEnough(self.__isEnoughMoney())

    def __onCacheResync(self, reason, _):
        if reason != CACHE_SYNC_REASON.SHOP_RESYNC:
            return
        self.__prepareBerthInfo()
        if self.__isDiscount != self.viewModel.currency.getIsDiscount():
            with self.viewModel.transaction() as vm:
                currency = vm.currency
                currency.setType(CurrencyType(self.__berthCurrency))
                currency.setValue(self.__pricePacksBerths.get(self.__berthCurrency))
                currency.setIsEnough(self.__isEnoughMoney())
                currency.setIsDiscount(self.__isDiscount)

    def __isEnoughMoney(self):
        money = int(self.itemsCache.items.stats.money.getSignValue(self.__berthCurrency))
        return self.__pricePacksBerths.get(self.__berthCurrency) <= money
