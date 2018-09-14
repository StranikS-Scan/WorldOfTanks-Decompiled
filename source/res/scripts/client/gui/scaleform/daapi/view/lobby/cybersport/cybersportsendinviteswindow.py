# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/cyberSport/CyberSportSendInvitesWindow.py
from adisp import process
from gui import SystemMessages
from gui.clubs import contexts as club_ctx, formatters as club_fmts
from gui.clubs.club_helpers import ClubListener
from gui.Scaleform.daapi.view.lobby.SendInvitesWindow import SendInvitesWindow
from gui.Scaleform.locale.WAITING import WAITING
from messenger.proto.events import g_messengerEvents

class CyberSportSendInvitesWindow(SendInvitesWindow, ClubListener):

    def __init__(self, ctx):
        super(CyberSportSendInvitesWindow, self).__init__(ctx)
        raise 'clubDbID' in ctx or AssertionError
        self.__clubDbID = ctx['clubDbID']
        self.__foundUsersCache = {}

    @process
    def sendInvites(self, accountsToInvite, comment):
        self.as_showWaitingS(WAITING.CLUBS_INVITES_SEND, {})
        result = yield self.clubsCtrl.sendRequest(club_ctx.SendInviteCtx(self.__clubDbID, accountsToInvite))
        if result.isSuccess():
            formatter = club_fmts.InvitesSysMsgFormatter(accountsToInvite, result, self.__foundUsersCache)
            SystemMessages.pushMessage(formatter.getSuccessSysMsg())
            errorSysMsg = formatter.getErrorSysMsg()
            if errorSysMsg:
                SystemMessages.pushMessage(errorSysMsg, type=SystemMessages.SM_TYPE.Error)
            self.destroy()
        self.as_hideWaitingS()

    def _populate(self):
        super(CyberSportSendInvitesWindow, self)._populate()
        g_messengerEvents.users.onFindUsersComplete += self.__onFindUsersComplete
        self.as_enableDescriptionS(False)

    def _dispose(self):
        g_messengerEvents.users.onFindUsersComplete -= self.__onFindUsersComplete
        super(CyberSportSendInvitesWindow, self)._dispose()

    def __onFindUsersComplete(self, _, users):
        self.__foundUsersCache.update(dict(((user.getID(), user) for user in users)))
