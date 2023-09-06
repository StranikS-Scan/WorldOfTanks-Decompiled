# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/currency_reserves/currency_reserves_view.py
import logging
import typing
from constants import PremiumConfigs, PREMIUM_TYPE, RENEWABLE_SUBSCRIPTION_CONFIG
from frameworks.wulf import ViewFlags, ViewSettings
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getWotPlusShopUrl, getBuyPremiumUrl
from gui.impl.gen.view_models.views.lobby.currency_reserves.currency_reserve_model import CurrencyEnum
from gui.impl.gen.view_models.views.lobby.currency_reserves.currency_reserves_view_model import CurrencyReservesViewModel
from gui.impl.lobby.premacc.premacc_helpers import PiggyBankConstants, getDeltaTimeHelper
from gui.impl.pub import ViewImpl
from gui.shared.event_dispatcher import showWotPlusInfoPage, showTankPremiumAboutPage, showShop, showSteamRedirectWotPlus
from helpers import dependency
from skeletons.gui.game_control import IGameSessionController, IWotPlusController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from uilogging.wot_plus.logging_constants import WotPlusInfoPageSource, ReservesKeys
from uilogging.wot_plus.loggers import WotPlusReservesLogger
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from typing import Dict, Any

class CurrencyReservesView(ViewImpl):
    _itemsCache = dependency.descriptor(IItemsCache)
    _gameSession = dependency.descriptor(IGameSessionController)
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _wotPlusCtrl = dependency.descriptor(IWotPlusController)
    __slots__ = ('_creditReserveInfo', '_creditReserveConfig', '_serverSettings', '_wotPlusUILogger')

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
        settings.model = CurrencyReservesViewModel()
        self._creditReserveInfo = self._itemsCache.items.stats.piggyBank
        self._creditReserveConfig = self._lobbyContext.getServerSettings().getPiggyBankConfig()
        self._serverSettings = self._lobbyContext.getServerSettings()
        self._wotPlusUILogger = WotPlusReservesLogger()
        super(CurrencyReservesView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(CurrencyReservesView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        self.viewModel.onClose += self._onClose
        self._gameSession.onPremiumNotify += self._onPremiumNotify
        self._lobbyContext.getServerSettings().onServerSettingsChange += self._onServerSettingsChange
        self._wotPlusCtrl.onDataChanged += self._onWotPlusDataChanged
        self.viewModel.goldReserve.onInfoButtonClick += self._onGoldReserveInfoButtonClick
        self.viewModel.goldReserve.onActionButtonClick += self._onGoldReserveActionButtonClick
        self.viewModel.creditReserve.onInfoButtonClick += self._onCreditReserveInfoButtonClick
        self.viewModel.creditReserve.onActionButtonClick += self._onCreditReserveActionButtonClick
        g_clientUpdateManager.addCallbacks({PiggyBankConstants.PIGGY_BANK: self._onPiggyBankChanged})
        self._wotPlusUILogger.onViewInitialize()

    def _finalize(self):
        self.viewModel.onClose -= self._onClose
        self._gameSession.onPremiumNotify -= self._onPremiumNotify
        self._lobbyContext.getServerSettings().onServerSettingsChange -= self._onServerSettingsChange
        self._wotPlusCtrl.onDataChanged -= self._onWotPlusDataChanged
        self.viewModel.goldReserve.onInfoButtonClick -= self._onGoldReserveInfoButtonClick
        self.viewModel.goldReserve.onActionButtonClick -= self._onGoldReserveActionButtonClick
        self.viewModel.creditReserve.onInfoButtonClick -= self._onCreditReserveInfoButtonClick
        self.viewModel.creditReserve.onActionButtonClick -= self._onCreditReserveActionButtonClick
        g_clientUpdateManager.removeObjectCallbacks(self)
        self._wotPlusUILogger.onViewFinalize()

    def _onPremiumNotify(self, *args):
        self._updateCreditReserve()

    def _onLoading(self, highlightedComponentId=-1, makeTopView=False):
        logging.debug('CurrencyReserves::_onLoading')
        self._updateGoldReserve()
        self._updateCreditReserve()
        self._updateTimeToOpen()

    def _onPiggyBankChanged(self, *args):
        self._updateCreditReserve()
        self._updateTimeToOpen()

    def _updateTimeToOpen(self):
        timeToOpen = getDeltaTimeHelper(self._creditReserveConfig, self._creditReserveInfo)
        self.viewModel.setTimeToOpen(timeToOpen)

    def _updateCreditReserve(self):
        with self.viewModel.creditReserve.transaction() as creditReserve:
            creditReserve.setIsEnabled(self._creditReserveConfig.get('enabled'))
            creditReserve.setIsActive(self._isPremiumPlusActive())
            creditReserve.setCurrency(CurrencyEnum.CREDITS)
            creditReserve.setAmount(self._creditReserveInfo.get('credits', 0))
            creditReserve.setMaxCapacity(self._creditReserveConfig.get('creditsThreshold', 0))

    def _updateGoldReserve(self):
        with self.viewModel.goldReserve.transaction() as goldReserve:
            goldReserve.setIsEnabled(self._serverSettings.isRenewableSubGoldReserveEnabled())
            goldReserve.setIsActive(self._wotPlusCtrl.isEnabled())
            goldReserve.setCurrency(CurrencyEnum.GOLD)
            goldReserve.setAmount(self._wotPlusCtrl.getGoldReserve())
            goldReserve.setMaxCapacity(self._serverSettings.getRenewableSubMaxGoldReserveCapacity())

    def _onServerSettingsChange(self, diff):
        if RENEWABLE_SUBSCRIPTION_CONFIG in diff:
            self._updateGoldReserve()
        if PremiumConfigs.PIGGYBANK in diff:
            self._updateCreditReserve()
            self._updateTimeToOpen()

    def _onWotPlusDataChanged(self, data):
        if 'isEnabled' in data or 'piggyBank' in data:
            self._updateGoldReserve()

    def _onClose(self):
        self._wotPlusUILogger.logCloseEvent()
        self.destroyWindow()

    def _isPremiumPlusActive(self):
        return self._itemsCache.items.stats.isActivePremium(PREMIUM_TYPE.PLUS)

    def _onGoldReserveInfoButtonClick(self):
        showWotPlusInfoPage(WotPlusInfoPageSource.GOLD_RESERVES, includeSubscriptionInfo=True)

    def _onGoldReserveActionButtonClick(self):
        self._wotPlusUILogger.logClickEvent(ReservesKeys.GOLD_ACTIVATE)
        if self._wotPlusCtrl.isWotPlusEnabled():
            showShop(getWotPlusShopUrl())
        else:
            showSteamRedirectWotPlus()

    def _onCreditReserveInfoButtonClick(self):
        self._wotPlusUILogger.logClickEvent(ReservesKeys.CREDITS_INFO)
        showTankPremiumAboutPage()

    def _onCreditReserveActionButtonClick(self):
        self._wotPlusUILogger.logClickEvent(ReservesKeys.CREDITS_ACTIVATE)
        showShop(getBuyPremiumUrl())
