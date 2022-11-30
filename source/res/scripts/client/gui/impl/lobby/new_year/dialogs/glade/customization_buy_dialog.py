# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/dialogs/glade/customization_buy_dialog.py
from frameworks.wulf import ViewSettings, WindowLayer
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.game_control.wallet import WalletController
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.dialogs.glade.customization_buy_dialog_model import CustomizationBuyDialogModel
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogBaseView
from gui.impl.pub.dialog_window import DialogButtons
from gui.shared.money import Currency
from helpers import dependency
from helpers import time_utils
from helpers.time_utils import ONE_DAY
from new_year.ny_buy_toy_helper import getToyPricesConfig
from new_year.ny_level_helper import getNYGeneralConfig
from new_year.ny_toy_info import NewYearCurrentToyInfo
from skeletons.gui.game_control import IWalletController
from skeletons.gui.shared import IItemsCache
from uilogging.ny.loggers import NyDogCustomizationLogger
_SHOW_HIDE_CONTAINERS = (WindowLayer.VIEW,)
_HIDE_DURATION = _SHOW_DURATION = 0.3

class CustomizationBuyDialogView(FullScreenDialogBaseView):
    __slots__ = ('__toyID',)
    _itemsCache = dependency.descriptor(IItemsCache)
    __wallet = dependency.descriptor(IWalletController)

    def __init__(self, toyID, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.dialogs.glade.CustomizationBuyDialog())
        settings.args = args
        settings.kwargs = kwargs
        settings.model = CustomizationBuyDialogModel()
        self.__toyID = toyID
        super(CustomizationBuyDialogView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(CustomizationBuyDialogView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(CustomizationBuyDialogView, self)._onLoading(args, kwargs)
        g_clientUpdateManager.addMoneyCallback(self._updateStatus)
        toyPrices = getToyPricesConfig()
        toy = NewYearCurrentToyInfo(self.__toyID)
        price = toyPrices.getToyPrice(self.__toyID, {}).get(Currency.GOLD, 0)
        with self.viewModel.transaction() as model:
            model.setPrice(price)
            model.setToyIcon(toy.getIcon(size='large'))
            model.setToyName(toy.getName())
        self._updateStatus()

    def _updateStatus(self, *_):
        toyPrices = getToyPricesConfig()
        totalGold = self._itemsCache.items.stats.money.get(Currency.GOLD)
        generalConfig = getNYGeneralConfig()
        eventEndTimeTill = generalConfig.getEventEndTime() - time_utils.getServerUTCTime()
        price = toyPrices.getToyPrice(self.__toyID, {}).get(Currency.GOLD, 0)
        currencyStatus = self.__wallet.componentsStatuses.get(Currency.GOLD)
        currencyEnable = currencyStatus == WalletController.STATUS.AVAILABLE
        enoughMoney = price <= totalGold
        isWalletError = self.__wallet.isNotAvailable
        with self.viewModel.transaction() as model:
            model.setEventTimeLeft(int(eventEndTimeTill / ONE_DAY))
            model.setTotalCurrency(int(totalGold))
            model.setEnoughMoney(enoughMoney)
            model.setCanBuy(currencyEnable and enoughMoney and not isWalletError)
            model.setIsError(isWalletError)

    def _onLoaded(self, *args, **kwargs):
        self.__changeLayersVisibiliy(True)

    def _finalize(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__changeLayersVisibiliy(False)
        super(CustomizationBuyDialogView, self)._finalize()

    def __changeLayersVisibiliy(self, isHide):
        from skeletons.gui.app_loader import IAppLoader
        appLoader = dependency.instance(IAppLoader)
        lobby = appLoader.getDefLobbyApp()
        if lobby:
            if isHide:
                lobby.containerManager.hideContainers(_SHOW_HIDE_CONTAINERS, time=_HIDE_DURATION)
            else:
                lobby.containerManager.showContainers(_SHOW_HIDE_CONTAINERS, time=_SHOW_DURATION)

    def _getEvents(self):
        return ((self.viewModel.onAccept, self._onAccept), (self.viewModel.onCancel, self._onCancel), (self.__wallet.onWalletStatusChanged, self._updateStatus))

    def _onAccept(self):
        NyDogCustomizationLogger().logClick(self.__toyID, 'confirmed')
        self._setResult(DialogButtons.SUBMIT)

    def _onCancel(self):
        NyDogCustomizationLogger().logClick(self.__toyID, 'canceled')
        self._setResult(DialogButtons.CANCEL)
