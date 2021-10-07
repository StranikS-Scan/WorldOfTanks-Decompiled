# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/currency_reserves/reserves_award_view.py
import typing
import BigWorld
from constants import PREMIUM_TYPE
from frameworks.wulf import ViewSettings
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getBuyPremiumUrl, getBuyRenewableSubscriptionUrl
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.currency_reserves.reserves_award_view_model import ReservesAwardViewModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.shared.event_dispatcher import showShop
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from account_helpers.renewable_subscription import RenewableSubscription

class ReservesAwardView(ViewImpl):
    _itemsCache = dependency.descriptor(IItemsCache)
    _lobbyContext = dependency.descriptor(ILobbyContext)
    __slots__ = ('_renewableSubHelper',)

    def __init__(self, layoutID, *args, **kwargs):
        settings = ViewSettings(layoutID)
        settings.model = ReservesAwardViewModel()
        settings.args = args
        settings.kwargs = kwargs
        self._renewableSubHelper = BigWorld.player().renewableSubscription
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
        showGoldWarning = self._isGoldReserveEnabled() and not self._renewableSubHelper.isEnabled() and goldEarned
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
        showShop(getBuyPremiumUrl())
        self.destroyWindow()

    def _onSubscriptionExtend(self):
        showShop(getBuyRenewableSubscriptionUrl())
        self.destroyWindow()

    def _onClose(self):
        self.destroyWindow()


class ReservesAwardWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, creditsEarned, goldEarned):
        super(ReservesAwardWindow, self).__init__(content=ReservesAwardView(R.views.lobby.currency_reserves.ReservesAwardView(), creditsEarned, goldEarned))
