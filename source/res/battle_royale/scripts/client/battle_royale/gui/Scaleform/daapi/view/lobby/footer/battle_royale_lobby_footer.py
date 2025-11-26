# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/lobby/footer/battle_royale_lobby_footer.py
from __future__ import absolute_import
from gui.impl.gen import R
from gui.impl.lobby.page.chats_presenter import ChatsPresenter
from gui.impl.lobby.page.contacts_list_presenter import ContactsListPresenter
from gui.impl.lobby.page.lobby_footer import LobbyFooter
from gui.impl.lobby.page.notifications_center_presenter import NotificationsCenterPresenter
from gui.impl.lobby.page.referral_program_presenter import ReferralProgramPresenter
from gui.impl.lobby.page.server_info_presenter import ServerInfoPresenter
from gui.impl.lobby.page.session_stats_presenter import SessionStatsPresenter
from gui.impl.lobby.page.vehicle_compare_presenter import VehicleComparePresenter
from battle_royale.gui.impl.lobby.views.presenters.battle_royale_platoon_presenter import BattleRoyalePlatoonPresenter

class BattleRoyaleLobbyFooter(LobbyFooter):

    def _initChildren(self):
        footer = R.aliases.lobby_footer.default
        self._registerChild(footer.Platoon(), BattleRoyalePlatoonPresenter())
        self._registerChild(footer.NotificationsCenter(), NotificationsCenterPresenter())
        self._registerChild(footer.ContactsList(), ContactsListPresenter())
        self._registerChild(footer.SessionStats(), SessionStatsPresenter())
        self._registerChild(footer.VehicleCompare(), VehicleComparePresenter())
        self._registerChild(footer.Chats(), ChatsPresenter())
        self._registerChild(footer.ReferralProgram(), ReferralProgramPresenter())
        self._registerChild(footer.ServerInfo(), ServerInfoPresenter())
