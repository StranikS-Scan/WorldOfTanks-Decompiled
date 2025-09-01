# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/lobby/page/lobby_header.py
from __future__ import absolute_import
from comp7_light.gui.impl.lobby.page.comp7_light_fight_start import Comp7LightFightStartPresenter
from comp7_light.gui.impl.lobby.page.comp7_light_prebattle_presenter import Comp7LightPrebattlePresenter
from gui.impl.gen import R
from gui.impl.lobby.page.header_state_presenter import HeaderStatePresenter
from gui.impl.lobby.page.lobby_header import LobbyHeader
from gui.impl.lobby.page.navigation_presenter import NavigationPresenter
from gui.impl.lobby.page.prem_shop_presenter import PremShopPresenter
from gui.impl.lobby.page.reserves_entry_point_presenter import ReservesEntryPointPresenter
from gui.impl.lobby.page.user_account_presenter import UserAccountPresenter
from gui.impl.lobby.page.wallet_presenter import WalletPresenter, GoldProvider, CreditsProvider, CrystalProvider, FreeXpProvider

class Comp7LightLobbyHeader(LobbyHeader):

    def _getChildComponents(self):
        header = R.aliases.lobby_header.default
        return {header.FightStart(): Comp7LightFightStartPresenter,
         header.NavigationBar(): NavigationPresenter,
         header.Prebattle(): Comp7LightPrebattlePresenter,
         header.Wallet(): lambda : WalletPresenter((CrystalProvider(),
                           GoldProvider(),
                           CreditsProvider(),
                           FreeXpProvider())),
         header.UserAccount(): UserAccountPresenter,
         header.HeaderState(): HeaderStatePresenter,
         header.ReservesEntryPoint(): ReservesEntryPointPresenter,
         header.PremShop(): PremShopPresenter}
