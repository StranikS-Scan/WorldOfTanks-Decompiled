# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/dialogs/crew_books_purchase_dialog.py
from base_crew_dialog_template_view import BaseCrewDialogTemplateView
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.customization.shared import getPurchaseGoldForCredits, getPurchaseMoneyState, MoneyForPurchase
from gui.impl import backport
from gui.impl.dialogs.dialog_template_button import CancelButton, ConfirmButton
from gui.impl.dialogs.sub_views.icon.icon_set import IconSet
from gui.impl.dialogs.sub_views.title.simple_text_title import SimpleTextTitle
from gui.impl.dialogs.sub_views.top_right.money_balance import MoneyBalance
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders as Placeholder
from gui.impl.gen.view_models.views.dialogs.sub_views.currency_view_model import CurrencyType, CurrencySize
from gui.impl.gen.view_models.views.lobby.crew.dialogs.crew_books_purchase_dialog_model import CrewBooksPurchaseDialogModel
from gui.impl.gui_decorators import args2params
from gui.impl.pub.dialog_window import DialogButtons
from gui.impl.pub.tooltip_window import SimpleTooltipContent
from gui.shared import event_dispatcher
from gui.shared.gui_items.processors.module import BookBuyer
from gui.shared.utils import decorators
from helpers import dependency
from skeletons.gui.shared import IItemsCache
INITIAL_BOOK_COUNT = 1

class CrewBooksPurchaseDialog(BaseCrewDialogTemplateView):
    __slots__ = ('_bookGuiItem', '_bookCount')
    LAYOUT_ID = R.views.lobby.crew.dialogs.CrewBooksPurchaseDialog()
    VIEW_MODEL = CrewBooksPurchaseDialogModel
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, crewBookCD):
        super(CrewBooksPurchaseDialog, self).__init__()
        self._bookGuiItem = self._itemsCache.items.getItemByCD(crewBookCD)
        self._bookCount = INITIAL_BOOK_COUNT

    @property
    def viewModel(self):
        return self.getViewModel()

    @property
    def purchasePrice(self):
        return self._bookGuiItem.buyPrices.itemPrice * self._bookCount

    def _initialize(self, *args, **kwargs):
        super(CrewBooksPurchaseDialog, self)._initialize(*args, **kwargs)
        self.viewModel.onStepperChanged += self._onStepperChanged

    def _finalize(self):
        self.viewModel.onStepperChanged -= self._onStepperChanged
        self._removeListener()
        self._bookGuiItem = None
        self._bookCount = None
        super(CrewBooksPurchaseDialog, self)._finalize()
        return

    def _onLoading(self, *args, **kwargs):
        self.setBackgroundImagePath(R.images.gui.maps.icons.crewBooks.screen_bg())
        self.setSubView(Placeholder.TOP_RIGHT, MoneyBalance())
        self.setSubView(Placeholder.ICON, IconSet(R.images.gui.maps.icons.crewBooks.books.large.dyn(self._bookGuiItem.icon)()))
        self.addButton(ConfirmButton(R.strings.dialogs.crewBookPurchase.purchase(), isDisabled=False, tooltipFactory=self._getToolTipBuilder()))
        self.addButton(CancelButton())
        self._updateViewModel()
        self._addListener()
        super(CrewBooksPurchaseDialog, self)._onLoading(*args, **kwargs)

    def _addListener(self):
        g_clientUpdateManager.addMoneyCallback(self.__onMoneyUpdated)

    def _removeListener(self):
        g_clientUpdateManager.removeObjectCallbacks(self)

    def _setTitle(self, book):
        bookNation = self._bookGuiItem.getNation()
        bookType = book.getBookType()
        if bookNation:
            nationText = backport.text(R.strings.nations.dyn(bookNation)())
            titleText = backport.text(R.strings.crew_books.items.dyn(bookType).Name(), nation=nationText)
        else:
            titleText = backport.text(R.strings.crew_books.items.dyn(bookType).Name())
        result = str(backport.text(R.strings.dialogs.crewBookPurchase.purchase.title(), book=titleText))
        self.setSubView(Placeholder.TITLE, SimpleTextTitle(result))

    def _getToolTipBuilder(self):
        return SimpleTooltipContent(body=backport.text(R.strings.dialogs.crewBookPurchase.btnDisabledTooltip()))

    @args2params(int)
    def _onStepperChanged(self, quantity):
        self._bookCount = quantity
        self._updatePrice()

    def __onMoneyUpdated(self, _):
        self._updatePrice()

    def _updateViewModel(self):
        with self.viewModel.transaction() as vm:
            self._fillViewModel(vm)

    def _updatePrice(self):
        with self.viewModel.transaction() as vm:
            self._setBookPrice(vm)

    def _fillViewModel(self, vm):
        self._setBookPrice(vm)
        self._setTitle(self._bookGuiItem)
        bookNameRoot = R.strings.crew_books.items.dyn(self._bookGuiItem.getBookType())
        bookName = str(backport.text(bookNameRoot.noNationName() if self._bookGuiItem.getNation() else bookNameRoot.Name()))
        vm.setBookName(bookName)
        vm.setIsBookPersonal(self._bookGuiItem.isPersonal())
        vm.setExperience(self._bookGuiItem.getXP())

    def _setBookPrice(self, vm):
        currency = self._bookGuiItem.buyPrices.itemPrice.getCurrency()
        money = self.purchasePrice.price.getSignValue(currency)
        state = getPurchaseMoneyState(self.purchasePrice.price)
        vm.bookPrice.setValue(money)
        vm.bookPrice.setIsEnough(state is MoneyForPurchase.ENOUGH)
        btnDisable = state is MoneyForPurchase.NOT_ENOUGH
        submitBtn = self.getButton(DialogButtons.SUBMIT)
        submitBtn.isDisabled = btnDisable
        submitBtn.tooltipFactory = self._getToolTipBuilder() if btnDisable else None
        vm.bookPrice.setType(CurrencyType(currency))
        vm.bookPrice.setSize(CurrencySize.BIG)
        return

    def _setResult(self, result):
        if result == DialogButtons.SUBMIT:
            if not self._buyBook():
                return
        super(CrewBooksPurchaseDialog, self)._setResult(result)

    def _buyBook(self):
        purchaseMoneyState = getPurchaseMoneyState(self.purchasePrice.price)
        if purchaseMoneyState is MoneyForPurchase.ENOUGH_WITH_EXCHANGE:
            purchaseGold = getPurchaseGoldForCredits(self.purchasePrice.price)
            event_dispatcher.showExchangeCurrencyWindowModal(currencyValue=purchaseGold)
            return False
        self._executeBuy()
        return True

    @decorators.adisp_process('buyItem')
    def _executeBuy(self):
        currency = self._bookGuiItem.buyPrices.itemPrice.getCurrency()
        result = yield BookBuyer(self._bookGuiItem, self._bookCount, currency).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
