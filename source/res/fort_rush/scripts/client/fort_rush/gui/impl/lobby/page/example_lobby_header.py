# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/lobby/page/example_lobby_header.py
from __future__ import absolute_import
from gui.impl.gen import R
from gui.impl.lobby.common.presenters.vehicles_info_presenter import VehiclesInfoPresenter
from gui.impl.lobby.page.fight_start import FightStartPresenter
from gui.impl.lobby.page.header_state_presenter import HeaderStatePresenter
from gui.impl.lobby.page.lobby_header import LobbyHeader
from gui.impl.lobby.page.navigation_presenter import NavigationPresenter
from gui.impl.lobby.page.prebattle_presenter import PrebattlePresenter
from gui.impl.lobby.page.prem_shop_presenter import PremShopPresenter
from gui.impl.lobby.page.reserves_entry_point_presenter import ReservesEntryPointPresenter
from gui.impl.lobby.page.user_account_presenter import UserAccountPresenter
from gui.impl.lobby.page.wallet_presenter import WalletPresenter, GoldProvider, CreditsProvider

class ExampleLobbyHeader(LobbyHeader):

    def _getChildComponents(self):
        header = R.aliases.lobby_header.default
        return {header.FightStart(): FightStartPresenter,
         header.NavigationBar(): NavigationPresenter,
         header.Prebattle(): PrebattlePresenter,
         header.Wallet(): lambda : WalletPresenter((GoldProvider(), CreditsProvider())),
         header.UserAccount(): UserAccountPresenter,
         header.HeaderState(): HeaderStatePresenter,
         header.ReservesEntryPoint(): ReservesEntryPointPresenter,
         header.PremShop(): PremShopPresenter,
         header.CurrentVehicle(): lambda : VehiclesInfoPresenter(self._currentVehicleFilter)}
