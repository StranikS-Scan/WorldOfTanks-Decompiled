# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/clans/invites/ClanSendInvitesWindow.py
from adisp import process
from gui import SystemMessages
from gui.Scaleform.daapi.view.lobby.SendInvitesWindow import SendInvitesWindow
from gui.Scaleform.locale.CLANS import CLANS
from gui.Scaleform.locale.WAITING import WAITING
from gui.clans import contexts as clan_ctx
from gui.clans import formatters as clans_fmts
from gui.clans.clan_helpers import ClanListener
from gui.clans.settings import CLAN_REQUESTED_DATA_TYPE
from gui.shared.events import CoolDownEvent
from gui.shared.view_helpers.CooldownHelper import CooldownHelper
from gui.shared.view_helpers import UsersInfoHelper
from helpers import i18n
from messenger.m_constants import USER_TAG

class ClanSendInvitesWindow(SendInvitesWindow, UsersInfoHelper, ClanListener):

    def __init__(self, ctx):
        super(ClanSendInvitesWindow, self).__init__(ctx)
        raise 'clanDbID' in ctx or AssertionError
        self.__clanDbID = ctx['clanDbID']
        self._cooldownHelper = CooldownHelper((CLAN_REQUESTED_DATA_TYPE.CREATE_INVITES,), self._handleSetCoolDown, CoolDownEvent.CLAN)
        self.__cooldown = None
        return

    @process
    def sendInvites(self, accountsToInvite, comment):
        self.as_showWaitingS(WAITING.CLANS_INVITES_SEND, {})
        accountsToInvite = [ int(userDbID) for userDbID in accountsToInvite ]
        ctx = clan_ctx.CreateInviteCtx(self.__clanDbID, accountsToInvite, comment)
        self.__cooldown = ctx.getCooldown()
        result = yield self.clansCtrl.sendRequest(ctx)
        successAccounts = [ item.getAccountDbID() for item in ctx.getDataObj(result.data) ]
        failedAccounts = set(accountsToInvite) - set(successAccounts)
        if successAccounts:
            accountNames = [ self.getUserName(userDbID) for userDbID in successAccounts ]
            SystemMessages.pushMessage(clans_fmts.getInvitesSentSysMsg(accountNames))
        if failedAccounts:
            accountNames = [ self.getUserName(userDbID) for userDbID in failedAccounts ]
            SystemMessages.pushMessage(clans_fmts.getInvitesNotSentSysMsg(accountNames), type=SystemMessages.SM_TYPE.Error)
        self.as_hideWaitingS()

    def _populate(self):
        super(ClanSendInvitesWindow, self)._populate()
        self._cooldownHelper.start()
        self.as_setInvalidUserTagsS([USER_TAG.IGNORED,
         USER_TAG.CURRENT,
         USER_TAG.CLAN_MEMBER,
         USER_TAG.OTHER_CLAN_MEMBER])
        self.as_enableMassSendS(False, CLANS.CLANPROFILE_SENDINVITESWINDOW_TOOLTIP_MASSSENDBLOCKED)

    def _dispose(self):
        self._cooldownHelper.stop()
        super(ClanSendInvitesWindow, self)._dispose()

    def _initCooldown(self):
        pass

    def _finiCooldown(self):
        pass

    def _handleSetCoolDown(self, isInCooldown):
        if not (isInCooldown and self.__cooldown is not None):
            raise AssertionError
            self.as_onReceiveSendInvitesCooldownS(self.__cooldown)
        return

    def _getTitle(self):
        return i18n.makeString(CLANS.CLANPROFILE_SENDINVITESWINDOW_TITLE)
