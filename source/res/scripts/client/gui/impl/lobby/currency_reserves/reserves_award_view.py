# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/currency_reserves/reserves_award_view.py
from constants import PREMIUM_TYPE
from frameworks.wulf import ViewSettings
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getBuyPremiumUrl, getWotPlusShopUrl
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.currency_reserves.reserves_award_view_model import ReservesAwardViewModel
from gui.impl.lobby.currency_reserves.sounds import RESERVES_AWARD_SOUND_SPACE
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.shared.event_dispatcher import showShop
from helpers import dependency
from skeletons.gui.game_control import IWotPlusController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from uilogging.wot_plus.logging_constants import WotPlusKeys, ReservesKeys
from uilogging.wot_plus.loggers import WotPlusEventLogger

class ReservesAwardView(ViewImpl):
    _itemsCache = dependency.descriptor(IItemsCache)
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _wotPlusCtrl = dependency.descriptor(IWotPlusController)
    __slots__ = ('_wotPlusUILogger',)
    _COMMON_SOUND_SPACE = RESERVES_AWARD_SOUND_SPACE

    def __init__(self, layoutID, *args, **kwargs):
        settings = ViewSettings(layoutID)
        settings.model = ReservesAwardViewModel()
        settings.args = args
        settings.kwargs = kwargs
        self._wotPlusUILogger = WotPlusEventLogger(WotPlusKeys.RESERVE_AWARD_VIEW)
        super(ReservesAwardView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ReservesAwardView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        self.viewModel.onClose += self._onClose
        self.viewModel.onPremiumAccountExtend += self._onPremiumAccountExtend
        self.viewModel.onSubscriptionExtend += self._onSubscriptionExtend

    def _finalize(self):
        self.viewModel.onClose -= self._onClose
        self.viewModel.onPremiumAccountExtend -= self._onPremiumAccountExtend
        self.viewModel.onSubscriptionExtend -= self._onSubscriptionExtend

    def _onLoading(self, creditsEarned, goldEarned):
        showCreditWarning = self._isPiggyBankEnabled() and not self._isPremiumPlusActive() and creditsEarned
        showGoldWarning = self._isGoldReserveEnabled() and not self._wotPlusCtrl.isEnabled() and goldEarned
        self.viewModel.setCreditAmount(creditsEarned)
        self.viewModel.setGoldAmount(goldEarned)
        self.viewModel.setShowCreditWarning(showCreditWarning)
        self.viewModel.setShowGoldWarning(showGoldWarning)

    def _isPremiumPlusActive(self):
        return self._itemsCache.items.stats.isActivePremium(PREMIUM_TYPE.PLUS)

    def _isPiggyBankEnabled(self):
        return self._lobbyContext.getServerSettings().getPiggyBankConfig().get('enabled', False)

    def _isGoldReserveEnabled(self):
        return self._lobbyContext.getServerSettings().isRenewableSubGoldReserveEnabled()

    def _onPremiumAccountExtend(self):
        self._wotPlusUILogger.logClickEvent(ReservesKeys.CREDITS_INFO)
        showShop(getBuyPremiumUrl())
        self.destroyWindow()

    def _onSubscriptionExtend(self):
        self._wotPlusUILogger.logClickEvent(ReservesKeys.GOLD_INFO)
        showShop(getWotPlusShopUrl())
        self.destroyWindow()

    def _onClose(self):
        self._wotPlusUILogger.logCloseEvent()
        self.destroyWindow()


class ReservesAwardWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, creditsEarned, goldEarned):
        super(ReservesAwardWindow, self).__init__(content=ReservesAwardView(R.views.lobby.currency_reserves.ReservesAwardView(), creditsEarned, goldEarned))
