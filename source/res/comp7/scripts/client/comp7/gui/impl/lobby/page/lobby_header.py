# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/page/lobby_header.py
from __future__ import absolute_import
from comp7.gui.impl.lobby.page.comp7_fight_start import Comp7FightStartPresenter
from comp7.gui.impl.lobby.page.comp7_prebattle_presenter import Comp7PrebattlePresenter
from gui.impl.gen import R
from gui.impl.lobby.page.header_state_presenter import HeaderStatePresenter
from gui.impl.lobby.page.lobby_header import LobbyHeader
from gui.impl.lobby.page.navigation_presenter import NavigationPresenter
from gui.impl.lobby.page.prem_shop_presenter import PremShopPresenter
from gui.impl.lobby.page.reserves_entry_point_presenter import ReservesEntryPointPresenter
from gui.impl.lobby.page.user_account_presenter import UserAccountPresenter
from gui.impl.lobby.page.wallet_presenter import WalletPresenter, GoldProvider, CreditsProvider, CrystalProvider, FreeXpProvider

class Comp7LobbyHeader(LobbyHeader):

    def _getChildComponents(self):
        header = R.aliases.lobby_header.default
        return {header.FightStart(): Comp7FightStartPresenter,
         header.NavigationBar(): NavigationPresenter,
         header.Prebattle(): Comp7PrebattlePresenter,
         header.Wallet(): lambda : WalletPresenter((CrystalProvider(),
                           GoldProvider(),
                           CreditsProvider(),
                           FreeXpProvider())),
         header.UserAccount(): UserAccountPresenter,
         header.HeaderState(): HeaderStatePresenter,
         header.ReservesEntryPoint(): ReservesEntryPointPresenter,
         header.PremShop(): PremShopPresenter}
