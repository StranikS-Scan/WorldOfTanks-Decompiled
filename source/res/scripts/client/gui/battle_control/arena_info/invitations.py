# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/arena_info/invitations.py
import BattleReplay
from adisp import process
from constants import INVITATION_TYPE
from gui.battle_control.arena_info.settings import INVITATION_DELIVERY_STATUS
from gui.battle_control.requests.context import SendInvitesCtx
from gui.prb_control import prbInvitesProperty
from ids_generators import SequenceIDGenerator
from skeletons.gui.battle_session import ISquadInvitationsHandler
from unit_roster_config import SquadRoster, EpicRoster
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
_STATUS = INVITATION_DELIVERY_STATUS
_SEND_ACTION_NAME = 'DynSquad.SendInvitationToSquad'
_ACCEPT_ACTION_NAME = 'DynSquad.AcceptInvitationToSquad'
_REJECT_ACTION_NAME = 'DynSquad.RejectInvitationToSquad'

class SquadInvitationsFilter(object):
    __slots__ = ('__arenaUniqueID', '__isReceivingProhibited', '__isSendingProhibited', '__received', '__sent')

    def __init__(self):
        super(SquadInvitationsFilter, self).__init__()
        self.__arenaUniqueID = 0
        self.__isReceivingProhibited = False
        self.__isSendingProhibited = False
        self.__received = {}
        self.__sent = {}

    def setArenaUniqueID(self, arenaUniqueID):
        self.__arenaUniqueID = arenaUniqueID

    def isReceivingProhibited(self):
        return self.__isReceivingProhibited

    def isSendingProhibited(self):
        return self.__isSendingProhibited

    def updatePersonalInfo(self, arenaDP):
        vInfoVO = arenaDP.getVehicleInfo()
        playerInfo = vInfoVO.player
        sessionProvider = dependency.instance(IBattleSessionProvider)
        arenaVisitor = sessionProvider.arenaVisitor
        isEpicBattle = arenaVisitor.gui.isEpicBattle()
        self.__isReceivingProhibited = playerInfo.forbidInBattleInvitations
        self.__isSendingProhibited = False
        if vInfoVO.isInSquad():
            if playerInfo.isPrebattleCreator:
                count = arenaDP.getVehiclesCountInPrebattle(vInfoVO.team, vInfoVO.prebattleID)
                maxSlots = SquadRoster.MAX_SLOTS if not isEpicBattle else EpicRoster.MAX_SLOTS
                self.__isSendingProhibited = count >= maxSlots
            else:
                self.__isSendingProhibited = True

    def addReceivedInvite(self, invite):
        if invite is None:
            return (0, _STATUS.NONE)
        else:
            self.__received[invite.creatorDBID] = invite.clientID
            include = _STATUS.RECEIVED_FROM
            if not self.__isInviteValid(invite):
                include |= _STATUS.RECEIVED_INACTIVE
            return (invite.creatorDBID, include)

    def addSentInvite(self, invite):
        if invite is None:
            return (0, _STATUS.NONE)
        else:
            self.__sent[invite.receiverDBID] = invite.clientID
            include = _STATUS.SENT_TO
            if not self.__isInviteValid(invite):
                include |= _STATUS.SENT_INACTIVE
            return (invite.receiverDBID, include)

    def filterReceivedInvites(self, getter, added, changed, deleted):
        for clientID in added:
            invite = getter(clientID)
            if invite is None:
                continue
            if not self.__isInviteValid(invite):
                continue
            self.__received[invite.creatorDBID] = invite.clientID
            yield (invite.creatorDBID, _STATUS.RECEIVED_FROM, _STATUS.RECEIVED_INACTIVE)

        for clientID in changed:
            invite = getter(clientID)
            if invite is None:
                continue
            if self.__isInviteValid(invite):
                yield (invite.creatorDBID, _STATUS.RECEIVED_FROM, _STATUS.RECEIVED_INACTIVE)
            yield (invite.creatorDBID, _STATUS.RECEIVED_INACTIVE, _STATUS.NONE)

        inverted = dict(zip(self.__received.values(), self.__received.keys()))
        for clientID in deleted:
            if clientID not in inverted:
                continue
            accountDBID = inverted[clientID]
            if self.__received.pop(accountDBID, None) is not None:
                yield (accountDBID, _STATUS.NONE, _STATUS.RECEIVED_FROM | _STATUS.RECEIVED_INACTIVE)

        return

    def filterSentInvites(self, getter, added, changed, deleted):
        for clientID in added:
            invite = getter(clientID)
            if invite is None:
                continue
            if not self.__isInviteValid(invite):
                continue
            self.__sent[invite.receiverDBID] = invite.clientID
            yield (invite.receiverDBID, _STATUS.SENT_TO, _STATUS.SENT_INACTIVE)

        for clientID in changed:
            invite = getter(clientID)
            if invite is None:
                continue
            if self.__isInviteValid(invite):
                yield (invite.receiverDBID, _STATUS.SENT_TO, _STATUS.SENT_INACTIVE)
            yield (invite.receiverDBID, _STATUS.SENT_INACTIVE, _STATUS.NONE)

        inverted = dict(zip(self.__sent.values(), self.__sent.keys()))
        for clientID in deleted:
            if clientID not in inverted:
                continue
            accountDBID = inverted[clientID]
            if self.__sent.pop(accountDBID, None) is not None:
                yield (accountDBID, _STATUS.NONE, _STATUS.SENT_TO | _STATUS.SENT_INACTIVE)

        return

    def __isInviteValid(self, invite):
        if invite.type not in {INVITATION_TYPE.SQUAD, INVITATION_TYPE.EPIC, INVITATION_TYPE.EVENT}:
            return False
        if not invite.isSameBattle(self.__arenaUniqueID):
            return False
        return False if not invite.isActive() else True


class _SquadInvitationsHandler(ISquadInvitationsHandler):
    __slots__ = ('__sessionProvider',)

    def __init__(self, setup):
        super(_SquadInvitationsHandler, self).__init__()
        self.__sessionProvider = setup.sessionProvider

    @prbInvitesProperty
    def prbInvites(self):
        return None

    def clear(self):
        self.__sessionProvider = None
        return

    def send(self, playerID):
        self.__onSendInviteToSquad(playerID)

    def accept(self, playerID):
        inviteID = self.__getInviteID(playerID, True, True)
        if inviteID is not None:
            self.prbInvites.acceptInvite(inviteID)
        return

    def reject(self, playerID):
        inviteID = self.__getInviteID(playerID, True, True)
        if inviteID is not None:
            self.prbInvites.declineInvite(inviteID)
        return

    @process
    def __onSendInviteToSquad(self, playerID):
        yield self.__sessionProvider.sendRequest(SendInvitesCtx(databaseIDs=(playerID,)))

    def __getInviteID(self, playerID, isCreator, incomingInvites):
        invites = self.prbInvites.getInvites(incoming=incomingInvites, onlyActive=True)
        if isCreator:

            def getter(item):
                return item.creatorDBID

        else:

            def getter(item):
                return item.receiverDBID

        for invite in invites:
            if invite.type in {INVITATION_TYPE.SQUAD, INVITATION_TYPE.EPIC, INVITATION_TYPE.EVENT} and getter(invite) == playerID:
                return invite.clientID

        return None


class _SquadInvitationsRecorder(_SquadInvitationsHandler):
    __slots__ = ('__idGen',)

    def __init__(self, setup):
        super(_SquadInvitationsRecorder, self).__init__(setup)
        self.__idGen = SequenceIDGenerator()

    def send(self, playerID):
        BattleReplay.g_replayCtrl.serializeCallbackData(_SEND_ACTION_NAME, (self.__idGen.next(), playerID))
        super(_SquadInvitationsRecorder, self).send(playerID)

    def accept(self, playerID):
        BattleReplay.g_replayCtrl.serializeCallbackData(_ACCEPT_ACTION_NAME, (self.__idGen.next(), playerID))
        super(_SquadInvitationsRecorder, self).accept(playerID)

    def reject(self, playerID):
        BattleReplay.g_replayCtrl.serializeCallbackData(_REJECT_ACTION_NAME, (self.__idGen.next(), playerID))
        super(_SquadInvitationsRecorder, self).reject(playerID)


class _SquadInvitationsPlayer(_SquadInvitationsHandler):
    __slots__ = ()

    def __init__(self, setup):
        super(_SquadInvitationsPlayer, self).__init__(setup)
        setCallback = BattleReplay.g_replayCtrl.setDataCallback
        for action, method in [(_SEND_ACTION_NAME, self.__onSend), (_ACCEPT_ACTION_NAME, self.__onAccept), (_REJECT_ACTION_NAME, self.__onReject)]:
            setCallback(action, method)

    def clear(self):
        delCallback = BattleReplay.g_replayCtrl.delDataCallback
        for eventName, method in [(_SEND_ACTION_NAME, self.__onSend), (_ACCEPT_ACTION_NAME, self.__onAccept), (_REJECT_ACTION_NAME, self.__onReject)]:
            delCallback(eventName, method)

        super(_SquadInvitationsPlayer, self).clear()

    def __onSend(self, _, playerID):
        self.send(playerID)

    def __onAccept(self, _, playerID):
        self.accept(playerID)

    def __onReject(self, _, playerID):
        self.reject(playerID)


def createInvitationsHandler(setup):
    if setup.isReplayPlaying:
        handler = _SquadInvitationsPlayer(setup)
    elif setup.isReplayRecording:
        handler = _SquadInvitationsRecorder(setup)
    else:
        handler = _SquadInvitationsHandler(setup)
    return handler
