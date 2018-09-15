# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/clans/invites/ClanSendInvitesWindow.py
from adisp import process
from client_request_lib.exceptions import ResponseCodes
from gui import SystemMessages
from gui.Scaleform.daapi.view.lobby.SendInvitesWindow import SendInvitesWindow
from gui.Scaleform.locale.CLANS import CLANS
from gui.Scaleform.locale.WAITING import WAITING
from gui.clans import contexts as clan_ctx
from gui.clans import formatters as clans_fmts
from gui.clans.clan_helpers import ClanListener, showClanInviteSystemMsg
from gui.shared.view_helpers import UsersInfoHelper
from helpers import i18n
from messenger.m_constants import USER_TAG

class ClanSendInvitesWindow(SendInvitesWindow, UsersInfoHelper, ClanListener):

    def __init__(self, ctx):
        super(ClanSendInvitesWindow, self).__init__(ctx)
        assert 'clanDbID' in ctx
        self.__clanDbID = ctx['clanDbID']

    @process
    def sendInvites(self, accountsToInvite, comment):
        self.as_showWaitingS(WAITING.CLANS_INVITES_SEND, {})
        accountsToInvite = [ int(userDbID) for userDbID in accountsToInvite ]
        ctx = clan_ctx.CreateInviteCtx(self.__clanDbID, accountsToInvite, comment)
        self.as_onReceiveSendInvitesCooldownS(ctx.getCooldown())
        result = yield self.clansCtrl.sendRequest(ctx)
        expectedCodes = (ResponseCodes.ACCOUNT_ALREADY_APPLIED, ResponseCodes.ACCOUNT_ALREADY_INVITED, ResponseCodes.NO_ERRORS)
        if result.getCode() in expectedCodes:
            successAccounts = [ item.getAccountDbID() for item in ctx.getDataObj(result.data) ]
            failedAccounts = set(accountsToInvite) - set(successAccounts)
        else:
            successAccounts = []
            failedAccounts = accountsToInvite
        if len(accountsToInvite) > 1:
            if successAccounts:
                accountNames = [ self.getUserName(userDbID) for userDbID in successAccounts ]
                SystemMessages.pushMessage(clans_fmts.getInvitesSentSysMsg(accountNames))
            if failedAccounts:
                accountNames = [ self.getUserName(userDbID) for userDbID in failedAccounts ]
                SystemMessages.pushMessage(clans_fmts.getInvitesNotSentSysMsg(accountNames), type=SystemMessages.SM_TYPE.Error)
        else:
            showClanInviteSystemMsg(self.getUserName(accountsToInvite[0]), result.isSuccess(), result.getCode())
        self.as_hideWaitingS()

    def _populate(self):
        super(ClanSendInvitesWindow, self)._populate()
        self.as_setInvalidUserTagsS([USER_TAG.IGNORED,
         USER_TAG.IGNORED_TMP,
         USER_TAG.CURRENT,
         USER_TAG.CLAN_MEMBER,
         USER_TAG.OTHER_CLAN_MEMBER])
        self.as_enableMassSendS(False, CLANS.CLANPROFILE_SENDINVITESWINDOW_TOOLTIP_MASSSENDBLOCKED)

    def _initCooldown(self):
        pass

    def _finiCooldown(self):
        pass

    def _handleSetCoolDown(self, event):
        pass

    def _getTitle(self):
        return i18n.makeString(CLANS.CLANPROFILE_SENDINVITESWINDOW_TITLE)
