# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/prb_windows/PrbSendInvitesWindow.py
import account_helpers
from debug_utils import LOG_ERROR
from gui import SystemMessages
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.daapi.view.meta.PrbSendInvitesWindowMeta import PrbSendInvitesWindowMeta
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.locale.DIALOGS import DIALOGS
from gui.prb_control.context import SendInvitesCtx
from gui.prb_control.prb_helpers import prbDispatcherProperty
from gui.prb_control.settings import REQUEST_TYPE, CTRL_ENTITY_TYPE
from gui.shared import EVENT_BUS_SCOPE, events
from helpers import i18n
from messenger.gui.Scaleform.data import users_data_providers, search_data_providers
from messenger.proto.interfaces import ISearchHandler

class PrbSendInvitesWindow(View, PrbSendInvitesWindowMeta, AbstractWindowView, ISearchHandler):

    def __init__(self, ctx):
        super(PrbSendInvitesWindow, self).__init__()
        self._searchDP = None
        self._friendsDP = None
        self._clanDP = None
        self._onlineMode = True
        self._ctx = ctx
        if 'ctrlType' in ctx:
            self._ctrlType = ctx['ctrlType']
        else:
            self._ctrlType = CTRL_ENTITY_TYPE.UNKNOWN
            LOG_ERROR('Control type is not defined', ctx)
        if 'prbName' in ctx:
            self._prbName = ctx['prbName']
        else:
            self._prbName = 'prebattle'
        if 'showClanOnly' in ctx:
            self._showClanOnly = ctx['showClanOnly']
        else:
            self._showClanOnly = False
        if 'invites' in ctx:
            self._invites = ctx['invites']
        else:
            self._invites = ()
        return

    @prbDispatcherProperty
    def prbDispatcher(self):
        pass

    def showError(self, value):
        SystemMessages.pushI18nMessage(value, type=SystemMessages.SM_TYPE.Error)

    def searchToken(self, value):
        self._searchDP.find(value, onlineMode=self._onlineMode)

    def setOnlineFlag(self, value):
        if value is False:
            self._onlineMode = None
        else:
            self._onlineMode = True
        self._friendsDP.setOnlineMode(self._onlineMode)
        self._clanDP.setOnlineMode(self._onlineMode)
        return

    def sendInvites(self, accountsToInvite, comment):
        functional = self.prbDispatcher.getFunctional(self._ctrlType)
        if functional:
            functional.request(SendInvitesCtx(accountsToInvite, comment))
        else:
            LOG_ERROR('Functional is not found', self._ctrlType)

    def onWindowClose(self):
        self.destroy()

    def onSearchComplete(self, result):
        self.as_onSearchResultReceivedS(True)

    def onSearchFailed(self, reason):
        self.as_onSearchResultReceivedS(False)

    def _populate(self):
        super(PrbSendInvitesWindow, self)._populate()
        self.addListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        self.as_setWindowTitleS(i18n.makeString(DIALOGS.SENDINVITES_COMMON_TITLE))
        self.as_setDefaultOnlineFlagS(self._onlineMode)
        self.as_showClanOnlyS(self._showClanOnly)
        self._searchDP = search_data_providers.SearchUsersDataProvider(exclude=[account_helpers.getPlayerDatabaseID()])
        self._searchDP.init(self.as_getSearchDPS(), [self])
        self._friendsDP = users_data_providers.FriendsDataProvider()
        self._friendsDP.init(self.as_getFriendsDPS(), self._onlineMode)
        self._clanDP = users_data_providers.ClanMembersDataProvider()
        self._clanDP.init(self.as_getClanDPS(), self._onlineMode)
        self._sendInvites()

    def _dispose(self):
        self.removeListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        if self._searchDP is not None:
            self._searchDP.fini()
            self._searchDP = None
        if self._friendsDP is not None:
            self._friendsDP.fini()
            self._friendsDP = None
        if self._clanDP is not None:
            self._clanDP.fini()
            self._clanDP = None
        super(PrbSendInvitesWindow, self)._dispose()
        return

    def _sendInvites(self):
        if self._invites:
            self.as_setInvitesS(self._invites)

    def __handleSetPrebattleCoolDown(self, event):
        if event.requestID is REQUEST_TYPE.SEND_INVITE:
            self.as_onReceiveSendInvitesCooldownS(event.coolDown)
