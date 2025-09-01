# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/page/lobby_header.py
from __future__ import absolute_import
from frameworks.wulf import WindowLayer
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.page.header.default_model import DefaultModel
from gui.impl.lobby.page.fight_start import FightStartPresenter
from gui.impl.lobby.page.header_state_presenter import HeaderStatePresenter
from gui.impl.lobby.page.navigation_presenter import NavigationPresenter
from gui.impl.lobby.page.prebattle_presenter import PrebattlePresenter
from gui.impl.lobby.page.prem_shop_presenter import PremShopPresenter
from gui.impl.lobby.page.reserves_entry_point_presenter import ReservesEntryPointPresenter
from gui.impl.lobby.page.user_account_presenter import UserAccountPresenter
from gui.impl.lobby.page.wallet_presenter import WalletPresenter, GoldProvider, CreditsProvider, CrystalProvider, FreeXpProvider
from gui.impl.pub.view_component import ViewComponent

class LobbyHeader(ViewComponent[DefaultModel]):

    def __init__(self):
        super(LobbyHeader, self).__init__(R.views.mono.hangar.header(), DefaultModel)

    @property
    def viewModel(self):
        return super(LobbyHeader, self).getViewModel()

    def setOldStyleViewFlag(self, value):
        self.viewModel.setOldStyle(value)

    def _getChildComponents(self):
        header = R.aliases.lobby_header.default
        return {header.FightStart(): FightStartPresenter,
         header.NavigationBar(): NavigationPresenter,
         header.Prebattle(): PrebattlePresenter,
         header.Wallet(): lambda : WalletPresenter((CrystalProvider(),
                           GoldProvider(),
                           CreditsProvider(),
                           FreeXpProvider())),
         header.UserAccount(): UserAccountPresenter,
         header.HeaderState(): HeaderStatePresenter,
         header.ReservesEntryPoint(): ReservesEntryPointPresenter,
         header.PremShop(): PremShopPresenter}

    def _getPopOverLayer(self):
        return WindowLayer.VIEW
