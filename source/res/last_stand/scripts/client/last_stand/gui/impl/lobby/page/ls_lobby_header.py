# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/page/ls_lobby_header.py
from gui.impl.gen import R
from gui.impl.lobby.page.fight_start import FightStartPresenter
from gui.impl.lobby.page.header_state_presenter import HeaderStatePresenter
from gui.impl.lobby.page.lobby_header import LobbyHeader
from gui.impl.lobby.page.navigation_presenter import NavigationPresenter
from gui.impl.lobby.page.prebattle_presenter import PrebattlePresenter
from gui.impl.lobby.page.prem_shop_presenter import PremShopPresenter
from gui.impl.lobby.page.user_account_presenter import UserAccountPresenter
from gui.impl.lobby.page.wallet_presenter import WalletPresenter, GoldProvider, CreditsProvider, CrystalProvider, FreeXpProvider

class LSLobbyHeader(LobbyHeader):

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
         header.PremShop(): PremShopPresenter}
