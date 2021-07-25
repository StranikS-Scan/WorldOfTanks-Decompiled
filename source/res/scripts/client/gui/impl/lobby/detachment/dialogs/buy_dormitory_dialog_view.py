# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/dialogs/buy_dormitory_dialog_view.py
from adisp import process
from frameworks.wulf import ViewSettings
from gui import DialogsInterface
from gui.Scaleform.daapi.view.dialogs.ExchangeDialogMeta import ExchangeCreditsWebProductMeta
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.buy_dormitory_dialog_model import BuyDormitoryDialogModel
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogView
from gui.shared import event_dispatcher as shared_events
from gui.shared.money import Currency, Money
from gui.shop import showBuyGoldForDormitory
from gui.sounds.filters import switchHangarOverlaySoundFilter
from helpers import dependency
from items.components.dormitory_constants import DormitorySections, BuyDormitoryReason
from skeletons.gui.shared import IItemsCache
from uilogging.detachment.loggers import DetachmentLogger
from uilogging.detachment.constants import ACTION, GROUP

class BuyDormitoryDialogView(FullScreenDialogView):
    __slots__ = ('_reason', '_countBlocks')
    __itemsCache = dependency.descriptor(IItemsCache)
    uiLogger = DetachmentLogger(GROUP.BUY_DORMITORY_DIALOG)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.detachment.dialogs.BuyDormitoryDialogView())
        settings.model = BuyDormitoryDialogModel()
        self._reason = kwargs.get('reason', BuyDormitoryReason.GENERAL_BUY)
        self._countBlocks = kwargs.get('countBlocks', 1)
        super(BuyDormitoryDialogView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    @property
    def shortage(self):
        shortage = self._stats.money.getShortage(Money.makeFrom(self.currency, self.price))
        return shortage.get(self.currency)

    @property
    def shortageDef(self):
        shortage = self._stats.money.getShortage(Money.makeFrom(self.currency, self.defPrice))
        return shortage.get(self.currency)

    @property
    def currency(self):
        return self.__getDormPrice()[DormitorySections.CURRENCY]

    @property
    def price(self):
        return self.__getDormPrice()[DormitorySections.PRICE] * self._countBlocks

    @property
    def defPrice(self):
        return self.__getDefaultDormPrice()[DormitorySections.PRICE] * self._countBlocks

    @property
    def isBuyingEnabled(self):
        return self.__itemsCache.items.shop.getDormitoryBuyingSettings

    @property
    def isDiscount(self):
        return self.defPrice > self.price

    @property
    def discountPercent(self):
        return max(0, 100 - int(self.price * 100.0 / self.defPrice))

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId == TOOLTIPS_CONSTANTS.NOT_ENOUGH_MONEY and self.isBuyingEnabled:
                specialArgs = (self.shortage, self.currency)
                return self.__getBackportTooltipWindow(tooltipId, specialArgs)
            if tooltipId == BuyDormitoryDialogModel.PRICE_TOOLTIP:
                if bool(self.shortage) and not self.isDiscount:
                    specialArgs = (self.shortage, self.currency)
                    return self.__getBackportTooltipWindow(TOOLTIPS_CONSTANTS.NOT_ENOUGH_MONEY, specialArgs)
                if self.isDiscount:
                    specialArgs = (self.price,
                     self.defPrice,
                     self.currency,
                     not bool(self.shortage),
                     not bool(self.shortageDef))
                    return self.__getBackportTooltipWindow(TOOLTIPS_CONSTANTS.PRICE_DISCOUNT, specialArgs)
        return super(BuyDormitoryDialogView, self).createToolTip(event)

    def _addListeners(self):
        super(BuyDormitoryDialogView, self)._addListeners()
        self.__itemsCache.onSyncCompleted += self.__onItemCacheSyncCompleted

    def _removeListeners(self):
        self.__itemsCache.onSyncCompleted -= self.__onItemCacheSyncCompleted
        super(BuyDormitoryDialogView, self)._removeListeners()

    def _setBaseParams(self, model):
        self.__fillViewModel()
        super(BuyDormitoryDialogView, self)._setBaseParams(model)

    def _initialize(self):
        super(BuyDormitoryDialogView, self)._initialize()
        switchHangarOverlaySoundFilter(on=True)

    def _finalize(self):
        super(BuyDormitoryDialogView, self)._finalize()
        switchHangarOverlaySoundFilter(on=False)

    def _onAcceptClicked(self):
        if self.shortage:
            if self.currency == Currency.GOLD:
                self.uiLogger.log(ACTION.BUY_GOLD)
                showBuyGoldForDormitory(self.price)
            elif self.currency == Currency.CREDITS:
                self.uiLogger.log(ACTION.CONVERT_GOLD_TO_CREDITS)
                self._showExchangeDialog()
        else:
            self.uiLogger.log(ACTION.DIALOG_CONFIRM)
            self._onAccept()

    def _onExitClicked(self):
        self.uiLogger.log(ACTION.DIALOG_EXIT)
        super(BuyDormitoryDialogView, self)._onExitClicked()

    def _onCancelClicked(self):
        self.uiLogger.log(ACTION.DIALOG_CANCEL)
        super(BuyDormitoryDialogView, self)._onCancelClicked()

    @process
    def _showExchangeDialog(self):
        yield DialogsInterface.showDialog(ExchangeCreditsWebProductMeta(name=backport.text(R.strings.dialogs.confirmExchangeDialog.exchangeCredits.title()), count=1, price=self.price))

    def __getDormRoomsCount(self):
        return self.__itemsCache.items.shop.getDormitoryRoomsCount * self._countBlocks

    def __getDormPrice(self):
        return self.__itemsCache.items.shop.getDormitoryPrice

    def __getDefaultDormPrice(self):
        return self.__itemsCache.items.shop.defaults.getDormitoryPrice

    def __onItemCacheSyncCompleted(self, reason, diff):
        self.__fillViewModel()

    def __fillViewModel(self):
        with self.viewModel.transaction() as viewModel:
            viewModel.setNewDormRooms(self.__getDormRoomsCount())
            viewModel.setAcceptButtonText(R.strings.dialogs.detachment.buyDormitory.button.submit())
            viewModel.setCancelButtonText(R.strings.dialogs.detachment.buyDormitory.button.cancel())
            viewModel.setTitleBody(R.strings.dialogs.detachment.buyDormitory.title())
            viewModel.setWarningText(self.__getReasonLocalID())
            viewModel.setIsBuyingEnabled(self.isBuyingEnabled)
            viewModel.setIsAcceptDisabled(self.__disabledAccept())
            viewModel.priceModel.setType(self.currency)
            viewModel.priceModel.setValue(self.price)
            if self.isDiscount:
                viewModel.priceModel.setDiscountValue(self.discountPercent)
            viewModel.priceModel.setHasDiscount(self.isDiscount)
            viewModel.priceModel.setIsEnough(not bool(self.shortage))

    def __disabledAccept(self):
        if not self.isBuyingEnabled:
            return True
        if self.currency == Currency.CREDITS and self.shortage:
            return not self.__checkEnoughGoldForExchangeToCredits()
        return False if self.currency == Currency.GOLD else bool(self.shortage)

    def __checkEnoughGoldForExchangeToCredits(self):
        money = Money.makeFrom(self.currency, self.price)
        return False if not shared_events.mayObtainWithMoneyExchange(money, itemsCache=self.__itemsCache) else True

    def __getReasonLocalID(self):
        reason = self._reason
        if reason == BuyDormitoryReason.RECRUIT_NEW_DETACHMENT:
            return R.strings.dialogs.detachment.buyDormitory.warning.recruit()
        return R.strings.dialogs.detachment.buyDormitory.warning.recover() if reason == BuyDormitoryReason.RECOVER_DETACHMENT else R.invalid()

    def __getBackportTooltipWindow(self, tooltipId, specialArgs):
        tooltipData = backport.createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=specialArgs)
        window = backport.BackportTooltipWindow(tooltipData, self.getParentWindow())
        window.load()
        return window
