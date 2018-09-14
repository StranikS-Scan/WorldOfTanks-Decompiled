# Embedded file name: scripts/client/gui/battle_control/DynSquadViewListener.py
import BigWorld
from constants import INVITATION_TYPE
from gui.battle_control import g_sessionProvider
from gui.battle_control.requests.context import SendInvitesCtx
from gui.prb_control.prb_helpers import prbInvitesProperty
from adisp import process

class DynSquadViewListener(object):

    def __init__(self, battleUI):
        super(DynSquadViewListener, self).__init__()
        self.__battleUI = battleUI
        self.__battleUI.addExternalCallbacks({'Battle.UsersRoster.LeaveSquad': self.__onLeaveSquad,
         'Battle.UsersRoster.ExcludedFromSquad': self.__onExcludedFromSquad,
         'Battle.UsersRoster.SendInvitationToSquad': self.__onSentInviteToSquad,
         'Battle.UsersRoster.WithdrawInvitationToSquad': self.__onWithdrawInviteToSquad,
         'Battle.UsersRoster.AcceptInvitationToSquad': self.__onAcceptInviteToSquad,
         'Battle.UsersRoster.RejectInvitationToSquad': self.__onRejectInviteToSquad,
         'Battle.addToDynamicSquad': self.__onSentInviteToSquad,
         'Battle.acceptInviteToDynamicSquad': self.__onAcceptInviteToSquad})

    @prbInvitesProperty
    def prbInvites(self):
        return None

    def destroy(self):
        if self.__battleUI:
            self.__battleUI.removeExternalCallbacks(('Battle.UsersRoster.LeaveSquad', 'Battle.UsersRoster.ExcludedFromSquad', 'Battle.UsersRoster.SendInvitationToSquad', 'Battle.UsersRoster.WithdrawInvitationToSquad', 'Battle.UsersRoster.AcceptInvitationToSquad', 'Battle.UsersRoster.RejectInvitationToSquad', 'Battle.addToDynamicSquad', 'Battle.acceptInviteToDynamicSquad'))
        self.__battleUI = None
        return

    def __onLeaveSquad(self, _, userId):
        pass

    def __onExcludedFromSquad(self, _, userId):
        pass

    @process
    def __onSentInviteToSquad(self, _, userId):
        yield g_sessionProvider.sendRequest(SendInvitesCtx(databaseIDs=(userId,)))

    def __onAcceptInviteToSquad(self, _, userId):
        inviteID = self.__getInviteID(userId, True, True)
        if inviteID is not None:
            self.prbInvites.acceptInvite(inviteID)
        return

    def __onWithdrawInviteToSquad(self, _, userId):
        inviteID = self.__getInviteID(userId, False, False)
        if inviteID is not None:
            self.prbInvites.revokeInvite(inviteID)
        return

    def __onRejectInviteToSquad(self, _, userId):
        inviteID = self.__getInviteID(userId, True, True)
        if inviteID is not None:
            self.prbInvites.declineInvite(inviteID)
        return

    def __getInviteID(self, userId, isCreator, incomingInvites):
        invites = self.prbInvites.getInvites(incoming=incomingInvites, onlyActive=True)
        if isCreator:
            idGetter = lambda i: i.creatorDBID
        else:
            idGetter = lambda i: i.receiverDBID
        for invite in invites:
            if invite.type == INVITATION_TYPE.SQUAD and idGetter(invite) == userId:
                return invite.clientID

        return None
