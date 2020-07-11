# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew_books/crew_books_buy_dialog.py
import logging
import adisp
from async import async, await, AsyncEvent, AsyncReturn, AsyncScope, BrokenPromiseError
from frameworks.wulf import Window, WindowStatus, WindowSettings, ViewSettings
from gui import SystemMessages, DialogsInterface
from gui.Scaleform.daapi.view.dialogs.ExchangeDialogMeta import ExchangeCreditsSingleItemModalMeta
from gui.shared.view_helpers.blur_manager import CachedBlur
from gui.Scaleform.genConsts.APP_CONTAINERS_NAMES import APP_CONTAINERS_NAMES
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew_books.crew_books_buy_dialog_model import CrewBooksBuyDialogModel
from gui.impl.lobby.dialogs.contents.common_balance_content import CommonBalanceContent
from gui.impl.pub.dialog_window import DialogButtons, DialogLayer, DialogContent, DialogResult
from gui.impl.wrappers.user_format_string_arg_model import UserFormatStringArgModel
from gui.shared.formatters.tankmen import getItemPricesViewModel
from gui.shared.gui_items.Vehicle import getIconResourceName
from gui.shared.gui_items.processors.module import ModuleBuyer
from gui.shared.money import Currency
from gui.shared.utils.decorators import process
from helpers.dependency import descriptor
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class CrewBooksBuyDialog(Window):
    __itemsCache = descriptor(IItemsCache)
    __gui = descriptor(IGuiLoader)
    __slots__ = ('__blur', '__scope', '__event', '__result', '__bookGuiItem', '__bookCount')

    def __init__(self, parent, crewBookCD):
        settings = WindowSettings()
        settings.flags = DialogLayer.TOP_WINDOW
        settings.content = DialogContent(ViewSettings(R.views.lobby.crew_books.crew_books_buy_dialog.CrewBooksBuyDialog(), model=CrewBooksBuyDialogModel()))
        settings.parent = parent
        super(CrewBooksBuyDialog, self).__init__(settings)
        self.__bookGuiItem = self.__itemsCache.items.getItemByCD(crewBookCD)
        blurLayers = [APP_CONTAINERS_NAMES.VIEWS,
         APP_CONTAINERS_NAMES.SUBVIEW,
         APP_CONTAINERS_NAMES.BROWSER,
         APP_CONTAINERS_NAMES.WINDOWS]
        self.__blur = CachedBlur(enabled=True, ownLayer=APP_CONTAINERS_NAMES.DIALOGS, layers=blurLayers)
        self.__bookCount = 1
        self.__scope = AsyncScope()
        self.__event = AsyncEvent(scope=self.__scope)
        self.__result = None
        return

    @property
    def viewModel(self):
        return self.content.getViewModel()

    @async
    def wait(self):
        try:
            yield await(self.__event.wait())
        except BrokenPromiseError:
            _logger.debug('%s has been destroyed without user decision', self)

        raise AsyncReturn(DialogResult(self.__result, None))
        return

    def _initialize(self, *args, **kwargs):
        super(CrewBooksBuyDialog, self)._initialize()
        self.content.setChildView(R.dynamic_ids.crew_books_buy_dialog.balance_content(), CommonBalanceContent())
        with self.viewModel.transaction() as vm:
            vm.setDialogTitle(backport.text(R.strings.crew_books.buy.confirmation.dyn(self.__bookGuiItem.getBookType()).title(), nation=backport.text(R.strings.nations.dyn(self.__bookGuiItem.getNation())())))
            vm.setBookIcon(R.images.gui.maps.icons.crewBooks.books.large.dyn(getIconResourceName(self.__bookGuiItem.icon))())
            vm.setBookTitle(self.__bookGuiItem.getName())
            bookDescriptionFmtArgs = vm.getBookDescriptionFmtArgs()
            bookDescriptionFmtArgs.addViewModel(UserFormatStringArgModel(self.__gui.systemLocale.getNumberFormat(self.__bookGuiItem.getXP()), 'exp', R.styles.HighlightTextStyle()))
            vm.setBookDescription(R.strings.crew_books.screen.bookType.dyn(self.__bookGuiItem.getBookSpread()).info.title())
            bookDescriptionFmtArgs.invalidate()
            self.__updateVMsInActionPriceList()
        self.__addListeners()

    def _finalize(self):
        self.__removeListeners()
        self.__bookGuiItem = None
        self.__bookCount = None
        super(CrewBooksBuyDialog, self)._finalize()
        self.__blur.fini()
        self.__scope.destroy()
        return

    @property
    def purchasePrice(self):
        return self.__bookGuiItem.buyPrices.itemPrice * self.__bookCount

    def __addListeners(self):
        self.viewModel.onBuyBtnClick += self.__onBuyBtnClick
        self.viewModel.onClosed += self.__onClosed
        self.viewModel.onStepperChanged += self.__onStepperChanged

    def __removeListeners(self):
        self.viewModel.onBuyBtnClick -= self.__onBuyBtnClick
        self.viewModel.onClosed -= self.__onClosed
        self.viewModel.onStepperChanged -= self.__onStepperChanged

    def __onStepperChanged(self, args):
        self.__bookCount = int(args['count'])
        self.__updateVMsInActionPriceList()

    def __updateVMsInActionPriceList(self):
        listArray = self.viewModel.bookPrice.getItems()
        listArray.clear()
        items = self.__itemsCache.items
        money = items.stats.money
        actionPriceModels = getItemPricesViewModel(money, self.purchasePrice, exchangeRate=items.shop.exchangeRate)[0]
        priceVM = next((model for model in actionPriceModels if model.getType() == Currency.CREDITS))
        priceVM.setFontNotEnoughIsEnabled(True)
        listArray.addViewModel(priceVM)
        self.viewModel.setIsBuyEnable(priceVM.getIsEnough())
        listArray.invalidate()

    @adisp.process
    def __onBuyBtnClick(self):
        self.viewModel.setIsBuyEnable(False)
        mayPurchase = True
        playerMoney = self.__itemsCache.items.stats.money
        requiredCurrency = self.__bookGuiItem.buyPrices.itemPrice.getCurrency()
        if requiredCurrency == Currency.CREDITS:
            if playerMoney.get(requiredCurrency) < self.purchasePrice.price.get(requiredCurrency):
                mayPurchase, _ = yield DialogsInterface.showDialog(ExchangeCreditsSingleItemModalMeta(self.__bookGuiItem.intCD, count=self.__bookCount))
        if mayPurchase:
            self.__executeBuy(requiredCurrency)
        if self.windowStatus != WindowStatus.LOADED:
            return
        self.__updateVMsInActionPriceList()

    @process('buyItem')
    def __executeBuy(self, requiredCurrency):
        result = yield ModuleBuyer(self.__bookGuiItem, self.__bookCount, requiredCurrency).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        if result.success:
            if self.windowStatus != WindowStatus.LOADED:
                return
            self.__result = DialogButtons.SUBMIT
            self.viewModel.setBuyComplete(True)

    def __onClosed(self, _=None):
        if self.__result is None:
            self.__result = DialogButtons.CANCEL
        self.__event.set()
        return
