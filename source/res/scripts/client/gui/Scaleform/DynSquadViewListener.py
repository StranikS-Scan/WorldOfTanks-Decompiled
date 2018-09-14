# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/DynSquadViewListener.py
from BattleReplay import g_replayCtrl
from constants import INVITATION_TYPE
from gui.battle_control import g_sessionProvider
from gui.battle_control.requests.context import SendInvitesCtx
from gui.prb_control.prb_helpers import prbInvitesProperty
from adisp import process

class DynSquadViewListener(object):

    def __init__(self, battleUI):
        super(DynSquadViewListener, self).__init__()
        self.__battleUI = battleUI
        self.__battleUI.addExternalCallbacks({'Battle.UsersRoster.LeaveSquad': self._onLeaveSquad,
         'Battle.UsersRoster.ExcludedFromSquad': self._onExcludedFromSquad,
         'Battle.UsersRoster.SendInvitationToSquad': self._onSentInviteToSquad,
         'Battle.UsersRoster.WithdrawInvitationToSquad': self._onWithdrawInviteToSquad,
         'Battle.UsersRoster.AcceptInvitationToSquad': self._onAcceptInviteToSquad,
         'Battle.UsersRoster.RejectInvitationToSquad': self._onRejectInviteToSquad,
         'Battle.addToDynamicSquad': self._onSentInviteToSquad,
         'Battle.acceptInviteToDynamicSquad': self._onAcceptInviteToSquad})

    @prbInvitesProperty
    def prbInvites(self):
        return None

    def destroy(self):
        if self.__battleUI:
            self.__battleUI.removeExternalCallbacks(('Battle.UsersRoster.LeaveSquad', 'Battle.UsersRoster.ExcludedFromSquad', 'Battle.UsersRoster.SendInvitationToSquad', 'Battle.UsersRoster.WithdrawInvitationToSquad', 'Battle.UsersRoster.AcceptInvitationToSquad', 'Battle.UsersRoster.RejectInvitationToSquad', 'Battle.addToDynamicSquad', 'Battle.acceptInviteToDynamicSquad'))
        self.__battleUI = None
        return

    def _onLeaveSquad(self, _, userId):
        pass

    def _onExcludedFromSquad(self, _, userId):
        pass

    @process
    def _onSentInviteToSquad(self, _, userId):
        yield g_sessionProvider.sendRequest(SendInvitesCtx(databaseIDs=(userId,)))

    def _onAcceptInviteToSquad(self, _, userId):
        inviteID = self.__getInviteID(userId, True, True)
        if inviteID is not None:
            self.prbInvites.acceptInvite(inviteID)
        return

    def _onWithdrawInviteToSquad(self, _, userId):
        inviteID = self.__getInviteID(userId, False, False)
        if inviteID is not None:
            self.prbInvites.revokeInvite(inviteID)
        return

    def _onRejectInviteToSquad(self, _, userId):
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


class RecordDynSquadViewListener(DynSquadViewListener):
    """Replay recording wrapper for DynSquadViewListener.
    
    This class wraps DynSquadViewListener in order to record player's
    actions with dyn squads during replay recording.
    """

    def _onSentInviteToSquad(self, callbackId, userId):
        g_replayCtrl.serializeCallbackData('DynSquad.SendInvitationToSquad', (callbackId, userId))
        super(RecordDynSquadViewListener, self)._onSentInviteToSquad(callbackId, userId)

    def _onWithdrawInviteToSquad(self, callbackId, userId):
        g_replayCtrl.serializeCallbackData('DynSquad.WithdrawInvitationToSquad', (callbackId, userId))
        super(RecordDynSquadViewListener, self)._onWithdrawInviteToSquad(callbackId, userId)

    def _onAcceptInviteToSquad(self, callbackId, userId):
        g_replayCtrl.serializeCallbackData('DynSquad.AcceptInvitationToSquad', (callbackId, userId))
        super(RecordDynSquadViewListener, self)._onAcceptInviteToSquad(callbackId, userId)

    def _onRejectInviteToSquad(self, callbackId, userId):
        g_replayCtrl.serializeCallbackData('DynSquad.RejectInvitationToSquad', (callbackId, userId))
        super(RecordDynSquadViewListener, self)._onRejectInviteToSquad(callbackId, userId)


class ReplayDynSquadViewListener(DynSquadViewListener):
    """Replay playing wrapper for DynSquadViewListener.
    
    This class wraps DynSquadViewListener in order to simulate player's
    actions with dyn squads during replay.
    """

    def __init__(self, battleUI):
        super(ReplayDynSquadViewListener, self).__init__(battleUI)
        for eventName, method in [('DynSquad.SendInvitationToSquad', self._onSentInviteToSquad),
         ('DynSquad.WithdrawInvitationToSquad', self._onWithdrawInviteToSquad),
         ('DynSquad.AcceptInvitationToSquad', self._onAcceptInviteToSquad),
         ('DynSquad.RejectInvitationToSquad', self._onRejectInviteToSquad)]:
            g_replayCtrl.setDataCallback(eventName, method)

    def destroy(self):
        for eventName, method in [('DynSquad.SendInvitationToSquad', self._onSentInviteToSquad),
         ('DynSquad.WithdrawInvitationToSquad', self._onWithdrawInviteToSquad),
         ('DynSquad.AcceptInvitationToSquad', self._onAcceptInviteToSquad),
         ('DynSquad.RejectInvitationToSquad', self._onRejectInviteToSquad)]:
            g_replayCtrl.delDataCallback(eventName, method)

        super(ReplayDynSquadViewListener, self).destroy()
