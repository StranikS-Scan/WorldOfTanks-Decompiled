# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/page/lobby_footer.py
from __future__ import absolute_import
import logging
import typing as t
from frameworks.wulf import WindowLayer
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.page.footer.default_model import DefaultModel
from gui.impl.lobby.page.chats_presenter import ChatsPresenter
from gui.impl.lobby.page.contacts_list_presenter import ContactsListPresenter
from gui.impl.lobby.page.notifications_center_presenter import NotificationsCenterPresenter
from gui.impl.lobby.page.platoon_presenter import PlatoonPresenter
from gui.impl.lobby.page.referral_program_presenter import ReferralProgramPresenter
from gui.impl.lobby.page.server_info_presenter import ServerInfoPresenter
from gui.impl.lobby.page.session_stats_presenter import SessionStatsPresenter
from gui.impl.lobby.page.vehicle_compare_presenter import VehicleComparePresenter
from gui.impl.pub.view_component import ViewComponent
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared.event_dispatcher import showLobbyMenu
from helpers import dependency
from skeletons.gui.game_control import IPlatoonController
if t.TYPE_CHECKING:
    from Event import Event
_logger = logging.getLogger(__name__)

class LobbyFooter(ViewComponent[DefaultModel], IGlobalListener):
    __platoonCtrl = dependency.descriptor(IPlatoonController)

    def __init__(self):
        super(LobbyFooter, self).__init__(R.views.mono.hangar.footer(), DefaultModel)

    @property
    def viewModel(self):
        return super(LobbyFooter, self).getViewModel()

    def setOldStyleViewFlag(self, value):
        self.viewModel.setOldStyle(value)

    def _initChildren(self):
        footer = R.aliases.lobby_footer.default
        self._registerChild(footer.Platoon(), PlatoonPresenter())
        self._registerChild(footer.NotificationsCenter(), NotificationsCenterPresenter())
        self._registerChild(footer.ContactsList(), ContactsListPresenter())
        self._registerChild(footer.SessionStats(), SessionStatsPresenter())
        self._registerChild(footer.VehicleCompare(), VehicleComparePresenter())
        self._registerChild(footer.Chats(), ChatsPresenter())
        self._registerChild(footer.ReferralProgram(), ReferralProgramPresenter())
        self._registerChild(footer.ServerInfo(), ServerInfoPresenter())

    def _getEvents(self):
        return ((self.viewModel.onOpenGameMenu, self.__showLobbyMenu),)

    def __showLobbyMenu(self):
        showLobbyMenu()

    def _getPopOverLayer(self):
        return WindowLayer.VIEW
