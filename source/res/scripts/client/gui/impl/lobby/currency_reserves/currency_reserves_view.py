# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/currency_reserves/currency_reserves_view.py
import logging
import typing
import BigWorld
from constants import PremiumConfigs, PREMIUM_TYPE, RENEWABLE_SUBSCRIPTION_CONFIG
from frameworks.wulf import ViewFlags, ViewSettings
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getBuyRenewableSubscriptionUrl, getBuyPremiumUrl
from gui.impl.gen.view_models.views.lobby.currency_reserves.currency_reserve_model import CurrencyEnum
from gui.impl.gen.view_models.views.lobby.currency_reserves.currency_reserves_view_model import CurrencyReservesViewModel
from gui.impl.lobby.premacc.premacc_helpers import PiggyBankConstants, getDeltaTimeHelper
from gui.impl.pub import ViewImpl
from gui.shared.event_dispatcher import showWotPlusInfoPage, showTankPremiumAboutPage, showShop
from helpers import dependency
from skeletons.gui.game_control import IGameSessionController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from account_helpers.renewable_subscription import RenewableSubscription
_logger = logging.getLogger(__name__)

class CurrencyReservesView(ViewImpl):
    _itemsCache = dependency.descriptor(IItemsCache)
    _gameSession = dependency.descriptor(IGameSessionController)
    _lobbyContext = dependency.descriptor(ILobbyContext)
    __slots__ = ('_renewableSubHelper', '_creditReserveInfo', '_creditReserveConfig', '_serverSettings')

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
        settings.model = CurrencyReservesViewModel()
        self._renewableSubHelper = BigWorld.player().renewableSubscription
        self._creditReserveInfo = self._itemsCache.items.stats.piggyBank
        self._creditReserveConfig = self._lobbyContext.getServerSettings().getPiggyBankConfig()
        self._serverSettings = self._lobbyContext.getServerSettings()
        super(CurrencyReservesView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(CurrencyReservesView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        self.viewModel.onClose += self._onClose
        self._gameSession.onPremiumNotify += self._onPremiumNotify
        self._lobbyContext.getServerSettings().onServerSettingsChange += self._onServerSettingsChange
        self._renewableSubHelper.onRenewableSubscriptionDataChanged += self._onRenewableSubscriptionDataChanged
        self.viewModel.goldReserve.onInfoButtonClick += self._onGoldReserveInfoButtonClick
        self.viewModel.goldReserve.onActionButtonClick += self._onGoldReserveActionButtonClick
        self.viewModel.creditReserve.onInfoButtonClick += self._onCreditReserveInfoButtonClick
        self.viewModel.creditReserve.onActionButtonClick += self._onCreditReserveActionButtonClick
        g_clientUpdateManager.addCallbacks({PiggyBankConstants.PIGGY_BANK: self._onPiggyBankChanged})

    def _finalize(self):
        self.viewModel.onClose -= self._onClose
        self._gameSession.onPremiumNotify -= self._onPremiumNotify
        self._lobbyContext.getServerSettings().onServerSettingsChange -= self._onServerSettingsChange
        self._renewableSubHelper.onRenewableSubscriptionDataChanged -= self._onRenewableSubscriptionDataChanged
        self.viewModel.goldReserve.onInfoButtonClick -= self._onGoldReserveInfoButtonClick
        self.viewModel.goldReserve.onActionButtonClick -= self._onGoldReserveActionButtonClick
        self.viewModel.creditReserve.onInfoButtonClick -= self._onCreditReserveInfoButtonClick
        self.viewModel.creditReserve.onActionButtonClick -= self._onCreditReserveActionButtonClick
        g_clientUpdateManager.removeObjectCallbacks(self)

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
            goldReserve.setIsActive(self._renewableSubHelper.isEnabled())
            goldReserve.setCurrency(CurrencyEnum.GOLD)
            goldReserve.setAmount(self._renewableSubHelper.getGoldReserve())
            goldReserve.setMaxCapacity(self._serverSettings.getRenewableSubMaxGoldReserveCapacity())

    def _onServerSettingsChange(self, diff):
        if RENEWABLE_SUBSCRIPTION_CONFIG in diff:
            self._updateGoldReserve()
        if PremiumConfigs.PIGGYBANK in diff:
            self._updateCreditReserve()
            self._updateTimeToOpen()

    def _onRenewableSubscriptionDataChanged(self, *args, **kwargs):
        self._updateGoldReserve()

    def _onClose(self):
        self.destroyWindow()

    def _isPremiumPlusActive(self):
        return self._itemsCache.items.stats.isActivePremium(PREMIUM_TYPE.PLUS)

    def _onGoldReserveInfoButtonClick(self):
        showWotPlusInfoPage()

    def _onGoldReserveActionButtonClick(self):
        showShop(getBuyRenewableSubscriptionUrl())

    def _onCreditReserveInfoButtonClick(self):
        showTankPremiumAboutPage()

    def _onCreditReserveActionButtonClick(self):
        showShop(getBuyPremiumUrl())
