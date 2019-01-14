# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/pub/dialog_window.py
import logging
from functools import partial
from gui.Scaleform.genConsts.APP_CONTAINERS_NAMES import APP_CONTAINERS_NAMES
from shared_utils import CONST_CONTAINER
import BigWorld
from async import async, await, AsyncEvent, AsyncReturn, AsyncScope, BrokenPromiseError
from frameworks.wulf import Array, ViewFlags
from frameworks.wulf import WindowFlags, Window
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.gen import R
from gui.impl.gen.view_models.ui_kit.currency_item_model import CurrencyItemModel
from gui.impl.gen.view_models.ui_kit.dialog_button_model import DialogButtonModel
from gui.impl.gen.view_models.windows.dialog_window_model import DialogWindowModel
from gui.impl.pub.view_impl import ViewImpl
from gui.impl.wrappers.background_blur import WGUIBackgroundBlurSupportImpl
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.game_control import IWalletController
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class DialogShine(CONST_CONTAINER):
    NONE = 0
    NORMAL = R.images.gui.maps.uiKit.dialogs.greenShine()
    RED = R.images.gui.maps.uiKit.dialogs.redShine()
    YELLOW = R.images.gui.maps.uiKit.dialogs.yellowShine()


class DialogButtons(CONST_CONTAINER):
    SUBMIT = DialogButtonModel.BTN_SUBMIT
    CANCEL = DialogButtonModel.BTN_CANCEL
    PURCHASE = DialogButtonModel.BTN_PURCHASE
    RESEARCH = DialogButtonModel.BTN_RESEARCH
    ALL = (SUBMIT,
     CANCEL,
     PURCHASE,
     RESEARCH)


class DialogContent(ViewImpl):
    __slots__ = ()

    def __init__(self, layoutID, viewModelClazz, *args, **kwargs):
        super(DialogContent, self).__init__(layoutID, ViewFlags.VIEW, viewModelClazz, *args, **kwargs)


class DialogWindow(Window):
    __slots__ = ('__blur', '__scope', '__event', '__result', '__currencyAdapter', '__buttons')

    def __init__(self, content, bottomContent=None, parent=None, showCurrency=False, enableBlur=True):
        super(DialogWindow, self).__init__(wndFlags=WindowFlags.DIALOG | WindowFlags.RESIZABLE, decorator=ViewImpl(R.views.dialogWindow(), ViewFlags.WINDOW_DECORATOR, DialogWindowModel), content=content, parent=parent)
        if bottomContent is not None:
            self._setBottomContent(bottomContent)
        self.__blur = WGUIBackgroundBlurSupportImpl()
        self.__scope = AsyncScope()
        self.__event = AsyncEvent(scope=self.__scope)
        self.__result = DialogButtons.CANCEL
        self.__buttons = {}
        if enableBlur:
            self.__blur.enable(APP_CONTAINERS_NAMES.DIALOGS, [APP_CONTAINERS_NAMES.VIEWS,
             APP_CONTAINERS_NAMES.WINDOWS,
             APP_CONTAINERS_NAMES.SUBVIEW,
             APP_CONTAINERS_NAMES.BROWSER])
        self.__currencyAdapter = None
        if showCurrency:
            self.__currencyAdapter = DialogWindowCurrencyAdapter()
            self.viewModel.currency.setItems(self.__currencyAdapter.currencyModel)
        self.viewModel.setHasCurrencyBlock(showCurrency)
        return

    @async
    def wait(self):
        try:
            yield await(self.__event.wait())
        except BrokenPromiseError:
            _logger.debug('%s has been destroyed without user decision', self)

        raise AsyncReturn(self.__result)

    @property
    def viewModel(self):
        return self._getDecoratorViewModel()

    @property
    def contentViewModel(self):
        return self.viewModel.getContent().getViewModel()

    @property
    def bottomContentViewModel(self):
        return self.viewModel.getBottomContent().getViewModel()

    def _initialize(self):
        super(DialogWindow, self)._initialize()
        self.viewModel.onClosed += self._onClosed
        self.viewModel.buttons.onUserItemClicked += self._onButtonClick

    def _finalize(self):
        if self.__currencyAdapter is not None:
            self.__currencyAdapter.finalize()
        self.viewModel.onClosed -= self._onClosed
        self.viewModel.buttons.onUserItemClicked -= self._onButtonClick
        self.__buttons.clear()
        super(DialogWindow, self)._finalize()
        self.__scope.destroy()
        self.__blur.disable()
        return

    def _onClosed(self, _=None):
        self.destroy()

    def _removeAllButtons(self):
        self.viewModel.buttons.setItems([])

    def _addButton(self, name, label, isFocused=False):
        button = DialogButtonModel()
        button.setName(name)
        button.setLabel(label)
        button.setDoSetFocus(isFocused)
        self.__buttons[name] = button
        self.viewModel.buttons.addViewModel(button, isSelected=isFocused)

    def _getButton(self, name):
        return self.__buttons[name] if name in self.__buttons else None

    def _onButtonClick(self, item):
        self.__result = item.getName()
        self.__event.set()

    def _setBackgroundImage(self, value):
        self.viewModel.setBackgroundImage(value)

    def _setHasCloseButton(self, value):
        self.viewModel.setHasCloseBtn(value)

    def _setBottomContent(self, value):
        self.viewModel.setBottomContent(value)

    def _setBackgroundShine(self, value):
        self.viewModel.setBackgroundShineImage(value)


class CurrencyStatus(CONST_CONTAINER):
    IN_PROGRESS = 0
    NOT_AVAILABLE = 1
    AVAILABLE = 2


class DialogWindowCurrencyAdapter(object):
    itemsCache = dependency.descriptor(IItemsCache)
    wallet = dependency.descriptor(IWalletController)
    __slots__ = ('__stats', '__currencyModel', '__currencyIndexes', '__callbacks')
    __CURRENCY_FORMATTER = {Currency.CREDITS: BigWorld.wg_getIntegralFormat,
     Currency.GOLD: BigWorld.wg_getGoldFormat,
     Currency.CRYSTAL: BigWorld.wg_getIntegralFormat,
     'freeXP': BigWorld.wg_getIntegralFormat}

    def __init__(self):
        self.__currencyModel = Array()
        self.__currencyIndexes = []
        self.__callbacks = {}
        self.__stats = self.itemsCache.items.stats
        for currency in Currency.GUI_ALL:
            self.__addCurrency(currency, self.__getCurrencyFormatter(currency)(self.__stats.actualMoney.get(currency)))

        self.__addCurrency('freeXP', self.__getCurrencyFormatter('freeXP')(self.__stats.actualFreeXP))
        self.wallet.onWalletStatusChanged += self.__onWalletChanged

    def finalize(self):
        for currency, callback in self.__callbacks.iteritems():
            g_clientUpdateManager.removeCallback('stats.{}'.format(currency), callback)

        self.wallet.onWalletStatusChanged -= self.__onWalletChanged
        self.__callbacks.clear()

    @property
    def currencyModel(self):
        return self.__currencyModel

    def __addCurrency(self, currency, value):
        button = CurrencyItemModel()
        button.setCurrency(currency)
        button.setValue(value)
        self.currencyModel.addViewModel(button)
        self.__currencyIndexes.append(currency)
        callback = partial(self.__onCurrencyUpdated, currency)
        self.__callbacks[currency] = callback
        g_clientUpdateManager.addCallback('stats.{}'.format(currency), callback)

    def __getCurrencyFormatter(self, currency):
        return self.__CURRENCY_FORMATTER[currency] if currency in self.__CURRENCY_FORMATTER else BigWorld.wg_getIntegralFormat

    def __onCurrencyUpdated(self, currency, value):
        index = self.__currencyIndexes.index(currency)
        self.currencyModel[index].setValue(self.__getCurrencyFormatter(currency)(value) if value is not None else '')
        return

    def __onWalletChanged(self, status):
        for currency in Currency.GUI_ALL:
            self.__onCurrencyUpdated(currency, self.__stats.actualMoney.get(currency) if status[currency] == CurrencyStatus.AVAILABLE else None)

        self.__onCurrencyUpdated('freeXP', self.__stats.actualFreeXP if status['freeXP'] == CurrencyStatus.AVAILABLE else None)
        return
