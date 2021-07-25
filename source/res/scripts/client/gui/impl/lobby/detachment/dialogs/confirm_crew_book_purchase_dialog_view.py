# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/dialogs/confirm_crew_book_purchase_dialog_view.py
import logging
import nations
from async import await, async
from frameworks.wulf import ViewSettings
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.customization.shared import getPurchaseMoneyState, MoneyForPurchase
from gui.impl.backport.backport_tooltip import createBackportTooltipContent
from gui.impl.dialogs.dialogs import showConvertCurrencyForCrewBookView
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.dialogs.confirm_crew_book_purchase_dialog_view_model import ConfirmCrewBookPurchaseDialogViewModel
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogView
from gui.impl.pub.dialog_window import DialogButtons
from gui.shared.event_dispatcher import getLoadedView
from gui.shared.gui_items.processors.common import GoldToCreditsExchanger
from gui.shared.money import Currency
from gui.shared.utils import decorators
from helpers.dependency import descriptor
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)
_INITIAL_AMOUNT = 1
_MAX_AMOUNT = 20

class ConfirmCrewBookPurchaseDialogView(FullScreenDialogView):
    __itemsCache = descriptor(IItemsCache)
    __slots__ = ('_bookItem', '_bookCount')

    def __init__(self, ctx):
        settings = ViewSettings(R.views.lobby.detachment.dialogs.ConfirmCrewBookPurchaseDialogView())
        settings.model = ConfirmCrewBookPurchaseDialogViewModel()
        super(ConfirmCrewBookPurchaseDialogView, self).__init__(settings)
        bookCD = ctx.get('bookCD')
        self._bookItem = self.__itemsCache.items.getItemByCD(bookCD)
        self._bookCount = ctx.get('count', _INITIAL_AMOUNT)

    @property
    def viewModel(self):
        return super(ConfirmCrewBookPurchaseDialogView, self).getViewModel()

    @property
    def requiredCurrency(self):
        return self._bookItem.buyPrices.itemPrice.getCurrency()

    @property
    def totalPrice(self):
        price = self._bookItem.buyPrices.itemPrice.price
        return price * self._bookCount

    @property
    def shortage(self):
        return self.__itemsCache.items.stats.money.getShortage(self.totalPrice)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId == TOOLTIPS_CONSTANTS.NOT_ENOUGH_MONEY:
                currency = self.requiredCurrency
                money = self.__itemsCache.items.stats.money
                shortage = max(self.totalPrice.get(currency) - money.get(currency, 0), 0)
                return createBackportTooltipContent(TOOLTIPS_CONSTANTS.NOT_ENOUGH_MONEY, (shortage, currency))
        return super(ConfirmCrewBookPurchaseDialogView, self).createToolTipContent(event, contentID)

    def _addListeners(self):
        super(ConfirmCrewBookPurchaseDialogView, self)._addListeners()
        self.viewModel.onStepperChange += self._onStepperChange
        g_clientUpdateManager.addMoneyCallback(self._onMoneyUpdate)

    def _onAcceptClicked(self):
        moneyState = getPurchaseMoneyState(self.totalPrice)
        if moneyState == MoneyForPurchase.ENOUGH_WITH_EXCHANGE:
            self.__showExchangeDialog()
        elif moneyState == MoneyForPurchase.ENOUGH:
            self._onAccept()

    def _onCancel(self):
        exchangeView = getLoadedView(R.views.lobby.detachment.dialogs.ConvertCurrencyView())
        if exchangeView:
            exchangeView.destroy()
        super(ConfirmCrewBookPurchaseDialogView, self)._onCancel()

    def _removeListeners(self):
        self.viewModel.onStepperChange -= self._onStepperChange
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(ConfirmCrewBookPurchaseDialogView, self)._removeListeners()

    def _setBaseParams(self, model):
        self.__fillModel()
        self.__updateStepper()
        super(ConfirmCrewBookPurchaseDialogView, self)._setBaseParams(model)

    def _onMoneyUpdate(self, *args, **kwargs):
        self.__fillModel()
        self.__updateStepper()

    def _getAdditionalData(self):
        return {'bookCount': self._bookCount}

    def _onStepperChange(self, args=None):
        if args is None:
            _logger.error('Incorrect args.')
            return
        else:
            bookCount = int(args.get('value'))
            if bookCount > 0:
                self._bookCount = bookCount
                self.__updateStepper()
            return

    def __fillModel(self):
        with self.viewModel.transaction() as viewModel:
            viewModel.setNation(nations.MAP.get(self._bookItem.nationID, ''))
            viewModel.setCrewBookType(self._bookItem.getBookType())
            viewModel.setMaxValue(_MAX_AMOUNT)
            viewModel.priceModel.setType(self.requiredCurrency)
            viewModel.setTitleBody(R.strings.dialogs.detachment.confirmCrewBooksPurchase.title())
            viewModel.setAcceptButtonText(R.strings.detachment.common.buy())
            viewModel.setCancelButtonText(R.strings.detachment.common.cancel())

    def __updateStepper(self):
        moneyState = getPurchaseMoneyState(self.totalPrice)
        isEnoughCredits = not bool(self.shortage)
        with self.viewModel.transaction() as viewModel:
            viewModel.setSelectedValue(self._bookCount)
            viewModel.setAmountXP(self._bookCount * self._bookItem.getXP())
            viewModel.priceModel.setValue(self.totalPrice.get(self.requiredCurrency))
            viewModel.priceModel.setIsEnough(isEnoughCredits)
            maxCountToBuy = max(_INITIAL_AMOUNT, min(self.__maxAvailableItemsToBuy(), _MAX_AMOUNT))
            viewModel.setMaxValue(maxCountToBuy)
            viewModel.setIsAcceptDisabled(moneyState == MoneyForPurchase.NOT_ENOUGH)

    def __maxAvailableItemsToBuy(self):
        bookPrice = self._bookItem.buyPrices.itemPrice.price.get(Currency.CREDITS, default=0)
        money = self.__itemsCache.items.stats.money
        exchangeRate = self.__itemsCache.items.shop.exchangeRate
        exchagedMoney = money.exchange(Currency.GOLD, Currency.CREDITS, exchangeRate, default=0)
        possibleCredits = exchagedMoney.get(Currency.CREDITS, default=0)
        return possibleCredits // bookPrice

    @async
    def __showExchangeDialog(self):
        sdr = yield await(showConvertCurrencyForCrewBookView(ctx={'crewbookCD': self._bookItem.intCD,
         'needCredits': self.shortage.credits}))
        if sdr.busy:
            return
        isOk, data = sdr.result
        if isOk == DialogButtons.SUBMIT:
            self.__exchange(int(data['gold']))

    @decorators.process('transferMoney')
    def __exchange(self, gold):
        result = yield GoldToCreditsExchanger(gold, withConfirm=False).request()
        if result and result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        if result.success:
            self._onAccept()
