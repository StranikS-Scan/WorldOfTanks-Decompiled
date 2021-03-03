# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/bm2021/dialogs/black_market_next_open_confirm_dialog.py
from async import await, async
from constants import Configs
from frameworks.wulf import ViewSettings
from gui.impl.dialogs.dialogs import showSingleDialogWithResultData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.bm2021.dialogs.black_market_next_open_confirm_dialog_model import BlackMarketNextOpenConfirmDialogModel
from gui.impl.lobby.bm2021.dialogs.black_market_exchange_currency import BlackMarketExchangeCurrency
from gui.impl.lobby.bm2021.sound import BLACK_MARKET_OVERLAY_SOUND_SPACE
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogView
from gui.shared.event_dispatcher import showBlackMarketVehicleListWindow
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.gui_items.loot_box import BLACK_MARKET_ITEM_TYPE
from gui.shared.money import Money, Currency
from helpers import dependency
from skeletons.gui.game_control import IEventItemsController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache

class BlackMarketNextOpenConfirmDialog(FullScreenDialogView):
    __slots__ = ('__endDate', '__nextOpenPrice', '__slotsNumber', '__nextOpenPriceType', '__restoreCb')
    _COMMON_SOUND_SPACE = BLACK_MARKET_OVERLAY_SOUND_SPACE
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __eventItemsCtrl = dependency.descriptor(IEventItemsController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, endDate, nextOpenPrice, nextOpenPriceType, slotsNumber, restoreCb=None):
        settings = ViewSettings(R.views.lobby.bm2021.dialogs.ConfirmNextOpen())
        settings.model = BlackMarketNextOpenConfirmDialogModel()
        super(BlackMarketNextOpenConfirmDialog, self).__init__(settings)
        self.__endDate = endDate
        self.__nextOpenPrice = nextOpenPrice
        self.__slotsNumber = slotsNumber
        self.__nextOpenPriceType = nextOpenPriceType
        self.__restoreCb = restoreCb

    @property
    def viewModel(self):
        return super(BlackMarketNextOpenConfirmDialog, self).getViewModel()

    def _finalize(self):
        self.__restoreCb = None
        super(BlackMarketNextOpenConfirmDialog, self)._finalize()
        return

    def _setBaseParams(self, model):
        model.setEndDate(self.__endDate)
        model.setSlotsNumber(self.__slotsNumber)
        model.setNextOpenPrice(self.__nextOpenPrice)
        self.__setStats(model.stats)

    def _addListeners(self):
        self.viewModel.onConfirm += self._onAccept
        self.viewModel.onOpenExchange += self.__onOpenExchange
        self.viewModel.onOpenVehicleList += self.__onOpenVehicleList
        self.__itemsCache.onSyncCompleted += self._onInventoryResync
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange

    def _removeListeners(self):
        self.viewModel.onConfirm -= self._onAccept
        self.viewModel.onOpenExchange -= self.__onOpenExchange
        self.viewModel.onOpenVehicleList -= self.__onOpenVehicleList
        self.__itemsCache.onSyncCompleted -= self._onInventoryResync
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange

    def _onInventoryResync(self, *args, **kwargs):
        with self.viewModel.stats.transaction() as model:
            self.__setStats(model)

    @async
    def __onOpenExchange(self):
        moneyArgs = {self.__nextOpenPriceType: self.__nextOpenPrice}
        result = yield await(showSingleDialogWithResultData(BlackMarketExchangeCurrency, R.views.lobby.bm2021.dialogs.BlackMarketExchangeCurrency(), price=ItemPrice(Money(**moneyArgs), Money(**moneyArgs)), layer=self.getParentWindow().layer + 1))
        if not result.busy and result.result[0]:
            self._onAccept()
        else:
            self.destroy()

    def __onOpenVehicleList(self):
        showBlackMarketVehicleListWindow(self.__restoreCb, self.getParentWindow())

    def __onServerSettingsChange(self, diff):
        if Configs.LOOT_BOXES_CONFIG.value in diff:
            item = self.__eventItemsCtrl.getOwnedItemsByType(BLACK_MARKET_ITEM_TYPE)
            if item is None or not diff[Configs.LOOT_BOXES_CONFIG.value].get(item.getID(), {}).get('enabled'):
                self.destroy()
        return

    def __setStats(self, model):
        model.setCredits(int(self._stats.money.getSignValue(Currency.CREDITS)))
        model.setGold(int(self._stats.money.getSignValue(Currency.GOLD)))
        model.setCrystal(int(self._stats.money.getSignValue(Currency.CRYSTAL)))
        model.setFreeXP(self._stats.freeXP)
        model.setExchangeRate(self.__itemsCache.items.shop.exchangeRate)
